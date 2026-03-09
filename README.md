<div align="center">

# NeoSignal

**AI news intelligence pipeline. Extracts signal from HackerNews noise — daily.**

[![CI](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/ci.yml/badge.svg)](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/ci.yml)
[![Daily Pipeline](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/daily_pipeline.yml/badge.svg)](https://github.com/NeoCodeSmith/NeoSignal/actions/workflows/daily_pipeline.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)

</div>

---

## What It Does

NeoSignal monitors HackerNews daily, filters for AI-related stories, and auto-generates styled PDF intelligence reports — committed directly to the repository on schedule.

```text
HackerNews API  →  Scraper  →  AI Filter  →  PDF Generator  →  Git commit
                                                    ↓
                                          Weekly Digest (Sunday)
```

**No backend. No database. No server.** Everything runs on GitHub Actions.

---

## Features

- **Smart AI filter** — 20+ keyword patterns covering LLMs, research, tools, business
- **Dual API fallback** — falls back from Show HN to Top Stories if one endpoint is down
- **Unicode-safe PDFs** — uses DejaVu TTF font in CI; ASCII sanitisation as fallback
- **Deduplication** — `history.log` tracks seen articles across runs
- **Weekly digest** — categorised Sunday summary across 4 intelligence domains
- **Zero silent failures** — always writes a valid `news_feed.json` even on network errors
- **Pylint 10.00/10** — enforced in CI

---

## Repository Structure

```text
NeoSignal/
├── src/
│   ├── scraper.py          # HN scraper with fallback API + graceful error handling
│   ├── pdf_generator.py    # Unicode-safe PDF report engine
│   └── digest.py           # Weekly categorised digest generator
├── tests/
│   └── test_scraper.py     # 10 unit tests covering all scraper paths
├── data/
│   └── news_feed.json      # Latest scrape output (auto-updated by CI)
├── reports/                # Generated PDF reports
├── archive/                # Weekly digest PDFs
├── history.log             # Deduplication log
├── .github/workflows/
│   ├── ci.yml              # Tests + Pylint on every push
│   ├── daily_pipeline.yml  # Hourly scrape + PDF generation
│   └── weekly_digest.yml   # Sunday digest
└── requirements.txt
```

---

## Quick Start

### Run Locally

```bash
git clone https://github.com/NeoCodeSmith/NeoSignal.git
cd NeoSignal
pip install -r requirements.txt

# Run the scraper
python -m src.scraper

# Generate a PDF report
python -m src.pdf_generator

# Generate weekly digest
python -m src.digest
```

### Run Tests

```bash
pytest tests/ -v
```

### Check Code Quality

```bash
pylint $(git ls-files '*.py')
```

---

## How the Pipeline Works

### 1. Scraper (`src/scraper.py`)

- Hits `hacker-news.firebaseio.com/v0/showstories.json` (falls back to `topstories`)
- Fetches up to 50 story items concurrently
- Filters by 20+ AI keywords (case-insensitive)
- Writes structured JSON with metadata to `data/news_feed.json`
- **Always writes output** — network failure → empty feed, not a crash

### 2. PDF Generator (`src/pdf_generator.py`)

- Reads `news_feed.json`, deduplicates against `history.log`
- Generates a styled PDF with article titles, scores, URLs
- Uses DejaVu Unicode font when available; ASCII sanitisation otherwise
- Saves to `reports/neosignal_report_YYYYMMDD_HHMM.pdf`
- Skips gracefully if no new articles

### 3. Weekly Digest (`src/digest.py`)

- Categorises the week's articles across 4 domains:
  - Model Releases & Research
  - Strategic & Business
  - Safety & Regulation
  - Tools & Engineering
- Saves to `archive/YYYY-WWW/neosignal_digest_YYYY-WWW.pdf`

---

## CI / CD

| Workflow | Trigger | What It Does |
|---|---|---|
| `ci.yml` | Every push to `main` | Runs tests + pylint |
| `daily_pipeline.yml` | 06:00 UTC daily | Scrape → filter → PDF → commit |
| `weekly_digest.yml` | 20:00 UTC Sunday | Digest → archive → commit |

All workflows use `GITHUB_TOKEN` for authenticated push. No secrets required.

---

## Configuration

All settings are environment-variable driven:

| Variable | Default | Description |
|---|---|---|
| `HN_FETCH_LIMIT` | `50` | Max stories to fetch per run |
| `REPORT_DAYS` | `7` | Lookback window for weekly digest |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — see [LICENSE](LICENSE).
