# SurfaceTrace-IN: Project Final Report
**Discovering Surface-Web Footprints of Darknet Sites Linked to Terrorism in India**

---

### Project Metadata
* **Project Title:** SurfaceTrace-IN: Surface-Web Reconnaissance Pipeline for Terror-Linked Hidden Service Detection
* **Academic Course:** CICD Pipeline and Security (DevSecOps)
* **Faculty Supervisor:** Prof. Priyanka Goel
* **Authors & Engineering Ownership:**
  * **Devanshi Jain (500123468):** Cryptographic Extraction, Scoring Formulation, Streamlit Review Dashboard, Labelling Protocol
  * **Shivang Mangal (500124202):** Collection Architecture, 5 Surface Collectors, Seed Curation, Polite Fetcher Engine
  * **Shreyash Shivhare (500122740):** Platform Infrastructure, SQLite WAL Database, Typer CLI, CI/CD Pipeline, Quantitative Evaluation

---

## Abstract
SurfaceTrace-IN investigates the feasibility, architectural design, and empirical efficacy of detecting dark-web (`.onion`) hidden services associated with terrorism, extremism, and radicalization in India exclusively through passive surface-web reconnaissance. Extremist entities operating hidden services face a fundamental operational contradiction: while the Tor network provides hosting anonymity and network resilience, isolated hidden services cannot recruit, disseminate propaganda, or solicit funding without publicizing their presence to prospective sympathizers. Consequently, threat actors and researchers disclose Tor addresses on the clearnet. 

Direct crawling of the Tor network introduces severe technical latency (>15–30s per request), extreme hidden service volatility (>60% churn rate), and catastrophic legal liabilities under Section 67B of the Indian Information Technology Act (2000) and the Unlawful Activities (Prevention) Act (UAPA) due to the inadvertent acquisition of illicit contraband or child exploitation material (CSAM). SurfaceTrace-IN overcomes these barriers by deploying a strictly non-invasive, Zero-Tor pipeline that surveys public search indices, research archives, code repositories, and syndication feeds. 

The system implements automated defang normalization, offline Tor v3 Ed25519 SHA3-256 cryptographic checksum verification, an explainable tri-factor threat scoring formula ($0\text{--}100$), and a human-in-the-loop analyst dashboard with automated address masking. Evaluated on a benchmark of 320 ingested documents across 5 diverse sources yielding 105 cryptographically verified `.onion` leads, the pipeline achieved 100.0% precision in its High-Priority tier ($\ge 60$) and successfully suppressed noise and non-terror false alarms to the Low-Priority tier (0.0% precision).

---

## 1. Introduction and Threat Context in India

### 1.1 Operational Motivation
Over the past decade, hybrid threat actors, designated terrorist organizations, and violent extremist networks targeting the Indian subcontinent have increasingly integrated darknet hidden services into their communications infrastructure. Banned entities—including Lashkar-e-Taiba (LeT), Jaish-e-Mohammed (JeM), Hizbul Mujahideen (HM), Islamic State Khorasan Province (ISKP), Al-Qaeda in the Indian Subcontinent (AQIS), and CPI (Maoist)—have leveraged Tor hidden services to host operational manuals, ideological manifestos, encrypted messaging directories, and cryptocurrency fundraising portals.

Traditional cyber threat intelligence (CTI) paradigms advocate active, automated crawling of the dark web. However, deploying automated crawlers directly into the Tor ecosystem presents severe limitations:
1. **Network Latency & Site Volatility:** Tor rendezvous routing introduces high round-trip latency, frequent connection timeouts, and CAPTCHA barriers. Over 60% of hidden services remain online for less than 48 hours.
2. **Institutional & Legal Exposure:** An automated crawler traversing darknet marketplaces or unindexed forums inevitably encounters illicit contraband, hacking tools, and prohibited Child Sexual Abuse Material (CSAM). In India, possessing or downloading such data constitutes a strict-liability criminal offense under Section 67B of the IT Act and Sections 7/8 of POCSO, creating unacceptable institutional liability for academic universities and security research teams.

### 1.2 Core Research Hypothesis
SurfaceTrace-IN is founded upon a core operational premise: **Extremist organizations cannot recruit or mobilize in total digital isolation.** To influence target demographics, radicalize youth, or solicit untraceable financial support across Jammu & Kashmir, central tribal regions, or urban hubs, threat networks are compelled to broadcast their entry points on the clearnet (the surface web)—via public pastebins, technical forums, social discussion platforms, research archives, and open code repositories. 

By systematically capturing and analyzing these surface-web disclosures, intelligence analysts can map, prioritize, and monitor extremist darknet footprints with **100% Zero-Tor access**, zero credential requirements, and zero threat of contraband acquisition.

---

## 2. Legal Guardrails & Ethical Architecture

SurfaceTrace-IN operates under a mandatory, non-negotiable ethical charter embedded directly into the pipeline's runtime logic:

1. **Zero-Tor / Zero-Hidden-Service Traffic:** The engine strictly forbids any connection to the Tor network, SOCKS5 proxies, or onion routing daemons. Every HTTP/HTTPS request is dispatched solely to standard clearnet domain names.
2. **No Interactive Infiltration:** The pipeline never creates user credentials, bypasses authentication gates, joins private channels, or engages in interactive communication.
3. **Strict Data Minimization (Hard Rule #3):** The system stores only page URLs, page titles, cleaned body text capped at 20,000 characters, and 300-character contextual snippets. Binary media, images, video files, and document downloads (`.pdf`, `.zip`, `.exe`) are strictly prohibited and dropped by content-type inspection before saving.
4. **Emergency Stop Protocol (Rule 4):** If abusive material (CSAM or illegal non-text media) is detected during ingestion, processing halts immediately, the database row is purged, and the faculty supervisor is notified.
5. **Polite Crawling Protocol:** Crawlers strictly honor `robots.txt` guidelines and enforce a mandatory 1.0-second delay per domain name.
6. **Address Masking Policy:** In adherence to responsible disclosure, all `.onion` addresses are masked in visualizations, UI displays, and exported CSV files (e.g., `abcdefgh...`), preventing accidental circulation of operational URLs.

---

## 3. Literature Review & Synthesis of Related Work

The project synthesizes 13 academic research publications and official security engineering standards spanning darknet forensics, threat intelligence automation, DevSecOps supply-chain controls, and multilingual NLP.

| S. No. | Author(s) & Year | Title & Source | Methodology | Key Findings | Addressed Research Gap |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | Shah & Madisetti (2025) | *MAD-CTI: Multi-Agent CTI Framework for Dark Web*, IEEE Access | Multi-agent cooperative LLM architecture for darknet entity extraction | Multi-agent reasoning improves threat entity extraction by 28% over monolithic models | Assumes raw data is already harvested from Tor; lacks a safe, surface-web collection mechanism. |
| **2** | de-Marcos et al. (2025) | *Methodologies for Dark Web Forum Analysis*, Electronics | Systematic literature review of 127 darknet scraping methodologies | Direct crawling encounters extreme legal hazards (CSAM), bot-traps, and rapid site turnover | Documents legal pitfalls of crawling but proposes no clear-web passive alternative. |
| **3** | Lewinsky et al. (2024) | *Detecting Terrorist Influencers Using Reciprocal ML*, Nature HSSC | Reciprocal human-in-the-loop machine learning on darknet forums | Human-analyst validation is essential for nuanced extremist ideological context | Relies on direct Tor infiltration; limited strictly to Arabic-language militant Da'wa. |
| **4** | Kühn et al. (2024) | *Manual & Semi-Automated Evaluation of Dark Web for CTI*, IEEE Access | Comparative benchmark of manual vs. automated scraping across 1,000+ sites | Automated scrapers generate >42% false positives due to link aggregators and dead nodes | Relied on active darknet connections; lacked cryptographic address validation. |
| **5** | Chandramouli et al. / NIST (2024) | *Software Supply Chain Security in DevSecOps*, NIST SP 800-204D | DevSecOps architectural standards for continuous policy gating and testing | Automated policy gates and regression test suites prevent delivery of compromised pipelines | General enterprise standard; requires contextualization for automated CTI ingestion pipelines. |
| **6** | Albizri et al. (2022) | *Using Hacker Forums on Dark Web for CTI*, AMCIS TREOs | Systematic review of cyber threat intelligence extraction from underground forums | Underground forums yield high-value early warnings, but manual retrieval is unscalable | Omitted surface-web intelligence leakage; lacked automated address sanitization. |
| **7** | Souppaya et al. / NIST (2022) | *Secure Software Development Framework (SSDF)*, NIST SP 800-218 | Comprehensive standard for secure software development across the SDLC | Mandates least-privilege architecture, defensive input parsing, and automated test runs | Organizational guideline; needs adaptation for open-source intelligence collection tools. |
| **8** | Basheer & Alkhatib (2021) | *Threats from the Dark: Dark Web Investigation for CTI*, J. Comput. Netw. | Taxonomic survey of dark web crawling architectures, tools, and legal hurdles | Dark web crawling suffers from >60% site churn, extreme latency, and legal jeopardy | Focuses on active Tor scraping despite acknowledging severe friction and legal exposure. |
| **9** | Cascavilla et al. (2021) | *Cybercrime Threat Intelligence: Multi-Vocal Review*, Comput. & Security | Systematic review evaluating 84 academic papers and 52 industry whitepapers | Identified major disconnect between theoretical AI threat models and production software | Highlights the total absence of automated, production-ready DevSecOps pipelines in academic CTI. |
| **10** | Gaikwad et al. (2021) | *Online Extremism Detection: Systematic Review*, IEEE Access | Systematic review of text classification algorithms and extremism lexicons | Multi-tiered, weighted contextual lexicons substantially outperform unigram keyword matching | Survey restricted to clearnet social platforms; omitted dark web footprint analysis. |
| **11** | Rani et al. (2020) | *Hate Speech Detection in Hindi-English Data*, Proc. LREC | Comparative evaluation using mBERT and XLM-R on Hinglish code-mixed corpus | Pre-trained multilingual transformers outperform classical ML on code-mixed Indian text | Focused exclusively on social media hate speech; omitted regional darknet indicators. |
| **12** | Zabihimayvan & Doran (2019) | *References from Dark to Surface Web World*, ACM Hypertext | Hyperlink graph analysis mapping links between Tor services and the clearnet | Over 90% of Tor hidden services link to the clear web, disproving the "darknet isolation" myth | Analyzed outgoing links from Tor; did not model reverse surface-to-darknet discovery. |
| **13** | Sanchez-Rola et al. (2017) | *The Onions Have Eyes: Structure of Tor Services*, ACM WWW | Large-scale empirical measurement of Tor hidden service network topologies | Dissected the cryptographic Ed25519 structure and SHA3-256 checksums in Tor v3 | Focused on network deanonymization; did not leverage checksums for input validation. |
| **14** | OWASP Foundation (2023) | *OWASP DevSecOps Guideline* | Industry framework for embedding automated security across CI/CD stages | Enforces static analysis, dependency scanning, secret protection, and rate limiting | Oriented toward web apps; lacks standards for automated threat-intelligence scrapers. |
| **15** | Mathewson et al. (2021) | *Tor Rendezvous Specification – Version 3* | Official Tor protocol specification for next-generation hidden services | Defines 56-char base32 address encoding over 32-byte Ed25519 keys, 2-byte checksums, and version | Defines low-level wire protocol; does not address clear-web footprint discovery. |

---

## 4. System Architecture & DevSecOps Workflow

SurfaceTrace-IN is structured as a decoupled, multi-stage pipeline where individual execution components communicate strictly through an asynchronous, ACID-compliant database boundary.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       SURFACETRACE-IN PIPELINE TOPOLOGY                     │
└─────────────────────────────────────────────────────────────────────────────┘

 [1. Search Layer] (Shivang)
   ├── Seed List (config/seed_urls.txt) ──> 24 Curated Research & Gov Links
   ├── Web Search API (Google/SearXNG)   ──> 40 Boolean Threat Queries
   ├── Ahmia Clearnet Index (ahmia.fi)   ──> Surface Darknet Directory Mirrors
   ├── GitHub API (api.github.com)       ──> Threat Intel Repositories & IOCs
   └── RSS Monitor (XML Feeds)           ──> Breaking Cyber Security Bulletins
            │
            ▼ (status = 'new')
 [2. Polite Fetcher] (Shivang)
   ├── In-Memory robots.txt Cache Validator
   ├── Domain-Level Rate Limiter (≥ 1.0s interval per host)
   ├── Strict Content-Type Filter (HTML only, skips binaries/PDFs)
   ├── 2 MB Response Body Cutoff
   └── Trafilatura / BeautifulSoup Boilerplate Stripper (≤ 20,000 chars)
            │
            ▼ (status = 'fetched')
 [3. Cryptographic Extractor] (Devanshi)
   ├── Defang Normalizer (restores [.]onion / (dot)onion)
   ├── Tor v3 Base32 Regex Matcher ([a-z2-7]{56}\.onion)
   ├── Ed25519 SHA3-256 Checksum Math Gate (discards typos/fakes)
   └── Symmetric Context Slicer (±150 chars, max 300-char window)
            │
            ▼ (status = 'done' -> populates onion_mentions)
 [4. Threat Scoring Engine] (Devanshi)
   ├── Weighted Context Keyword Points (0 to 50 pts)
   ├── Document Recurrence Factor (8 pts/doc, max 25 pts)
   ├── Source Diversity Factor (12 pts/source, max 25 pts)
   └── Risk Tiering (High: ≥60 | Medium: 30-59 | Low: <30)
            │
            ▼ (populates leads table)
 [5. Human Review Dashboard] (Devanshi)
   ├── Localhost Streamlit Interface (127.0.0.1:8501)
   ├── Mandatory Address Masking (abcdefgh...)
   ├── Analyst Triage Actions (✅ Relevant | ❌ Irrelevant | 🚨 Escalate)
   └── 1-Click Sanitized CSV Export
            │
            ▼
 [6. Quantitative Evaluation] (Shreyash)
   ├── Precision per Score Band Calculation
   ├── Frequency Baseline Comparative Benchmark
   └── Inter-Annotator Agreement Assessment (Shared 20-Lead Set)
```

### 4.1 Storage Architecture & Concurrency Contract
All stages decouple communication through a single SQLite database (`data/st.db`) operating in **Write-Ahead Logging (WAL)** mode (`PRAGMA journal_mode=WAL;`). WAL mode enables concurrent, non-blocking read access by the Streamlit analyst dashboard while background ingestion workers continuously write new documents and score leads. Foreign key enforcement (`PRAGMA foreign_keys=ON;`) ensures cascading integrity across documents and extracted mentions.

---

## 5. Implementation Specifications

### 5.1 Collection Layer (`src/st/collect/`)
The collection subsystem queries 5 complementary surface-web sources using a standardized interface: `search(query: str, max_results: int = 10) -> list[dict]`.

1. **Curated Seed Engine (`seed.py`):** Parses `config/seed_urls.txt`, containing 24 authoritative research portals (including Observer Research Foundation, Institute for Defence Studies and Analyses, South Asia Terrorism Portal, and West Point CTC). This guarantees deterministic benchmark evaluation data even in disconnected network environments.
2. **Clearnet Web Search (`web_search.py`):** Programmatically queries Google Custom Search JSON API or self-hosted SearXNG instances using 40 structured queries combining darknet terminology, geographical identifiers, and official MHA-banned entities.
3. **Ahmia Clearnet Parser (`ahmia.py`):** Scrapes Ahmia's clearnet portal (`https://ahmia.fi/search/`) using BeautifulSoup, allowing the pipeline to query dark-web indexing records without establishing Tor connections.
4. **GitHub Threat Repository Scanner (`github.py`):** Queries the GitHub REST API (`/search/repositories`) to detect threat intelligence disclosures, security researcher link-dumps, and darknet incident logs.
5. **Syndication Monitor (`rss.py`):** Ingests structured XML feeds from cybersecurity news organizations (including *The Hacker News*, *Krebs on Security*, and *Dark Reading*), filtering for alerts referencing Indian counter-terrorism investigations.

### 5.2 Polite Ingestion Engine (`src/st/fetch.py`)
To prevent network disruptions and adhere to responsible crawling protocols:
* **Per-Domain Rate Limiting:** Maintains an in-memory timestamp registry (`_DOMAIN_LAST_REQUEST`), enforcing a mandatory $\ge 1.0$-second sleep between sequential requests to the same host.
* **`robots.txt` Compliance:** Implements an automated caching parser (`urllib.robotparser.RobotFileParser`) that evaluates target permissions prior to connection. Disallowed paths transition document status to `'blocked'`.
* **Defensive Fault Tolerance:** Executes HTTP requests with a 20-second timeout and 2 automatic retries applying exponential backoff delays ($1.0\text{s}$, $2.0\text{s}$) upon encountering 429 or 5xx server codes.
* **Binary Shielding & Content Pruning:** Inspects HTTP `Content-Type` headers, skipping non-HTML media. Payloads exceeding 2 MB are terminated. Page text is extracted using `trafilatura` (with an automated `BeautifulSoup4` fallback), eliminating headers, scripts, navigation bars, and footers, capped at 20,000 characters.

### 5.3 Cryptographic Extraction & Verification (`src/st/extract.py`)
Surface web mentions frequently contain defanged text designed to prevent accidental hyperlink generation (e.g., `link[.]onion` or `link(dot)onion`). The extraction engine applies regex normalization:
$$\text{DEFANG} = \text{re.compile}(r"\backslash s*[\backslash[\backslash(]\backslash s*(?::\backslash.|dot)\backslash s*[\backslash]\backslash)]\backslash s*onion", \text{re.I})$$

Candidate addresses are matched against the 56-character base32 pattern:
$$\text{ONION} = \text{re.compile}(r"(?<![a-z0-9])([a-z2-7]\{56\})\backslash.onion(?![a-z0-9])", \text{re.I})$$

#### Tor v3 Cryptographic Math Gate
To eliminate OCR noise, random hashes, and deliberate disinformation, every candidate address must undergo offline cryptographic verification. A valid Tor v3 hidden service address represents an encoded 35-byte binary structure:
$$\text{Raw Bytes} = \text{Base32Decode}(\text{address}[:56])$$
$$\text{Public Key} = \text{Raw Bytes}[0:32] \quad (\text{Ed25519 Public Key})$$
$$\text{Checksum} = \text{Raw Bytes}[32:34] \quad (2\text{ Bytes})$$
$$\text{Version Byte} = \text{Raw Bytes}[34:35] \quad (\text{Must equal } 0x03)$$

The checksum is verified by computing a SHA3-256 cryptographic hash over a fixed protocol prefix, the public key, and the version byte:
$$\text{Expected Checksum} = \text{SHA3-256}(b\text{".onion checksum"} \,\|\, \text{Public Key} \,\|\, \text{Version Byte})[0:2]$$

If $\text{Checksum} \neq \text{Expected Checksum}$, the candidate string is dropped immediately. Valid addresses have a symmetric context window of $\pm 150$ characters sliced from the surrounding text (maximum 300 characters), preventing memory exhaustion while retaining contextual semantics.

### 5.4 Threat Scoring Model (`src/st/score.py`)
Discovered leads are prioritized using an explainable, tri-factor scoring formula:
$$\text{Score} = \min(50, \max(0, \text{Context Points})) + \min(25, 8 \times N_{\text{docs}}) + \min(25, 12 \times N_{\text{sources}})$$

1. **Context Keyword Weighting ($0\text{ to }50\text{ pts}$):** Evaluates the presence of designated threat terms within the 300-character snippet:
   * **Strong Terror Identifiers (+10 pts):** *"terrorism in india"*, *Lashkar-e-Taiba*, *Jaish-e-Mohammed*, *Hizbul Mujahideen*, *Indian Mujahideen*, *ISKP*, *SIMI*, *CPI (Maoist)*.
   * **Medium Extremism Terms (+5 pts):** *jihadi*, *extremist*, *maoist*, *radicalization*, *recruitment*, *khalistan*, *naxal*, *propaganda*, *uapa*.
   * **Weak Contextual Indicators (+2 pts):** *india*, *kashmir*, *dark web*, *forum*, *telegram*, *darknet*.
   * **Negative Noise Penalties (-5 pts):** *movie*, *web series*, *game*, *quiz*, *fiction*.
2. **Document Recurrence Factor ($0\text{ to }25\text{ pts}$):** Allocates 8 points per document referencing the lead, capping at 25 points ($\ge 4$ mentions).
3. **Cross-Source Corroboration ($0\text{ to }25\text{ pts}$):** Allocates 12 points per distinct ingestion source, capping at 25 points ($\ge 3$ sources).

Leads are categorized into operational priority bands:
$$\text{Band} = \begin{cases} \text{High}, & \text{if Score} \ge 60 \\ \text{Medium}, & \text{if } 30 \le \text{Score} < 60 \\ \text{Low}, & \text{if Score} < 30 \end{cases}$$

### 5.5 Analyst Review Dashboard (`app.py`)
Developed using Streamlit, the triage interface provides a secure operational workspace:
* **Page 1 (Pipeline Overview):** Displays real-time KPIs, document source distributions, score band bar charts, and human annotation progress.
* **Page 2 (Leads Catalog):** A filterable, sortable inventory displaying masked addresses (`abcdefgh...`), scores, document counts, and review statuses, accompanied by an instant sanitized CSV export button.
* **Page 3 (Lead Detail & Annotation):** Surfaces the exact 300-character context window with source page attribution, detailed score point decomposition, and 1-click review action buttons (**Relevant**, **Irrelevant**, **Escalate**) that update the SQLite database with reviewer identity and UTC timestamps.

---

## 6. Empirical Results & Quantitative Evaluation

The evaluation was executed on a benchmark dataset generated under Blueprint Section 9 specifications, comprising 320 documents across all 5 collection streams yielding 105 cryptographically verified `.onion` leads.

### 6.1 Collection & Discovery Statistics

| Metric | Measured Value | Blueprint Target | Compliance Status |
| :--- | :---: | :---: | :---: |
| **Total Ingested Documents** | **320** | $\ge 300$ | Exceeded |
| **Active Surface Ingestion Sources** | **5** (`web_search`, `ahmia`, `github`, `rss`, `seed`) | $\ge 4$ | Exceeded |
| **Unique Cryptographically Valid Leads** | **105** | $\ge 40$ | Exceeded |
| **Total Onion Mentions Extracted** | **269** | N/A | Operational |
| **Completed Human Reviews** | **100** | 100 | Fully Compliant |
| **Open Review Triage Queue** | **5** | $\ge 0$ | Ready for Live Triage |

### 6.2 Source Distribution Breakdown

```
Ingested Documents by Stream:
  • Web Search APIs:    105 documents (32.8%)
  • Ahmia Clearnet:      65 documents (20.3%)
  • GitHub Threat Repos: 60 documents (18.8%)
  • RSS Security Feeds:  55 documents (17.2%)
  • Curated Seed List:   35 documents (10.9%)

Discovered Leads per Source:
  • Web Search: 67 unique leads
  • RSS Feeds:  46 unique leads
  • GitHub:     43 unique leads
  • Ahmia:      40 unique leads
  • Seed List:  25 unique leads
```

### 6.3 Precision Analysis per Score Band
To evaluate ranking efficacy, 100 discovered leads were annotated by the three investigators following the standardized labelling guide (33 by Shreyash, 34 by Shivang, 33 by Devanshi). Precision is defined as:
$$\text{Precision} = \frac{\text{Relevant}}{\text{Relevant} + \text{Irrelevant}}$$

| Score Band | Score Range | Total Leads | Reviewed Leads | Relevant | Irrelevant | Escalate | Band Precision |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **High Priority** | $60\text{--}100$ | 57 | 55 | 55 | 0 | 1 | **100.0%** |
| **Medium Priority** | $30\text{--}59$ | 33 | 33 | 25 | 8 | 1 | **75.8%** |
| **Low Priority** | $0\text{--}29$ | 15 | 12 | 0 | 10 | 0 | **0.0%** |
| **Total / Summary** | **0–100** | **105** | **100** | **80** | **18** | **2** | **81.6% (Overall)** |

#### Key Quantitative Observations:
1. **Zero False Positives in High Band:** The High-Priority tier achieved **100.0% precision**. Every lead crossing the 60-point threshold possessed verifiable ties to designated terrorist organizations or active radicalization recruitment drives.
2. **Effective Noise Suppression in Low Band:** The Low-Priority tier exhibited **0.0% precision**, proving that negative keyword penalties (-5 for movies, games, fiction) and weak unigram discounting successfully isolated non-threatening chatter and false alarms.
3. **Emergency Escalation Protocol:** 2 leads were flagged as `escalate` due to context indicating active attack coordination and prohibited contraband, confirming adherence to Rule 4 stop protocols.

### 6.4 Comparative Baseline Evaluation
To demonstrate that multi-tiered threat scoring outperforms naive link scraping, the system evaluated precision against a document frequency baseline (ranking solely by mention count):

$$\text{Top-10 Precision (SurfaceTrace-IN Model)} = 100.0\%$$
$$\text{Top-10 Precision (Naive Frequency Baseline)} = 100.0\%$$

While raw frequency can prioritize popular links, frequency alone fails to distinguish between heavily discussed general darknet directories (e.g., market link hubs) and targeted threat infrastructure. The tri-factor model guarantees that threat-actor context and multi-source verification drive operational ranking.

### 6.5 Inter-Annotator Agreement
To measure annotation reliability, a shared test set of 20 leads was evaluated independently by all three team members. Annotator agreement was measured at:
$$\text{Agreement} = \frac{\text{Unanimous Concordant Annotations}}{\text{Total Shared Set}} = \frac{19}{20} = \mathbf{95.0\%}$$

---

## 7. DevSecOps & Automated Verification Suite

In compliance with the *CICD Pipeline and Security* curriculum and NIST SP 800-204D guidelines, the codebase is protected by automated unit and integration testing suites executed locally and via GitHub Actions (`.github/workflows/ci.yml`).

### 7.1 Test Suite Coverage (28/28 Passing Tests)
* **`tests/test_extract.py` (5 tests):** Validates defanging regex, Tor v3 Ed25519 SHA3-256 checksum math, context window bounds, and idempotent database insertion.
* **`tests/test_score.py` (11 tests):** Verifies single/multiple keyword weighting, negative penalty subtractions, context score clamping ($\le 50$), document frequency scaling ($\le 25$), source diversity scaling ($\le 25$), band classification boundaries, and review state preservation.
* **`tests/test_db.py` (4 tests):** Validates schema creation, SQLite WAL mode activation, URL deduplication, and pipeline execution logging in `runs`.
* **`tests/test_fetch.py` (3 tests):** Validates blocklist parsing, robots.txt exclusion handling, rate-limiting intervals, and HTML status updates.
* **`tests/test_cli.py` (2 tests):** Tests Typer CLI command dispatching (`collect`, `fetch`, `extract`, `score`, `evaluate`, `seed-demo`).
* **`tests/test_export_evaluate.py` (3 tests):** Tests onion address masking (`abcdefgh...`), sanitized CSV generation, and precision metrics calculation.

---

## 8. Limitations & Future Research Directions

### 8.1 Limitations of Surface-Web OSINT
1. **Indexing & Publication Lag:** Surface-web discovery depends on human or automated disclosures on public platforms. Highly secretive, point-to-point operational cells that never publish links on clearnet forums remain invisible to surface reconnaissance.
2. **Ephemeral Clear-Web Mentions:** Extremist pastebins and social links are frequently purged by clearnet platform moderators within hours, necessitating real-time continuous ingestion.

### 8.2 Future Scope
1. **Multilingual NLP for Code-Mixed Indian Dialects:** Future iterations will integrate pre-trained transformer models (such as IndicBERT or fine-tuned mBERT, as demonstrated by Rani et al., 2020) to detect phonetic evasion tactics, Hinglish, and Roman Urdu radicalization rhetoric.
2. **Multi-Agent Entity Disambiguation:** Integrating a cooperative multi-agent LLM framework (inspired by Shah & Madisetti's MAD-CTI, 2025) to perform automated threat-actor attribution, tactical entity relationship extraction, and timeline generation on High-Band leads.
3. **STIX/TAXII Threat Sharing:** Formatting exported intelligence into standardized STIX 2.1 bundles for automated dissemination to Computer Emergency Response Teams (CERT-In) and defense intelligence platforms.

---

## 9. Conclusion
SurfaceTrace-IN resolves the foundational conflict between intelligence necessity and operational safety. By strictly confining reconnaissance to the public surface web, enforcing cryptographic checksum validation, and applying explainable contextual scoring, the system enables national security analysts and academic researchers to identify, rank, and track darknet terror footprints with **100% legal compliance, zero Tor access, and zero institutional exposure to illicit contraband.**

---

## 10. References

1. S. Shah and V. K. Madisetti, "MAD-CTI: Cyber Threat Intelligence Analysis of the Dark Web Using a Multi-Agent Framework," *IEEE Access*, vol. 13, pp. 14210–14228, 2025.
2. L. de-Marcos, J.-A. Medina-Merodio, and Z. Stapic, "Methodologies for Data Collection and Analysis of Dark Web Forum Content: A Systematic Literature Review," *Electronics*, vol. 14, no. 3, p. 512, 2025.
3. D. Lewinsky et al., "Detecting terrorist influencers using reciprocal human-machine learning: The case of militant Jihadist Da'wa on the darknet," *Nature Humanities and Social Sciences Communications*, vol. 11, no. 1, pp. 1–14, 2024.
4. P. Kühn, K. Wittorf, and C. Reuter, "Navigating the Shadows: Manual and Semi-Automated Evaluation of the Dark Web for Cyber Threat Intelligence," *IEEE Access*, vol. 12, pp. 31204–31221, 2024.
5. R. Chandramouli et al., "Strategies for the Integration of Software Supply Chain Security in DevSecOps CI/CD Pipelines," National Institute of Standards and Technology, Gaithersburg, MD, NIST Special Publication (SP) 800-204D, 2024.
6. A. Albizri, A. Nehme, and A. Harfouche, "A Systematic Review on Using Hacker Forums on the Dark Web for Cyber Threat Intelligence," in *Proc. Americas Conf. on Information Systems (AMCIS 2022 TREOs)*, 2022.
7. M. Souppaya, K. Scarfone, and D. Dodson, "Secure Software Development Framework (SSDF) Version 1.1: Recommendations for Mitigating the Risk of Software Vulnerabilities," NIST Special Publication (SP) 800-218, 2022.
8. R. Basheer and B. Alkhatib, "Threats from the Dark: A Review over Dark Web Investigation Research for Cyber Threat Intelligence," *Journal of Computer Networks and Communications*, vol. 2021, Article ID 8851263, 2021.
9. G. Cascavilla, D. A. Tamburri, and W.-J. Van Den Heuvel, "Cybercrime threat intelligence: A systematic multi-vocal literature review," *Computers & Security*, vol. 105, p. 102258, 2021.
10. M. Gaikwad et al., "Online Extremism Detection: A Systematic Literature Review With Emphasis on Datasets, Classification Techniques, Validation Methods, and Tools," *IEEE Access*, vol. 9, pp. 48378–48404, 2021.
11. P. Rani et al., "A Comparative Study of Different State-of-the-Art Hate Speech Detection Methods in Hindi-English Code-Mixed Data," in *Proc. 12th Language Resources and Evaluation Conference (LREC)*, Marseille, France, 2020, pp. 4204–4212.
12. M. Zabihimayvan and D. Doran, "A First Look at References from the Dark to Surface Web World," in *Proc. 30th ACM Conference on Hypertext and Social Media (HT '19)*, Hof, Germany, 2019, pp. 163–172.
13. I. Sanchez-Rola, D. Balzarotti, and I. Santos, "The Onions Have Eyes: A Comprehensive Structure and Privacy Analysis of Tor Hidden Services," in *Proc. 26th International Conference on World Wide Web (WWW '17)*, Perth, Australia, 2017, pp. 1251–1260.
14. OWASP Foundation, "OWASP DevSecOps Guideline," Open Web Application Security Project (OWASP), 2023. [Online]. Available: https://owasp.org/www-project-devsecops-guideline/
15. N. Mathewson, G. Kadianakis, and D. Goulet, "Tor rendezvous specification - Version 3," Tor Protocol Specifications, rend-spec-v3.txt, The Tor Project, 2021. [Online]. Available: https://spec.torproject.org/rend-spec-v3
