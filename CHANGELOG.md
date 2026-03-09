# Changelog

## [2.0.0] — 2026-03-10

Complete rebuild from `realtime-web-scraper`. Renamed to **NeoSignal**.

### Breaking Changes

- `scripts/` directory replaced by `src/` module structure
- `news_feed.json` now uses structured format: `{"meta": {...}, "articles": [...]}`
- `pdf_gen.py` and `generate_pdf_report.py` merged into `src/pdf_generator.py`

### Fixed

- **Unicode crash** — HN titles with `–`, `'`, `"` no longer crash PDF generation
- **Deprecated fpdf2 API** — migrated from `ln=1` / `Arial` to `XPos/YPos` / `Helvetica`
- **Silent scraper failure** — network errors no longer crash CI; empty feed written instead
- **Missing font in CI** — `fonts-dejavu-core` now installed in all PDF-generating workflows

### Added

- Dual API fallback: Show HN → Top Stories
- Deduplication via `history.log`
- Weekly digest with 4-category classification
- 10 unit tests covering all scraper code paths
- CI workflow (`ci.yml`) for tests + pylint on every push
- Graceful handling of 0-article runs throughout pipeline

## [1.x] — 2026 (realtime-web-scraper)

Legacy history. See git log for full record.
