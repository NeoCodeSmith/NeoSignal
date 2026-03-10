<div align="center">

<img src="https://img.shields.io/badge/NeoSignal-AI%20Intelligence-0A1228?style=for-the-badge&labelColor=0A1228&color=006EE6" alt="NeoSignal"/>

# NeoSignal

### AI News Intelligence — Daily

**Scrapes 10 authoritative sources · Cross-verifies stories · Generates premium PDF reports · Delivers by email · Fully automated on GitHub Actions**

<br/>

[![CI](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/ci.yml/badge.svg)](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/ci.yml)
[![Daily Pipeline](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/daily_pipeline.yml/badge.svg)](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/daily_pipeline.yml)
[![Weekly Digest](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/weekly_digest.yml/badge.svg)](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/weekly_digest.yml)
[![Pylint 10/10](https://img.shields.io/badge/pylint-10.00%2F10-brightgreen)](https://pylint.org)
[![Tests](https://img.shields.io/badge/tests-29%20passing-brightgreen)](tests/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<br/>

```
10 Sources  →  AI Filter  →  Cross-Verify  →  Score  →  Premium PDF  →  Email  →  Git
```

**No backend. No database. No server. Zero infrastructure cost.**

</div>

---

## What Is NeoSignal?

NeoSignal is a fully automated AI news intelligence pipeline. Every morning at **9:00 AM IST**, it:

1. **Scrapes** 10 authoritative AI news sources simultaneously
2. **Filters** 30+ AI keyword patterns across all articles
3. **Deduplicates** stories that appear across multiple sources using title-similarity matching
4. **Scores** each story with an authenticity score based on cross-source verification
5. **Generates** a premium multi-page PDF intelligence report
6. **Emails** the report directly to your inbox
7. **Commits** the report to this repository as a permanent record

Every Sunday at **9:00 PM IST**, a weekly digest categorises the week's stories into 4 intelligence domains.

---

## Sources

| Source | Type | Coverage |
|---|---|---|
| HackerNews (Show / Top / New) | Community | Practitioner discussions, OSS launches |
| Reddit r/artificial | Community | General AI news and discussion |
| Reddit r/MachineLearning | Community | Research papers, technical debate |
| Reddit r/singularity | Community | AI futures and strategic implications |
| Reddit r/LocalLLaMA | Community | Local model deployment and benchmarks |
| TechCrunch AI | Media | Industry news, funding, products |
| VentureBeat AI | Media | Enterprise AI, strategy, investments |
| MIT Technology Review | Media | Research-grade analysis |
| The Verge AI | Media | Consumer AI, products, policy |
| Wired AI | Media | Long-form AI journalism |
| ArXiv CS.AI | Research | Pre-print papers, cutting-edge research |

---

## Authenticity Scoring

Every story is scored **0 – 100%** based on independent cross-source verification:

| Tier | Score | Meaning |
|---|---|---|
| 🟢 **VERIFIED** | 80 – 100% | Covered by 3+ independent sources including media outlets |
| 🟡 **CONFIRMED** | 50 – 79% | Covered by 2 sources, or 1 high-quality media outlet |
| ⚪ **EMERGING** | 25 – 49% | Single-source; passes AI keyword filter |

Stories below **25%** authenticity are automatically dropped.

**Score formula:**
```
authenticity = 0.5 (base)
             + 0.3 × (additional sources, max +0.5)
             + 0.1 (if story spans both community + media types)
             + 0.1 (if HN score ≥ 100)
             = max 1.0
```

---

## PDF Report Structure

Each daily report contains:

| Page | Content |
|---|---|
| 1 | **Cover** — Brand bar, date, stat cards (Total / Verified / Confirmed / Emerging), pipeline explanation, tier legend |
| 2 | **Source Breakdown** — Table showing article count per source and category |
| 3+ | **Intelligence Tiers** — Articles grouped by VERIFIED → CONFIRMED → EMERGING, each with title, source badge, summary, authenticity %, and URL |

---

## Repository Structure

```
NeoSignal/
├── src/
│   ├── scraper.py          # Multi-source scraper with cross-source authenticity scoring
│   ├── pdf_generator.py    # Premium PDF report engine (DejaVu Unicode font)
│   └── digest.py           # Weekly categorised digest generator
├── tests/
│   └── test_scraper.py     # 29 unit tests — keyword filter, dedup, scoring, I/O
├── data/
│   └── news_feed.json      # Latest scrape output — auto-updated by CI daily
├── reports/                # Daily PDF reports — auto-committed by CI
├── archive/                # Weekly digest PDFs — auto-committed Sunday nights
├── history.log             # Deduplication log — prevents re-reporting seen stories
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # Tests + Pylint on every push/PR
│   │   ├── daily_pipeline.yml  # 9:00 AM IST — scrape → PDF → email → commit
│   │   └── weekly_digest.yml   # 9:00 PM IST Sunday — digest → email → commit
│   └── EMAIL_SETUP.md          # Step-by-step email delivery setup guide
├── requirements.txt
└── .pylintrc
```

---

## Quick Start

### Prerequisites

```bash
git clone https://github.com/NeoCodeSmith/NeoSignal.git
cd NeoSignal
pip install -r requirements.txt
sudo apt-get install -y fonts-dejavu-core   # Ubuntu/Debian — required for Unicode PDF
```

### Run the Pipeline Locally

```bash
# 1. Scrape all sources and produce data/news_feed.json
python -m src.scraper

# 2. Generate the PDF report
python -m src.pdf_generator

# 3. Generate weekly digest
python -m src.digest
```

### Run Tests

```bash
pytest tests/ -v
```

### Check Code Quality

```bash
pylint src/ tests/
```

---

## Automated Delivery — Email Setup

The daily report is emailed automatically at 9:00 AM IST.  
**One-time setup: add 3 repository secrets.**

See **[.github/EMAIL_SETUP.md](.github/EMAIL_SETUP.md)** for the full step-by-step guide.

| Secret | Description |
|---|---|
| `EMAIL_USERNAME` | Your Gmail address |
| `EMAIL_PASSWORD` | Gmail App Password (16 chars) — **not** your account password |
| `EMAIL_TO` | Recipient email address |

---

## Schedules

| Workflow | Schedule | IST | UTC |
|---|---|---|---|
| Daily Report | Every day | 9:00 AM | 3:30 AM |
| Weekly Digest | Every Sunday | 9:00 PM | 3:30 PM |

Both workflows can also be triggered manually from the **Actions** tab → **Run workflow**.

---

## CI / CD

| Workflow | Trigger | Steps |
|---|---|---|
| `ci.yml` | Every push + PR to `main` | Install deps → Run 29 tests → Pylint (≥ 9.0 required) |
| `daily_pipeline.yml` | 9 AM IST cron + manual | Install fonts → Scrape → Validate → PDF → Validate → Email → Commit |
| `weekly_digest.yml` | 9 PM IST Sunday + manual | Scrape → Digest PDF → Email → Commit to archive |

All commits use `GITHUB_TOKEN` — no personal tokens stored.

---

## Technical Details

### Scraper (`src/scraper.py`)

- Parallel scraping across 10+ sources with full error isolation per source
- `_safe_get()` catches all network exceptions — one failed source never crashes the pipeline
- Title-similarity deduplication using `SequenceMatcher` (45% threshold)
- HTML stripping and entity decoding for RSS `<description>` fields
- Atomic JSON write (`os.replace`) — partial writes never corrupt the feed

### PDF Generator (`src/pdf_generator.py`)

- DejaVu Unicode TTF font — handles em-dashes, smart quotes, ellipses natively
- Pure flow layout — zero absolute `set_xy` inside article cards
- Pre-flight height estimation — page breaks happen before cards, never mid-card
- Colour-coded tiers (green/amber/slate), source type badges (blue=media, purple=community)
- Left tier stripe, alternating card backgrounds, running header/footer

### Authenticity Engine

```python
authenticity = min(
    0.5                                      # base score
    + min(0.3 * (n_sources - 1), 0.5)       # cross-source bonus (capped)
    + (0.1 if cross_type_diversity else 0)   # community + media both present
    + (0.1 if hn_score >= 100 else 0),       # high community engagement
    1.0
)
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Security

See [SECURITY.md](SECURITY.md).

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built with GitHub Actions · fpdf2 · Python 3.11

**No servers were harmed in the making of this pipeline.**

</div>
