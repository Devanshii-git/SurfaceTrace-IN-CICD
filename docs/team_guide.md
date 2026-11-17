# SurfaceTrace-IN: The Complete Team Guide & Step-by-Step Walkthrough
**A Plain-English Handbook for Devanshi, Shivang, and Shreyash**

---

## 1. The Core Idea in 60 Seconds

### What is the project?
SurfaceTrace-IN is an **automated Open-Source Intelligence (OSINT) detection pipeline**. It searches the normal, public internet (the surface web) to find public leaks and mentions of dark-web (`.onion`) hidden services tied to **terrorism in India**, scores how dangerous each link is ($0\text{ to }100$), and displays them in a private web dashboard for human review.

### The Golden Rule
**We NEVER connect to Tor, we NEVER open any `.onion` website, and we NEVER create user accounts.** 
The entire pipeline operates 100% on the normal public web. We inspect the public *footprint* left behind on the clearnet.

```
       SURFACE WEB (Normal Internet)                     DARK WEB (Tor)
┌──────────────────────────────────────────┐      ┌──────────────────────────┐
│  • News Articles (The Hindu, TOI)        │      │                          │
│  • Research Papers (ORF, IDSA)           │      │   Hidden Extremist       │
│  • GitHub Threat Repositories            │      │   Forums & Portals       │
│  • Ahmia Clearnet Index (ahmia.fi)       │      │   (.onion sites)         │
│  • Cybersecurity RSS Feeds               │      │                          │
│                                          │      │                          │
│  "Police found suspect sharing           │      │                          │
│   darknet link: expyuzz...onion"         │      │                          │
│         ▲                                │      │                          │
│         │ (Our Tool Reads This Text!)    │      │  [NO DIRECT CONNECTION]  │
└─────────┼────────────────────────────────┘      └────────────┬─────────────┘
          │                                                    │
          └──────────────── X NEVER VISIT X ───────────────────┘
```

---

## 2. Why `.onion`? (The Extremist Paradox)

### What is a `.onion` link?
Normal websites end in `.com`, `.in`, or `.org`. A `.onion` address is a special website that exists only inside the **Tor network** (The Dark Web). For example:
`expyuzz5wqqfdgah56abcdefghijklmnopqrstuvwxyz1234567890.onion`
You cannot open it in Google Chrome; it only works inside the Tor Browser.

### Why do terror groups use `.onion`?
1. **Total Anonymity:** To get a `.com` site, you must buy it with a credit card, email, and phone number from companies like GoDaddy. A `.onion` address is generated for free by computer math—there is no company or owner name attached.
2. **Hidden Server Location:** Normal websites have an IP address (a physical location on a map). On Tor, traffic bounces through multiple encrypted computers. Police cannot pinpoint where the physical computer is.
3. **Cannot Be Taken Down:** If someone hosts terror manuals on `.com`, police or AWS shut it down in 10 minutes. A `.onion` site has no central authority to delete it.

### The Big Catch (Why Our Project Exists):
> **If an extremist `.onion` site is completely secret, how do they recruit new people?**
> If nobody knows the address, nobody visits it! 
> Therefore, recruiters and researchers are **forced to post the `.onion` link on the public internet** (forums, pastebins, research papers, news reports). 
> **That is where our tool catches them!**

---

## 3. Are We Training an AI Model or Checking?

**We are CHECKING, NOT training an AI.**

* We did **not** build or train a neural network (like ChatGPT or BERT).
* We built an **Automated Search & Detection Engine** (similar to how an antivirus scanner or specialized search engine works).
* The 5 sources are the **places we search**. 
* The scoring is based on an **explainable mathematical formula** (rule-based points for group names, recurrence, and diversity), not an unexplainable black-box AI.

---

## 4. Why ONLY These 5 Sources?

We search 5 specific surface-web sources. Each plays a distinct role:

| Source | Role | Why It Was Chosen |
| :--- | :--- | :--- |
| **1. Seed List** (`seed.py`) | *The Reliable Anchor* | Reads 24 trusted research papers (ORF, IDSA, SATP, West Point CTC). **Why:** Guarantees we always have verified benchmark data, even if external search APIs run out of quota or internet is offline. |
| **2. Web Search** (`web_search.py`) | *The Broad Net* | Searches Google & SearXNG. **Why:** Finds Indian news articles (*The Hindu, Times of India*) reporting on police counter-terror operations where darknet links are quoted. |
| **3. Ahmia Clearnet** (`ahmia.py`) | *The Window to Tor* | Ahmia crawls Tor but publishes its search page on the **normal web (`ahmia.fi`)**. **Why:** Lets us query dark-web listings *safely through a normal browser* without touching Tor! |
| **4. GitHub Repos** (`github.py`) | *The Security Whiteboard* | Searches GitHub via API. **Why:** Cybersecurity researchers and OSINT analysts upload IOC lists and threat-intelligence link-dumps to GitHub. |
| **5. RSS Feeds** (`rss.py`) | *The Breaking News Ticker* | Reads XML feeds from *The Hacker News* and *KrebsOnSecurity*. **Why:** Automatically ingests breaking cyber-threat alerts without needing complex web scrapers. |

### Why NOT Telegram, Twitter, or Darknet Forums?
* **Hard Rule #2 (No Logins):** Joining private extremist Telegram rooms or dark-web forums requires accounts. Under Indian law (**IT Act & UAPA**), joining terror chat rooms creates severe criminal liability.
* **Technical Anti-Bot Walls:** Twitter and Reddit block automated student scrapers with CAPTCHAs and expensive API paywalls. Our 5 sources are open, legal, and reliable.

---

## 5. Where Does Search Happen & What Are the 40 Queries?

* **Where?** Exclusively on the **clearnet (public internet)** using standard HTTPS calls to Google APIs, GitHub APIs, Ahmia's website, and RSS feeds.
* **What are the 40 queries?** They are located in `config/queries.txt`. They combine 3 specific pillars:
  $$\text{Darknet Term} + \text{India Region / Legal Term} + \text{Designated Terror Group}$$

### Examples from the 40 Queries:
1. **Designated Groups:** `"dark web" "Lashkar-e-Taiba"`, `"onion link" Jaish-e-Mohammed`, `"dark web" "ISKP" India`, `"hidden service" Hizbul Mujahideen`.
2. **Regional Insurgencies:** `"dark web" Khalistan extremist`, `"dark web" Maoist insurgency`, `"onion link" Kashmir terrorism`.
3. **Operational Threats:** `"terrorism in India" "dark web" forum`, `"darknet" terror module India`, `"dark web" terror funding India`.

---

## 6. Step-by-Step Execution: What Happens When You Type `run-all`?

When you run `python -m st run-all`, the pipeline executes 4 automated stages in sequence:

```
[1. Collect] ────> [2. Fetch] ────> [3. Extract] ────> [4. Score] ────> [5. Dashboard]
(5 Sources)     (Download & Clean)  (Crypto Math)   (Threat Points)   (Streamlit UI)
```

---

### Step 1: Collection (`src/st/collect/`)
* The script reads `config/queries.txt`.
* It calls all 5 collectors (`seed`, `web_search`, `ahmia`, `github`, `rss`).
* It inserts candidate URLs into the SQLite `documents` table with `status = 'new'`. Duplicate URLs are automatically ignored.

---

### Step 2: Polite Fetching & Cleaning (`src/st/fetch.py`)
For every document where `status = 'new'`:

1. **Why check `robots.txt`?**
   - It's the internet's "do-not-enter" sign. Following it ensures we respect website owners, follow Indian IT Act ethical guidelines, and prevent our IP address from being banned by firewalls (Cloudflare).
2. **Why the 1-second delay?**
   - It enforces a speed limit ($\le 1$ request per second per domain) so we don't accidentally overload anyone's server like a DDoS attack.
3. **Why download ONLY HTML (skipping PDFs, images, videos, zip files)?**
   - **Legal Protection (CSAM / Terror Contraband):** Dark-web forums frequently circulate illegal videos and Child Sexual Abuse Material. Under **Section 67B of the IT Act**, possessing or downloading such files carries mandatory criminal penalties. By downloading **HTML text ONLY**, we can never accidentally download illegal files!
   - **Malware Protection:** Terrorists and hackers hide viruses inside `.zip`, `.pdf`, and `.exe` files. Plain HTML text cannot infect your computer.
   - **Speed & Memory:** A video is 100 MB; an HTML text page is 20 KB.
4. **HTML Cleaning:**
   - Strips out ads, javascript `<script>`, menus `<nav>`, and footers `<footer>` using `BeautifulSoup` and `trafilatura`.
   - Caps clean article text to 20,000 characters and updates `status = 'fetched'`.

---

### Step 3: Cryptographic Extraction (`src/st/extract.py`)
For every document where `status = 'fetched'`:

1. **Defanging:** Restores obfuscated text (converts `example[.]onion` or `example(dot)onion` into `example.onion`).
2. **Regex Matching:** Finds any 56-character base32 string ending in `.onion`.
3. **Did it use an AI prompt? NO! It uses Cryptographic Math:**
   - Can someone trick the tool by typing 56 random letters? **No.**
   - In Tor v3, characters 1–52 are the public key, characters 53–54 are a checksum, and character 55 is the version (`03`).
   - The code calculates:
     $$\text{Expected Checksum} = \text{SHA3-256}(b\text{".onion checksum"} \,\|\, \text{Public Key} \,\|\, \text{Version Byte})[0:2]$$
   - If the address's checksum does not match the math, **it is rejected as fake or corrupted!**
4. **Context Window:** It cuts **150 characters before** and **150 characters after** the link (a 300-character snippet).
5. **Save:** Saves into the `onion_mentions` table and updates document `status = 'done'`.

---

### Step 4: Threat Scoring (`src/st/score.py`)
The tool calculates a danger score ($0\text{--}100$) for every verified address:

$$\text{Score} = \min(50, \text{Context Points}) + \min(25, 8 \times N_{\text{docs}}) + \min(25, 12 \times N_{\text{sources}})$$

* **Context Points (Up to 50 pts):**
  - Group names (*Lashkar-e-Taiba, CPI Maoist, ISKP*) $\to$ **+10 pts each**.
  - Threat words (*radicalization, recruitment, jihadi, khalistan*) $\to$ **+5 pts each**.
  - False-alarm penalty (*movie, web series, game, quiz*) $\to$ **-5 pts penalty**.
* **Document Recurrence (Up to 25 pts):** Mentioned in multiple articles? (8 pts per document).
* **Source Diversity (Up to 25 pts):** Mentioned across both news and GitHub? (12 pts per distinct source).
* **Assigns Priority Band:**
  - **High Priority ($\ge 60$):** Immediate verified threat.
  - **Medium Priority ($30\text{--}59$):** Suspicious extremist chatter.
  - **Low Priority ($< 30$):** Harmless noise, movies, or general directories.

---

### Step 5: Analyst Review Dashboard (`app.py`)
Run `streamlit run app.py` to open the local analyst portal (`http://localhost:8501`):
* **Page 1 (Overview):** Operational metrics (320 Documents, 105 Leads) and bar charts of leads per band and source.
* **Page 2 (Leads Catalog):** Searchable table with **masked addresses** (`abcdefgh...`) and a 1-click **Export Masked CSV** button.
* **Page 3 (Lead Detail):** Displays the exact 300-character context snippet, score breakdown, and live review action buttons (**✅ Relevant**, **❌ Irrelevant**, **🚨 Escalate**).

---

### Step 6: Empirical Evaluation (`src/st/evaluate.py`)
Run `$env:PYTHONPATH="src;." ; python -m st evaluate`:
* **High Band Precision:** **100.0%** (55 relevant / 0 irrelevant).
* **Medium Band Precision:** **75.8%** (25 relevant / 8 irrelevant).
* **Low Band Precision:** **0.0%** (Noise cleanly suppressed to the bottom).
* **Shared Consensus Agreement:** **95.0%** (19 of 20 leads unanimously agreed upon by all three team members).

---

## 7. Command Cheat Sheet for the Team

| Command | What It Does Under the Hood | When to Use It |
| :--- | :--- | :--- |
| **`pytest`** | Runs all 28 automated unit tests; verifies math, regex, database, and scoring logic. | First step in the demo to prove software quality. |
| **`$env:PYTHONPATH="src;." ; python -m st evaluate`** | Calculates precision per band, source yields, and baseline comparison from SQLite. | Second step in the demo to show evaluation metrics. |
| **`streamlit run app.py`** | Boots the localhost analyst review dashboard at `http://localhost:8501`. | Third step in the demo to show the interactive UI. |
| **`python -m st run-all`** | Runs the complete 4-stage pipeline (Collect $\to$ Fetch $\to$ Extract $\to$ Score) end-to-end. | Use when performing a fresh pipeline run. |
| **`python -m st seed-demo`** | Populates `data/demo.db` and `data/st.db` with the verified benchmark dataset. | Use to restore demo data instantly. |

---

## 8. Panel Defense Q&A (How to Answer Examiner Questions)

### Q1: "How can you be certain you didn't connect to Tor?"
* **Answer:** *"Our codebase uses standard Python HTTP libraries (`requests`) without SOCKS5 proxies or Tor daemon bindings. All network connections are dispatched exclusively to standard clearnet HTTP/HTTPS domains."*

### Q2: "What if someone writes a fake .onion address in a forum?"
* **Answer:** *"Tor v3 addresses contain an embedded cryptographic checksum. Our `is_valid_v3` function extracts the public key and computes a SHA3-256 digest over the key and version byte. Random or corrupted strings fail with 99.99% mathematical certainty and are dropped immediately."*

### Q3: "Why did you use rule-based scoring instead of an AI / LLM classifier?"
* **Answer:** *"In national security and legal intelligence, models must be fully explainable and auditable in court. Deep black-box neural networks hallucinate and cannot explain why a score was given. Our tri-factor model provides transparent, verifiable point attribution."*

### Q4: "Why is this project suitable for a DevSecOps / CICD course?"
* **Answer:** *"Most threat intelligence scripts are fragile, manual, and unmaintained. We built an automated, continuous DevSecOps pipeline with automated policy gates (`robots.txt` compliance, rate limiting), 28 automated regression tests, Docker packaging, and SQLite WAL concurrency."*
