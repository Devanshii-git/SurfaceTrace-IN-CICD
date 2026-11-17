"""SurfaceTrace-IN Review Dashboard.

Owned by Devanshi.
Run with: streamlit run app.py
Features 3 pages:
  1. Overview: stats, distributions, charts.
  2. Leads: filterable, sortable list with search.
  3. Lead Detail: score breakdown, contexts, review buttons (Relevant, Irrelevant, Escalate).
Addresses are masked by default (first 8 chars + ...) with a toggle for team review.
"""
from __future__ import annotations

import io
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="SurfaceTrace-IN Dashboard",
    page_icon="🛡️",
    layout="wide",
)

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "data" / "st.db"


def get_db_path() -> Path:
    custom = os.environ.get("DATABASE_PATH")
    if custom:
        return Path(custom)
    data_dir = os.environ.get("DATA_DIR")
    if data_dir:
        return Path(data_dir) / "st.db"
    return DEFAULT_DB_PATH


def get_connection() -> sqlite3.Connection:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn


def mask_onion(address: str) -> str:
    if not address:
        return "..."
    addr = address.strip()
    return f"{addr[:8]}..."


def format_address(address: str, show_full: bool) -> str:
    return address if show_full else mask_onion(address)


# --- Sidebar ---
st.sidebar.title("SurfaceTrace-IN")
st.sidebar.caption("Surface-Web OSINT Discovery for Terrorism-related .onion Footprints")

reviewer_name = st.sidebar.text_input("Reviewer Name", value="Analyst")
show_full_onion = st.sidebar.toggle("Show Full .onion Addresses (Team Only)", value=False)

page = st.sidebar.radio(
    "Navigation",
    ["1. Overview", "2. Leads", "3. Lead Detail"],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "⚠️ **Hard Rule:** This pipeline operates exclusively on surface-web data. "
    "Never connect to or visit any `.onion` service."
)

conn = get_connection()


# --- Page 1: Overview ---
if page == "1. Overview":
    st.header("📊 Pipeline Overview")

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM documents")
    total_docs = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM onion_mentions")
    total_mentions = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM leads")
    total_leads = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM leads WHERE review_status IN ('relevant', 'irrelevant', 'escalate')")
    reviewed_leads = cur.fetchone()[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Documents", total_docs)
    c2.metric("Onion Mentions", total_mentions)
    c3.metric("Discovered Leads", total_leads)
    c4.metric("Reviewed Leads", f"{reviewed_leads} / {total_leads}")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Leads by Score Band")
        cur.execute("SELECT band, COUNT(*) as cnt FROM leads GROUP BY band ORDER BY cnt DESC")
        band_data = cur.fetchall()
        if band_data:
            df_band = pd.DataFrame(band_data, columns=["Band", "Count"])
            st.bar_chart(df_band.set_index("Band"))
        else:
            st.info("No leads scored yet.")

    with col2:
        st.subheader("Documents by Source")
        cur.execute("SELECT source, COUNT(*) as cnt FROM documents GROUP BY source ORDER BY cnt DESC")
        source_data = cur.fetchall()
        if source_data:
            df_src = pd.DataFrame(source_data, columns=["Source", "Count"])
            st.bar_chart(df_src.set_index("Source"))
        else:
            st.info("No documents collected yet.")

    st.subheader("Review Progress by Status")
    cur.execute("SELECT review_status, COUNT(*) as cnt FROM leads GROUP BY review_status")
    status_data = cur.fetchall()
    if status_data:
        df_status = pd.DataFrame(status_data, columns=["Review Status", "Count"])
        st.dataframe(df_status, use_container_width=True)


# --- Page 2: Leads ---
elif page == "2. Leads":
    st.header("📋 Discovered Leads Catalog")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        band_disp = st.selectbox("Filter by Band", ["All", "High", "Medium", "Low"], key="p2_band")
        band_filter = band_disp.lower()
    with col_f2:
        status_disp = st.selectbox("Filter by Review Status", ["All", "New", "Relevant", "Irrelevant", "Escalate"], key="p2_status")
        status_filter = status_disp.lower()
    with col_f3:
        search_query = st.text_input("Search (Address / Note)", "", key="p2_search")

    query = "SELECT onion, score, band, doc_count, source_count, review_status, reviewer, note, updated_at FROM leads WHERE 1=1"
    params = []

    if band_filter != "all":
        query += " AND band = ?"
        params.append(band_filter)
    if status_filter != "all":
        query += " AND review_status = ?"
        params.append(status_filter)
    if search_query:
        query += " AND (onion LIKE ? OR note LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    query += " ORDER BY score DESC, doc_count DESC"

    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()

    st.caption(f"Displaying **{len(rows)}** matching leads (ordered by Score descending)")

    if rows:
        data = []
        for r in rows:
            data.append(
                {
                    "Onion Address": format_address(r["onion"], show_full_onion),
                    "Raw Onion": r["onion"],
                    "Score": r["score"],
                    "Band": r["band"].upper(),
                    "Documents": r["doc_count"],
                    "Sources": r["source_count"],
                    "Review Status": r["review_status"].upper(),
                    "Reviewer": r["reviewer"] or "",
                    "Note": r["note"] or "",
                    "Updated": r["updated_at"] or "",
                }
            )
        df_leads = pd.DataFrame(data)
        # Display table without raw onion
        st.dataframe(df_leads.drop(columns=["Raw Onion"]), use_container_width=True)

        # Export Masked CSV button
        csv_buffer = io.StringIO()
        export_df = df_leads.copy()
        export_df["Onion Address"] = export_df["Raw Onion"].apply(mask_onion)
        export_df.drop(columns=["Raw Onion"]).to_csv(csv_buffer, index=False)

        st.download_button(
            label="📥 Export Masked CSV",
            data=csv_buffer.getvalue(),
            file_name=f"surfacetrace_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )
    else:
        st.info("No leads found matching the selected filters.")


# --- Page 3: Lead Detail ---
elif page == "3. Lead Detail":
    st.header("🔎 Lead Detail & Annotation")

    # Display persistent alert if a lead was just reviewed
    if "review_alert" in st.session_state:
        st.success(st.session_state.pop("review_alert"))

    cur = conn.cursor()

    # Quick triage filter so analysts can directly view only new leads
    filter_choice = st.radio(
        "Triage Filter",
        ["All Leads", "Unreviewed (new) Only", "High Band Only"],
        horizontal=True,
        key="lead_triage_filter",
    )

    if filter_choice == "Unreviewed (new) Only":
        cur.execute("SELECT onion, score, band, review_status FROM leads WHERE review_status = 'new' ORDER BY score DESC")
    elif filter_choice == "High Band Only":
        cur.execute("SELECT onion, score, band, review_status FROM leads WHERE band = 'high' ORDER BY score DESC")
    else:
        cur.execute("SELECT onion, score, band, review_status FROM leads ORDER BY score DESC")

    all_leads = cur.fetchall()

    if not all_leads:
        st.info(f"No leads matching triage filter '{filter_choice}'.")
    else:
        lead_options = [r["onion"] for r in all_leads]

        # Keep selected lead across re-renders
        prev_onion = st.session_state.get("current_lead_onion")
        default_index = 0
        if prev_onion and prev_onion in lead_options:
            default_index = lead_options.index(prev_onion)

        selected_idx = st.selectbox(
            "Select Lead to Review",
            range(len(lead_options)),
            index=default_index,
            format_func=lambda idx: f"{format_address(all_leads[idx]['onion'], show_full_onion)} | Score: {all_leads[idx]['score']} | [{all_leads[idx]['review_status'].upper()}]",
            key="lead_detail_selector",
        )

        selected_onion = lead_options[selected_idx]
        st.session_state["current_lead_onion"] = selected_onion

        cur.execute("SELECT * FROM leads WHERE onion = ?", (selected_onion,))
        lead = cur.fetchone()

        st.subheader(f"Address: `{format_address(selected_onion, show_full_onion)}`")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Score", lead["score"])
        col_m2.metric("Band", lead["band"].upper())
        col_m3.metric("Doc Count", lead["doc_count"])
        col_m4.metric("Source Count", lead["source_count"])

        st.markdown("### Context Mentions & Source Pages")
        cur.execute(
            """
            SELECT om.context, d.url, d.title, d.source
            FROM onion_mentions om
            JOIN documents d ON om.doc_id = d.id
            WHERE om.onion = ?
            """,
            (selected_onion,),
        )
        mentions = cur.fetchall()

        if mentions:
            for i, m in enumerate(mentions, 1):
                with st.expander(f"Mention #{i} — Source: {m['source']} | Page: {m['title'] or m['url']}"):
                    st.markdown(f"**Source URL:** `{m['url']}`")
                    st.markdown("**Context Snippet (max 300 chars):**")
                    st.code(m["context"], language="text")
        else:
            st.info("No mentions found for this address.")

        st.markdown("---")
        st.subheader("Human Review Annotation")

        status_badge_map = {
            "relevant": "🟢 **RELEVANT**",
            "irrelevant": "🔴 **IRRELEVANT**",
            "escalate": "🚨 **ESCALATE (RULE 4 STOP)**",
            "new": "🟡 **NEW (UNREVIEWED)**",
        }
        badge = status_badge_map.get(lead["review_status"], lead["review_status"].upper())
        st.markdown(f"Current Review Status: {badge}")
        if lead["reviewer"]:
            st.caption(f"Last recorded reviewer: `{lead['reviewer']}` | Updated at: `{lead['updated_at']}`")

        note_key = f"note_area_{selected_onion}"
        note_input = st.text_area(
            "Reviewer Note",
            value=lead["note"] or "",
            placeholder="Enter context observations or investigative notes...",
            key=note_key,
        )

        btn_c1, btn_c2, btn_c3 = st.columns(3)

        def save_review(new_status: str):
            now_iso = datetime.now(timezone.utc).isoformat()
            typed_note = st.session_state.get(note_key, lead["note"] or "")
            with conn:
                conn.execute(
                    """
                    UPDATE leads
                    SET review_status = ?, reviewer = ?, note = ?, updated_at = ?
                    WHERE onion = ?
                    """,
                    (new_status, reviewer_name, typed_note, now_iso, selected_onion),
                )
            st.session_state["current_lead_onion"] = selected_onion
            st.session_state["review_alert"] = f"✅ Lead `{format_address(selected_onion, show_full_onion)}` updated to **{new_status.upper()}** by {reviewer_name}!"
            st.rerun()

        with btn_c1:
            if st.button("✅ Relevant", use_container_width=True, key=f"btn_rel_{selected_onion}"):
                save_review("relevant")
        with btn_c2:
            if st.button("❌ Irrelevant", use_container_width=True, key=f"btn_irrel_{selected_onion}"):
                save_review("irrelevant")
        with btn_c3:
            if st.button("🚨 Escalate", use_container_width=True, key=f"btn_esc_{selected_onion}"):
                save_review("escalate")

conn.close()

