# Contributing to NeoSignal

Thank you for your interest in improving NeoSignal.

---

## What Counts as a Contribution

- Adding a new news source (RSS feed or API)
- Improving the authenticity scoring algorithm
- Improving PDF layout or typography
- Adding new keyword categories to the AI filter
- Bug fixes with a root cause analysis
- Documentation improvements

---

## Standards

All contributions must pass the full CI suite:

```bash
pytest tests/ -v          # All tests must pass
pylint src/ tests/         # Score must be ≥ 9.0 (target: 10.0)
```

---

## Adding a News Source

1. Add the source URL to `RSS_SOURCES` in `src/scraper.py` (for RSS/Atom)  
   or add a new scraper function following the `scrape_hackernews()` pattern.
2. Verify the source returns AI-relevant articles via the keyword filter.
3. Add test coverage in `tests/test_scraper.py`.

---

## Pull Request Checklist

- [ ] All 29 tests pass (`pytest tests/ -v`)
- [ ] Pylint score ≥ 9.0 (`pylint src/ tests/`)
- [ ] New functionality has corresponding tests
- [ ] CHANGELOG.md updated under the `[Unreleased]` section
- [ ] No credentials, tokens, or API keys in code or commits

---

## Reporting Issues

- **Bug**: Include the workflow run URL, the exact error, and expected vs actual behaviour.
- **New source request**: Include the RSS URL and a sample of 5 AI-relevant article titles.
- **Security**: See [SECURITY.md](SECURITY.md).
