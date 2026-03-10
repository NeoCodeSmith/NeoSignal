"""Unit tests for NeoSignal multi-source scraper v3."""

import json
from unittest.mock import MagicMock, patch

import requests as req

from src.scraper import _article_id, _is_ai, _similarity, deduplicate, scrape, _write


class TestIsAi:
    """Tests for the AI keyword filter."""

    def test_llm_matches(self):
        """LLM keyword should match."""
        assert _is_ai("Show HN: We built an LLM router") is True

    def test_case_insensitive(self):
        """Matching must be case-insensitive."""
        assert _is_ai("OpenAI releases GPT-5") is True

    def test_unrelated_does_not_match(self):
        """Non-AI story must not match."""
        assert _is_ai("Best coffee shops in Berlin") is False

    def test_empty_does_not_match(self):
        """Empty string must return False."""
        assert _is_ai("") is False

    def test_anthropic_matches(self):
        """'anthropic' must match."""
        assert _is_ai("Anthropic raises $2B") is True

    def test_alignment_matches(self):
        """'alignment' must match."""
        assert _is_ai("AI alignment research from DeepMind") is True


class TestArticleId:
    """Tests for the article ID function."""

    def test_same_title_same_id(self):
        """Same title must produce the same ID."""
        assert _article_id("GPT-5 is here") == _article_id("GPT-5 is here")

    def test_case_normalised(self):
        """ID must be case-insensitive."""
        assert _article_id("GPT-5") == _article_id("gpt-5")

    def test_returns_12_chars(self):
        """ID must be exactly 12 hex characters."""
        assert len(_article_id("any title")) == 12


class TestSimilarity:
    """Tests for title similarity scoring."""

    def test_identical_titles(self):
        """Identical titles must score 1.0."""
        assert _similarity("GPT-5 released", "GPT-5 released") == 1.0

    def test_very_different_titles(self):
        """Completely different titles must score below threshold."""
        score = _similarity("OpenAI raises funding", "Coffee shop in Berlin")
        assert score < 0.45

    def test_same_story_different_wording(self):
        """Same story with different wording must score above threshold."""
        score = _similarity(
            "OpenAI releases GPT-5 model",
            "OpenAI launches new GPT-5 language model"
        )
        assert score >= 0.45


class TestDeduplicate:
    """Tests for cross-source deduplication and scoring."""

    def _make_article(self, title, source, source_type="media", score=0):
        """Helper to build a minimal article dict."""
        return {
            "id": _article_id(title),
            "title": title,
            "url": "https://example.com",
            "source": source,
            "source_type": source_type,
            "score": score,
            "date": "2026-03-10",
            "scraped_at": "2026-03-10T00:00:00+00:00",
        }

    def test_single_article_gets_base_score(self):
        """Single-source article should get authenticity score of 0.5."""
        articles = [self._make_article("New LLM released", "TechCrunch AI")]
        result = deduplicate(articles)
        assert len(result) == 1
        assert result[0]["authenticity_score"] == 0.5

    def test_two_sources_boosts_score(self):
        """Same story from 2 sources must score above 0.5."""
        articles = [
            self._make_article("OpenAI launches GPT-5", "TechCrunch AI", "media"),
            self._make_article("OpenAI announces GPT-5 model", "VentureBeat AI", "media"),
        ]
        result = deduplicate(articles)
        assert len(result) == 1
        assert result[0]["authenticity_score"] > 0.5
        assert result[0]["source_count"] == 2

    def test_cross_type_diversity_bonus(self):
        """Community + media combination should get diversity bonus."""
        articles = [
            self._make_article("Anthropic Claude 4 released", "TechCrunch AI", "media"),
            self._make_article("Anthropic releases Claude 4", "HackerNews", "community"),
        ]
        result = deduplicate(articles)
        assert result[0]["authenticity_score"] >= 0.9

    def test_hn_score_bonus(self):
        """Article with HN score >= 100 should get bonus."""
        articles = [self._make_article("New neural net paper", "HackerNews", "community", score=250)]
        result = deduplicate(articles)
        assert result[0]["authenticity_score"] >= 0.6

    def test_low_auth_filtered(self):
        """Articles below MIN_AUTHENTICITY threshold must be dropped."""
        articles = [self._make_article("AI thing", "Unknown", "community", score=1)]
        # Single community source with no score = 0.5 base, which passes
        result = deduplicate(articles)
        assert len(result) == 1  # base 0.5 passes the 0.25 threshold

    def test_distinct_stories_not_merged(self):
        """Clearly different stories must not be merged."""
        articles = [
            self._make_article("OpenAI raises $10B from Microsoft", "TechCrunch AI"),
            self._make_article("New ArXiv paper on quantum computing algorithms", "ArXiv CS.AI"),
        ]
        result = deduplicate(articles)
        assert len(result) == 2


class TestWrite:
    """Tests for atomic file write."""

    def test_writes_structured_json(self, tmp_path, monkeypatch):
        """Written file must have meta + articles structure."""
        monkeypatch.setattr("src.scraper.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.scraper.NEWS_FILE", str(tmp_path / "news_feed.json"))
        articles = [{"id": "abc", "title": "Test LLM story", "url": "https://x.com",
                     "source": "HN", "source_type": "community", "score": 0,
                     "date": "2026-03-10", "scraped_at": "2026-03-10T00:00:00+00:00"}]
        _write(articles, raw_count=5)
        data = json.loads((tmp_path / "news_feed.json").read_text())
        assert data["meta"]["article_count"] == 1
        assert data["meta"]["raw_count"] == 5
        assert data["articles"][0]["title"] == "Test LLM story"

    def test_empty_feed_is_valid_json(self, tmp_path, monkeypatch):
        """Empty article list must still produce valid structured JSON."""
        monkeypatch.setattr("src.scraper.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.scraper.NEWS_FILE", str(tmp_path / "news_feed.json"))
        _write([])
        data = json.loads((tmp_path / "news_feed.json").read_text())
        assert data["articles"] == []


class TestScrape:
    """Integration tests for the full scrape pipeline."""

    def test_writes_output_on_total_network_failure(self, tmp_path, monkeypatch):
        """scrape() must always write news_feed.json even if all network calls fail."""
        monkeypatch.setattr("src.scraper.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.scraper.NEWS_FILE", str(tmp_path / "news_feed.json"))
        with patch("src.scraper.requests.get", side_effect=req.RequestException("down")):
            result = scrape()
        assert not result
        assert (tmp_path / "news_feed.json").exists()

    def test_filters_non_ai_from_hn(self, tmp_path, monkeypatch):
        """Scraper must exclude non-AI HN stories."""
        monkeypatch.setattr("src.scraper.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.scraper.NEWS_FILE", str(tmp_path / "news_feed.json"))

        call_count = [0]

        def mock_get(url, **_kwargs):
            """Mock HN endpoints."""
            mock = MagicMock()
            if "showstories" in url or "topstories" in url or "newstories" in url:
                mock.json.return_value = [1, 2]
            elif "/item/1" in url:
                mock.json.return_value = {
                    "id": 1, "title": "GPT-5 released by OpenAI",
                    "url": "https://openai.com", "score": 500,
                }
            elif "/item/2" in url:
                mock.json.return_value = {
                    "id": 2, "title": "Best pizza places in Rome",
                    "url": "https://food.com", "score": 10,
                }
            else:
                raise req.RequestException("reddit/rss blocked")
            call_count[0] += 1
            return mock

        with patch("src.scraper.requests.get", side_effect=mock_get):
            result = scrape()

        ai_titles = [a["title"] for a in result]
        assert any("GPT" in t for t in ai_titles)
        assert not any("pizza" in t.lower() for t in ai_titles)
