# Changelog

All notable changes to NeoSignal are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [3.1.0] — 2026-03-10

### Fixed
- **Empty pages in PDF** — article cards used absolute `set_xy` coordinates causing `auto_page_break` to scatter card elements across 5+ blank pages. Rewrote with pure flow layout and pre-flight height estimation.
- **Headlines only** — scraper never captured article body/description. All 3 scrapers now extract summaries: HN `text` field, Reddit `selftext`, RSS `<description>` / `content:encoded` / Atom `<summary>`.

### Improved
- Deduplication now picks the longest available summary from any source variant of the same story.
- `digest.py` updated to v3.1 format: renders summaries, authenticity scores, multi-source badges.

---

## [3.0.0] — 2026-03-10

### Added
- **Multi-source scraping** — 10 sources: HN (Show/Top/New), Reddit ×4, TechCrunch AI, VentureBeat AI, MIT Tech Review, The Verge AI, Wired AI, ArXiv CS.AI
- **Cross-source authenticity scoring** — 0.25–1.0 range; VERIFIED / CONFIRMED / EMERGING tiers
- **Title-similarity deduplication** — `SequenceMatcher` across all sources (45% threshold)
- **Premium PDF** — cover page with stat cards, source breakdown table, tiered article sections, colour-coded badges, DejaVu Unicode font
- **Email delivery** — daily PDF emailed via Gmail SMTP at 9:00 AM IST; see `.github/EMAIL_SETUP.md`
- **Git push race-condition fix** — `git pull --rebase` before every push in all workflows
- 22 unit tests → expanded to 29

### Changed
- Renamed repository from `realtime-web-scraper` to **NeoSignal**

---

## [2.0.0] — 2026-03-09

### Changed
- Complete project rebuild. Force-pushed to `main`.
- `scripts/` replaced by `src/` module structure
- `news_feed.json` now uses structured format: `{"meta": {...}, "articles": [...]}`

### Fixed
- Unicode crash in PDF — HN titles with `–`, `'`, `"` no longer crash fpdf2
- Deprecated fpdf2 API — migrated from `ln=1` / `Arial` to `XPos/YPos` / `DejaVu`
- Silent scraper failure — network errors no longer crash CI
- `.gitignore` was excluding CI-generated files (PDFs, JSON, history.log)
- Pylint score raised from failing to **10.00/10**

### Added
- Dual HN API fallback: Show HN → Top Stories → New Stories
- `history.log` deduplication across runs
- Weekly digest with 4-category classification
- 10 unit tests; CI workflow enforces pylint ≥ 9.0

---

## [1.x] — 2026 (`realtime-web-scraper`)

Original proof-of-concept. Single-source HN scraper, basic PDF output.
