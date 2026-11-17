# SurfaceTrace-IN: Pipeline Execution Overview
**What Happens Inside the System When You Run the Pipeline**

---

## 1. Quick Summary of the Pipeline Run

When you execute:
```powershell
python -m st run-all
```
The program triggers a **4-stage automated chain reaction** that queries the public internet, downloads and cleans articles, cryptographically verifies hidden service addresses, and computes threat scores—all before you open the human review dashboard.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE EXECUTION FLOW                           │
└─────────────────────────────────────────────────────────────────────────────┘

 [Terminal: python -m st run-all]
        │
        ▼
 1. SEARCH (st collect) ─────────► Ingests candidate URLs from 5 surface sources
        │                          (Seed, Google/SearXNG, Ahmia, GitHub, RSS)
        ▼
 2. FETCH (st fetch) ────────────► Downloads pages politely (1s delay, robots.txt)
        │                          Strips ads/scripts; extracts clean text (≤20k chars)
        ▼
 3. EXTRACT (st extract) ────────► Normalizes defanged links; runs Tor v3 SHA3-256 math;
        │                          Cuts 300-char context window (±150 chars)
        ▼
 4. SCORE (st score) ────────────► Calculates threat score (0–100) using keywords,
        │                          recurrence, and diversity; assigns High/Med/Low bands
        ▼
 [Dashboard: streamlit run app.py] ──► Human review on localhost:8501 with masked addresses
```

---

## 2. Detailed Step-by-Step Breakdown

---

### Step 1: SEARCH (`st collect`) — Finding Candidate Webpages

The program wakes up and loads two configuration files:
* **`config/queries.txt`:** 40 targeted queries combining darknet wording, regional terms, and banned groups (e.g., `"dark web" "Lashkar-e-Taiba"`, `"terrorism in India" ".onion"`, `"Maoist insurgency" "darknet"`).
* **`config/seed_urls.txt`:** 24 verified academic and think-tank research reports (ORF, MP-IDSA, SATP, West Point CTC).

It contacts **5 distinct surface-web sources**:
1. **Curated Seed Engine (`seed.py`):** Reads the 24 trusted research links stored locally on disk. (Guarantees benchmark data even without an active internet connection).
2. **Web Search API (`web_search.py`):** Dispatches queries to Google Custom Search JSON API / SearXNG to fetch top-ranking news articles and investigative blogs.
3. **Ahmia Clearnet Index (`ahmia.py`):** Queries Ahmia's public clearnet search page (`https://ahmia.fi/search/?q=...`) to identify dark-web directories indexed on the surface web.
4. **GitHub Threat Scanner (`github.py`):** Queries the GitHub REST API (`/search/repositories`) for security researcher repositories containing IOCs and darknet link dumps.
5. **Syndication Monitor (`rss.py`):** Parses live XML feeds from leading cybersecurity publications (*The Hacker News*, *Krebs on Security*, *Dark Reading*) for recent cyber-threat investigations.

> **Database Action (`documents` table):**
> * All discovered links are inserted into the `documents` table in `data/st.db`.
> * Each record gets: `url`, `title`, `source`, `query`, and `status = 'new'`.
> * Duplicate URLs are automatically ignored (`INSERT OR IGNORE`).

---

### Step 2: FETCH (`st fetch`) — Downloading & Sanitizing Page Text

The fetcher asks the database for all records with `status = 'new'`. For every URL:

1. **Safety Blocklist Check:** Checks `config/blocklist.txt`. If the domain is banned, it skips the URL and marks `status = 'blocked'`.
2. **Politeness Check (`robots.txt`):** Reads `domain.com/robots.txt` using Python's `RobotFileParser`. If the website disallows automated crawlers, the tool respects the rule, skips the page, and records `status = 'blocked'`.
3. **Speed Limit (Rate Limiting):** Checks an in-memory stopwatch (`_DOMAIN_LAST_REQUEST`). If the same website was visited less than 1.0 second ago, **it pauses for 1 second** to prevent server overload.
4. **Download & Content Inspection:**
   - Sends an HTTP GET request with a transparent User-Agent: `SurfaceTrace-ClassProject/1.0`.
   - Checks `Content-Type`: **HTML only**. If the URL points to a `.pdf`, video `.mp4`, image `.jpg`, or `.zip` file, **it immediately skips it**.
     * *Why?* To eliminate malware risks, prevent high memory usage, and strictly prevent the accidental acquisition of prohibited media (CSAM/contraband under Section 67B of the IT Act).
5. **Text Cleaning:**
   - Drops all `<script>`, `<style>`, `<nav>`, and `<footer>` elements using `trafilatura` (or `BeautifulSoup4`).
   - Retains only the clean, readable article paragraphs.
6. **Data Minimization:** Truncates the cleaned body text to a maximum of **20,000 characters**.

> **Database Action (`documents` table):**
> * Stores the cleaned text, sets `fetched_at` timestamp, and updates `status = 'fetched'`.
> * If a website is offline, broken, or times out after 20 seconds, it marks `status = 'failed'` with the error message (the pipeline never crashes).

---

### Step 3: EXTRACT (`st extract`) — Finding & Verifying `.onion` Addresses

The extractor queries SQLite for all documents marked as `status = 'fetched'`:

1. **Defanging Normalization:** Automatically fixes obfuscated links typed by forum users or researchers (converts `example[.]onion` or `example(dot)onion` into `example.onion`).
2. **Regex Pattern Matching:** Scans the text for 56-character base32 strings ending in `.onion`:
   ```python
   ONION = re.compile(r"(?<![a-z0-9])([a-z2-7]{56})\.onion(?![a-z0-9])", re.I)
   ```
3. **The Offline Cryptographic Checksum Gate (Zero AI Prompts):**
   - Candidate addresses are not assumed to be real. Tor v3 addresses encode a 32-byte Ed25519 public key, a 2-byte checksum, and a 1-byte version (`03`).
   - The code calculates:
     $$\text{Expected Checksum} = \text{SHA3-256}(b\text{".onion checksum"} \,\|\, \text{Public Key} \,\|\, \text{Version Byte})[0:2]$$
   - If the calculated 2 bytes do not match the address's checksum, **the string is rejected as a fake or typo**.
4. **Context Window Slicing:** For every cryptographically valid address, it grabs **150 characters before** and **150 characters after** the match (a symmetric **300-character context window**).

> **Database Action (`onion_mentions` table):**
> * Inserts `(onion, doc_id, context)` into `onion_mentions`.
> * Updates the source document from `status = 'fetched'` to `status = 'done'`.

---

### Step 4: SCORE (`st score`) — Calculating Threat Levels ($0\text{--}100$)

The scoring engine queries SQLite for all distinct verified `.onion` addresses. For each address, it computes a danger score:

$$\text{Final Score} = \min(50, \text{Context Points}) + \min(25, 8 \times N_{\text{docs}}) + \min(25, 12 \times N_{\text{sources}})$$

1. **Context Points (Up to 50 pts):**
   - Matches keywords from `config/keywords.yml` within the 300-character snippet:
     - **Strong (+10 pts each):** Banned terror groups (*Lashkar-e-Taiba*, *Jaish-e-Mohammed*, *CPI Maoist*, *ISKP*, *SIMI*).
     - **Medium (+5 pts each):** Threat terms (*radicalization*, *recruitment*, *jihadi*, *khalistan*, *uapa*).
     - **Weak (+2 pts each):** Context indicators (*india*, *kashmir*, *dark web*, *forum*).
     - **Negative Penalties (-5 pts each):** Non-threat noise (*movie*, *web series*, *game*, *quiz*, *fiction*).
2. **Document Recurrence (Up to 25 pts):** Awards 8 points per document referencing the address (caps at 4 documents).
3. **Source Diversity (Up to 25 pts):** Awards 12 points per distinct source stream referencing the address (caps at 3 sources).
4. **Priority Band Assignment:**
   - **High Priority ($\ge 60$):** Verified terror group footprint / operational portal.
   - **Medium Priority ($30\text{--}59$):** Suspicious extremist propaganda or recruitment chatter.
   - **Low Priority ($< 30$):** False alarms, entertainment noise, or general privacy directories.

> **Database Action (`leads` table):**
> * Populates or updates `score`, `band`, `doc_count`, and `source_count`.
> * Preserves existing human review statuses and notes.

---

## 3. The End Result: Opening the Analyst Dashboard

Once the automated pipeline completes, the analyst launches the web dashboard:
```powershell
streamlit run app.py
```
This opens `http://localhost:8501` in the browser:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SURFACETRACE-IN ANALYST DASHBOARD UI                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [Page 1: Overview]                                                         │
│  • Metrics: Total Documents (320) | Leads (105) | Reviewed (100)            │
│  • Visualizations: Leads by Score Band | Documents by Source Stream         │
│                                                                             │
│  [Page 2: Leads Catalog]                                                    │
│  • Sortable Table: Address (Masked: abcdefgh...) | Score | Band | Status     │
│  • 1-Click Action: "📥 Export Masked CSV"                                   │
│                                                                             │
│  [Page 3: Lead Detail & Triage]                                             │
│  • Context Snippet: Full 300-character sentence with source attribution     │
│  • Triage Actions: [✅ Relevant]  [❌ Irrelevant]  [🚨 Escalate]             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Summary Table of Pipeline Stages

| Stage | Input | Primary Operations | Output | Database Table |
| :--- | :--- | :--- | :--- | :--- |
| **1. Collect** | `queries.txt`, `seed_urls.txt` | Queries 5 surface sources | Raw webpage URLs | `documents` (`status='new'`) |
| **2. Fetch** | URLs from `documents` | Polite rate limits (1s), robots.txt, HTML cleaning | Clean body text ($\le 20\text{k}$ chars) | `documents` (`status='fetched'`) |
| **3. Extract** | Cleaned article text | Defang normalization, Tor v3 SHA3-256 checksums | Verified onion addresses + 300-char context | `onion_mentions`, `documents` (`status='done'`) |
| **4. Score** | Extracted contexts | Weighted keywords, recurrence, source diversity | Danger score ($0\text{--}100$), High/Med/Low bands | `leads` |
| **5. Review** | Scored `leads` | Streamlit UI, address masking, human triage | Analyst labels (`relevant`, `irrelevant`, `escalate`) | `leads` (updated review fields) |
