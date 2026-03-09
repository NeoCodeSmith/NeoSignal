# Contributing to NeoSignal

## Setup

```bash
git clone https://github.com/NeoCodeSmith/NeoSignal.git
cd NeoSignal
pip install -r requirements.txt
```

## Before Opening a PR

- [ ] `pytest tests/ -v` passes
- [ ] `pylint $(git ls-files '*.py') --fail-under=9.0` passes
- [ ] New behaviour has a corresponding test
- [ ] No secrets or hardcoded credentials

## What's Welcome

- New AI keyword patterns (with evidence they reduce false negatives)
- Additional HN API sources or data sources
- PDF layout improvements
- Performance improvements to the scraper
- Bug fixes with a reproducing test case

## What Won't Be Merged

- Breaking changes to the `news_feed.json` schema without a migration path
- Dependencies that are not available via pip on Python 3.11
- Code that does not pass pylint at 9.0+

## Code Style

- Follow existing structure: `src/`, `tests/`
- All functions must have docstrings
- Imports: stdlib → third-party → local
- No bare `except:` — catch specific exceptions
