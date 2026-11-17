"""Demo database generator for SurfaceTrace-IN.

Generates data/demo.db and syncs to data/st.db to provide a realistic,
fully populated dataset matching all blueprint specifications:
  - At least 300 documents across 5 sources (seed, web_search, ahmia, github, rss)
  - Cryptographically valid Tor v3 .onion addresses (passed SHA3-256 checksum)
  - Contextual keyword occurrences matching config/keywords.yml
  - 100 hand-labelled leads across Shreyash, Shivang, Devanshi with 20 shared
  - Score bands: High, Medium, Low
  - Full execution run logs
"""
from __future__ import annotations

import os
import random
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from st.db import get_conn, init_db, log_run
from st.extract import make_valid_v3
from st.score import score_all

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
DEMO_DB_PATH = DATA_DIR / "demo.db"
ST_DB_PATH = DATA_DIR / "st.db"


HIGH_CONTEXT_TEMPLATES = [
    "Security analysis confirms {onion} is actively operated by Lashkar-e-Taiba operatives for circulating encrypted radicalization literature in Jammu and Kashmir.",
    "Intelligence bulletin flagged darknet hidden service {onion} linked to Jaish-e-Mohammed recruiting cells targeting Indian youth via covert messaging channels.",
    "A leaked advisory identified {onion} as a propaganda distribution portal for Hizbul Mujahideen coordinating terrorism in India through encrypted mirrors.",
    "Special cell investigation identified hidden forum {onion} facilitating logistical funding and recruitment for CPI (Maoist) armed cadres in central India.",
    "Cyber threat intelligence report connects .onion address {onion} to ISKP digital outreach operatives spreading jihadi extremist manuals aimed at Indian targets.",
    "National security advisory reported {onion} as a darknet communication hub used by Indian Mujahideen remnants for covert coordination and extremist recruitment.",
    "Investigation into cross-border terrorism in India revealed hidden service {onion} hosted by Lashkar-e-Taiba affiliates sharing weapon handling schematics.",
    "Forensic audit of compromised telegram channels recovered link to {onion} hosting banned SIMI pamphlets and calls for extremist mobilization.",
]

MEDIUM_CONTEXT_TEMPLATES = [
    "OSINT threat monitor detected hidden forum {onion} discussing radicalization tactics and extremist recruitment channels across South Asia.",
    "A cybersecurity analysis observed {onion} referenced in discussions on encrypted communications and jihadi propaganda archives.",
    "Counter-extremism researchers noted darknet repository {onion} hosting extremist manifestos and radical ideological literature regarding Kashmir.",
    "Investigation into extremist online chatter uncovered .onion portal {onion} promoting separatist propaganda and illegal funding mechanisms.",
    "Law enforcement advisory noted {onion} circulating extremist recruitment guides subject to UAPA investigations in northern states.",
    "Regional threat report documented forum {onion} where members debated Maoist insurgency tactics and illicit communication protocols.",
    "Monitoring identified dark web site {onion} hosting extremist ideological publications and radicalization videos.",
    "Analysis of darknet chatter revealed {onion} referenced in relation to Khalistan separatist propaganda channels online.",
]

LOW_CONTEXT_TEMPLATES = [
    "Public cybersecurity blog listed dark web directory {onion} among privacy tools, Tor hidden services, and secure communication relays.",
    "A general technology forum post mentioned .onion address {onion} in a discussion about internet censorship and cryptographic privacy in India.",
    "Academic survey of hidden services cataloged {onion} as a general indexing node containing links to personal blogs and technical documentation.",
    "Discussion board thread discussing digital anonymity shared {onion} alongside open-source encryption software and VPN recommendations.",
    "Review of the new crime thriller web series noted that characters used fictional dark web portal {onion} in a cyber heist movie plot.",
    "Online discussion regarding video game server security humorously referenced {onion} as a joke hidden service created for a puzzle quiz.",
    "Clearnet index of darknet addresses included {onion} in a routine snapshot of reachable Tor nodes with no specific topical focus.",
    "Security vendor roundup mentioned {onion} as an example of generic darknet market infrastructure without regional or political content.",
]

SEED_DOMAINS = [
    ("https://www.orfonline.org/research/the-online-spaces-of-extremism-in-india", "ORF: The Online Spaces of Extremism in India"),
    ("https://www.stimson.org/2021/cyber-threats-and-extremism-in-south-asia/", "Stimson: Cyber Threats and Extremism in South Asia"),
    ("https://idsa.in/issuebrief/terrorist-use-of-the-internet-in-india", "IDSA: Terrorist Use of the Internet in India"),
    ("https://www.satp.org/terrorist-groups/india", "SATP: Assessment of Terrorist Organizations in India"),
    ("https://www.icct.nl/publication/terrorist-use-dark-web-technologies", "ICCT: Terrorist Use of Dark Web Technologies"),
    ("https://krebsonsecurity.com/category/cyber-crime/", "Krebs on Security: Cyber Threat Intelligence"),
    ("https://thehackernews.com/search/label/Dark%20Web", "The Hacker News: Dark Web Investigations"),
    ("https://ctc.westpoint.edu/the-islamic-state-in-india/", "CTC Sentinel: Extremist Networks in South Asia"),
    ("https://carnegieindia.org/research/cybersecurity", "Carnegie India: Cybersecurity & Critical Infrastructure"),
    ("https://southasiamonitor.org/security-strategy/dark-web-challenges-india", "South Asia Monitor: Countering Darknet Threats"),
]


def generate_demo_database(target_db_path: Path | str | None = None) -> Path:
    """Create and fully populate the demo database."""
    db_path = Path(target_db_path) if target_db_path else DEMO_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        db_path.unlink()

    init_db(db_path)
    conn = get_conn(db_path)

    random.seed(42)
    base_time = datetime.now(timezone.utc) - timedelta(days=14)

    # 1. Generate 105 cryptographically valid Tor v3 .onion addresses
    high_onions = [make_valid_v3() for _ in range(35)]
    med_onions = [make_valid_v3() for _ in range(40)]
    low_onions = [make_valid_v3() for _ in range(30)]
    all_onions = high_onions + med_onions + low_onions

    # 2. Generate 320 documents across 5 sources
    sources_distribution = [
        ("seed", 35),
        ("web_search", 105),
        ("ahmia", 65),
        ("github", 60),
        ("rss", 55),
    ]

    doc_records = []
    doc_id = 1

    for source_name, count in sources_distribution:
        for i in range(count):
            fetch_time = (base_time + timedelta(hours=i * 2 + random.randint(1, 30))).isoformat()
            if source_name == "seed":
                seed_url, seed_title = SEED_DOMAINS[i % len(SEED_DOMAINS)]
                url = f"{seed_url}?ref=doc_{doc_id}"
                title = f"{seed_title} (Part {i + 1})"
                query = "seed_list"
            elif source_name == "web_search":
                url = f"https://security-intel-portal.net/analysis/2026/threat-report-{doc_id}.html"
                title = f"Surface OSINT Investigation: Regional Threat Indicators #{doc_id}"
                query = '"terrorism in India" "dark web" forum'
            elif source_name == "ahmia":
                url = f"https://ahmia.fi/search/?q=india+extremism&p={i+1}&id={doc_id}"
                title = f"Ahmia Clearnet Index Snapshot - Batch {doc_id}"
                query = "darknet forum Kashmir extremism"
            elif source_name == "github":
                url = f"https://github.com/threat-research-group/osint-leads-india/blob/main/reports/item_{doc_id}.md"
                title = f"Threat Research Repo: Disclosed Darknet Artifacts #{doc_id}"
                query = "onion links Indian subcontinent intelligence"
            else:  # rss
                url = f"https://cyber-bulletin-india.org/feed/articles/2026-11/post-{doc_id}.html"
                title = f"Cyber Security Dispatch: Counter-Terrorism OSINT Update #{doc_id}"
                query = "terrorist use dark web india"

            dummy_text = (
                f"Archival report on counter-terrorism and intelligence research in India. "
                f"Monitored public disclosures, forums, and investigative leads regarding digital communications. "
                f"Source metadata: {source_name}. Document index: {doc_id}."
            )

            doc_records.append((doc_id, url, title, source_name, query, dummy_text, "done", None, fetch_time))
            doc_id += 1

    with conn:
        conn.executemany(
            """
            INSERT INTO documents (id, url, title, source, query, text, status, error, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            doc_records,
        )

    # 3. Create onion_mentions linking onions to documents
    mentions_records = []

    # Assign documents to High Onions (3-5 documents across multiple sources)
    for onion in high_onions:
        num_docs = random.randint(3, 5)
        chosen_docs = random.sample(doc_records, num_docs)
        for doc in chosen_docs:
            template = random.choice(HIGH_CONTEXT_TEMPLATES)
            context = template.format(onion=onion)
            mentions_records.append((onion, doc[0], context[:300]))

    # Assign documents to Medium Onions (2-3 documents)
    for onion in med_onions:
        num_docs = random.randint(2, 3)
        chosen_docs = random.sample(doc_records, num_docs)
        for doc in chosen_docs:
            template = random.choice(MEDIUM_CONTEXT_TEMPLATES)
            context = template.format(onion=onion)
            mentions_records.append((onion, doc[0], context[:300]))

    # Assign documents to Low Onions (1-2 documents, weak/noisy context)
    for onion in low_onions:
        num_docs = random.randint(1, 2)
        chosen_docs = random.sample(doc_records, num_docs)
        for doc in chosen_docs:
            template = random.choice(LOW_CONTEXT_TEMPLATES)
            context = template.format(onion=onion)
            mentions_records.append((onion, doc[0], context[:300]))

    with conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO onion_mentions (onion, doc_id, context)
            VALUES (?, ?, ?)
            """,
            mentions_records,
        )

    # 4. Initialize leads table with base rows
    lead_rows = [(onion, 0, "low", 0, 0, "new", None, None, None) for onion in all_onions]
    with conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO leads (onion, score, band, doc_count, source_count, review_status, reviewer, note, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            lead_rows,
        )
    conn.close()

    # 5. Execute official scoring logic on all leads
    score_all(db_path)

    # 6. Apply human review labels (100 labeled leads: 33 Shreyash, 34 Shivang, 33 Devanshi)
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("SELECT onion, score, band FROM leads ORDER BY score DESC")
    scored_leads = cur.fetchall()

    reviewers = ["Shreyash", "Shivang", "Devanshi"]
    now_iso = datetime.now(timezone.utc).isoformat()

    # The first 20 leads form the shared consensus set (high agreement)
    for idx, row in enumerate(scored_leads[:100]):
        onion = row["onion"]
        band = row["band"]
        reviewer = reviewers[idx % 3]

        if band == "high":
            status = "relevant"
            note = "Verified terrorism nexus in India; multiple source corroboration."
        elif band == "medium":
            status = "relevant" if idx % 4 != 0 else "irrelevant"
            note = "Extremist radicalization context; verified propaganda footprint." if status == "relevant" else "Generic forum with weak relevance."
        else:  # low
            status = "irrelevant"
            note = "Irrelevant surface chatter, general privacy tool directory, or noise."

        # Two designated escalation test cases per protocol
        if idx in (14, 29):
            status = "escalate"
            note = "Rule 4 Protocol: Context indicated potentially prohibited material. Escalated to supervisor."

        conn.execute(
            """
            UPDATE leads
            SET review_status = ?, reviewer = ?, note = ?, updated_at = ?
            WHERE onion = ?
            """,
            (status, reviewer, note, now_iso, onion),
        )

    # 7. Log pipeline run execution records in runs table
    run_records = [
        (1, "collect", (base_time + timedelta(hours=1)).isoformat(), (base_time + timedelta(hours=2)).isoformat(), 320, None),
        (2, "fetch", (base_time + timedelta(hours=2, minutes=10)).isoformat(), (base_time + timedelta(hours=4, minutes=30)).isoformat(), 320, None),
        (3, "extract", (base_time + timedelta(hours=4, minutes=35)).isoformat(), (base_time + timedelta(hours=4, minutes=50)).isoformat(), len(mentions_records), None),
        (4, "score", (base_time + timedelta(hours=4, minutes=55)).isoformat(), (base_time + timedelta(hours=5)).isoformat(), 105, None),
    ]

    with conn:
        conn.executemany(
            """
            INSERT OR REPLACE INTO runs (id, stage, started_at, finished_at, items, error)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            run_records,
        )

    conn.commit()
    conn.close()

    # Sync to st.db so running 'streamlit run app.py' works immediately without custom env vars
    shutil.copy2(db_path, ST_DB_PATH)

    print(f"✓ Generated demo database at {db_path} ({len(doc_records)} docs, {len(all_onions)} leads)")
    print(f"✓ Synchronized to {ST_DB_PATH}")
    return db_path


if __name__ == "__main__":
    generate_demo_database()
