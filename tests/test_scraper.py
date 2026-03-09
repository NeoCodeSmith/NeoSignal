"""Unit tests for NeoSignal scraper module."""

import json
from unittest.mock import MagicMock, patch

import requests as req

from src.scraper import _write, fetch_story, fetch_story_ids, is_ai_related, scrape


class TestIsAiRelated:
    """Tests for the AI keyword filter."""

    def test_returns_true_for_llm(self):
        """LLM in title should match."""
        assert is_ai_related("Show HN: We built an LLM router") is True

    def test_returns_true_case_insensitive(self):
        """Keyword matching must be case-insensitive."""
        assert is_ai_related("OpenAI releases GPT-5") is True

    def test_returns_false_for_unrelated(self):
        """Non-AI story should not match."""
        assert is_ai_related("Ask HN: Best coffee shops in Berlin?") is False

    def test_returns_false_for_empty_string(self):
        """Empty string should never match."""
        assert is_ai_related("") is False

    def test_detects_neural(self):
        """'neural' keyword should match."""
        assert is_ai_related("Neural architecture search at scale") is True

    def test_detects_anthropic(self):
        """'anthropic' keyword should match."""
        assert is_ai_related("Anthropic raises $2B Series D") is True


class TestFetchStoryIds:
    """Tests for story ID fetching with fallback logic."""

    def test_returns_list_on_success(self):
        """Returns up to FETCH_LIMIT IDs when API is reachable."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = list(range(100))
        with patch("src.scraper.requests.get", return_value=mock_resp):
            result = fetch_story_ids()
        assert isinstance(result, list)
        assert len(result) == 50  # capped at FETCH_LIMIT

    def test_returns_empty_list_on_all_failure(self):
        """Returns empty list when all API endpoints are unreachable."""
        with patch("src.scraper.requests.get", side_effect=req.RequestException("network error")):
            result = fetch_story_ids()
        assert not result

    def test_returns_available_ids_on_partial_failure(self):
        """Falls back to top stories if show stories endpoint fails."""
        call_count = [0]

        def side_effect(_url, **_kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise req.RequestException("show stories down")
            mock = MagicMock()
            mock.json.return_value = list(range(30))
            return mock

        with patch("src.scraper.requests.get", side_effect=side_effect):
            result = fetch_story_ids()
        assert len(result) == 30


class TestFetchStory:
    """Tests for individual story fetching."""

    def test_returns_dict_on_success(self):
        """Returns story dict when API responds correctly."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"id": 123, "title": "Test", "url": "https://example.com"}
        with patch("src.scraper.requests.get", return_value=mock_resp):
            result = fetch_story(123)
        assert result["id"] == 123

    def test_returns_none_on_failure(self):
        """Returns None when story fetch fails."""
        with patch("src.scraper.requests.get", side_effect=req.RequestException("timeout")):
            result = fetch_story(456)
        assert result is None


class TestWrite:
    """Tests for the atomic write function."""

    def test_writes_valid_json(self, tmp_path, monkeypatch):
        """Written file must contain valid JSON with expected structure."""
        monkeypatch.setattr("src.scraper.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.scraper.NEWS_FILE", str(tmp_path / "news_feed.json"))
        articles = [{"id": 1, "title": "Test", "url": "https://x.com", "source": "HN", "date": "2026-01-01"}]
        _write(articles)
        data = json.loads((tmp_path / "news_feed.json").read_text())
        assert data["meta"]["article_count"] == 1
        assert data["articles"][0]["title"] == "Test"

    def test_writes_empty_feed_on_no_articles(self, tmp_path, monkeypatch):
        """Empty feed must still produce a valid JSON file with status reason."""
        monkeypatch.setattr("src.scraper.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.scraper.NEWS_FILE", str(tmp_path / "news_feed.json"))
        _write([], reason="no_ids")
        data = json.loads((tmp_path / "news_feed.json").read_text())
        assert data["meta"]["status"] == "no_ids"
        assert data["articles"] == []


class TestScrape:
    """Integration test: full scrape pipeline."""

    def test_scrape_writes_output_even_on_network_failure(self, tmp_path, monkeypatch):
        """Scrape must write output file even when all network calls fail."""
        monkeypatch.setattr("src.scraper.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.scraper.NEWS_FILE", str(tmp_path / "news_feed.json"))
        with patch("src.scraper.requests.get", side_effect=req.RequestException("unreachable")):
            result = scrape()
        assert not result
        assert (tmp_path / "news_feed.json").exists()

    def test_scrape_filters_non_ai_stories(self, tmp_path, monkeypatch):
        """Only AI-related stories should appear in the output."""
        monkeypatch.setattr("src.scraper.DATA_DIR", str(tmp_path))
        monkeypatch.setattr("src.scraper.NEWS_FILE", str(tmp_path / "news_feed.json"))

        def mock_get(url, **_kwargs):
            """Mock HN API responses."""
            mock = MagicMock()
            if "showstories" in url or "topstories" in url:
                mock.json.return_value = [1, 2]
            elif "/item/1" in url:
                mock.json.return_value = {
                "id": 1, "title": "GPT-5 released",
                "url": "https://openai.com",
                "score": 100}
            else:
                mock.json.return_value = {"id": 2, "title": "Coffee shop opens in Berlin", "url": "https://berlin.com", "score": 5}
            return mock

        with patch("src.scraper.requests.get", side_effect=mock_get):
            result = scrape()

        assert len(result) == 1
        assert "GPT" in result[0]["title"]
