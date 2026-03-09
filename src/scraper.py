"""
NeoSignal Scraper
Fetches AI-related stories from HackerNews API and writes them to data/news_feed.json.
Handles network failures gracefully — always produces a valid output file.
"""

import json
import logging
import os
from datetime import datetime, timezone

import requests

log = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
NEWS_FILE = os.path.join(DATA_DIR, "news_feed.json")

HN_SHOW_API = "https://hacker-news.firebaseio.com/v0/showstories.json"
HN_TOP_API  = "https://hacker-news.firebaseio.com/v0/topstories.json"
HN_ITEM_API = "https://hacker-news.firebaseio.com/v0/item/{}.json"
FETCH_LIMIT = 50

AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "llm", "large language model",
    "gpt", "claude", "gemini", "neural", "deep learning", "transformer",
    "diffusion", "stable diffusion", "openai", "anthropic", "mistral",
    "rag", "vector", "embedding", "fine-tun", "reinforcement learning",
]


def _safe_get(url: str, timeout: int = 10) -> requests.Response | None:
    """GET request with timeout. Returns None on any network error."""
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as exc:  # pylint: disable=broad-exception-caught
        # Network layers (urllib3, requests, OS) raise varied exception types
        log.warning("Request failed [%s]: %s", url, exc)
        return None


def fetch_story_ids() -> list[int]:
    """Fetch story IDs from Show HN, falling back to Top Stories."""
    for api_url in (HN_SHOW_API, HN_TOP_API):
        resp = _safe_get(api_url)
        if resp is not None:
            ids = resp.json()
            log.info("Fetched %d story IDs from %s", len(ids), api_url)
            return ids[:FETCH_LIMIT]
    log.error("All HN API endpoints unreachable.")
    return []


def fetch_story(story_id: int) -> dict | None:
    """Fetch a single story item. Returns None on failure."""
    resp = _safe_get(HN_ITEM_API.format(story_id))
    return resp.json() if resp is not None else None


def is_ai_related(title: str) -> bool:
    """Return True if the title contains any AI-related keyword."""
    lower = title.lower()
    return any(kw in lower for kw in AI_KEYWORDS)


def scrape() -> list[dict]:
    """
    Main entry point. Scrapes HN for AI articles and writes to NEWS_FILE.
    Always writes a valid JSON file — returns empty list on total failure.
    """
    log.info("NeoSignal scrape started.")
    os.makedirs(DATA_DIR, exist_ok=True)

    story_ids = fetch_story_ids()
    if not story_ids:
        log.warning("No story IDs fetched. Writing empty feed.")
        _write([], reason="no_ids")
        return []

    articles = []
    for sid in story_ids:
        story = fetch_story(sid)
        if not story:
            continue
        title = story.get("title", "").strip()
        if not title or not is_ai_related(title):
            continue
        articles.append({
            "id": sid,
            "title": title,
            "url": story.get("url") or f"https://news.ycombinator.com/item?id={sid}",
            "score": story.get("score", 0),
            "source": "HackerNews",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        })

    log.info("Found %d AI-related articles.", len(articles))
    _write(articles)
    return articles


def _write(articles: list[dict], reason: str = "ok") -> None:
    """Write articles to NEWS_FILE atomically."""
    payload = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "article_count": len(articles),
            "status": reason,
        },
        "articles": articles,
    }
    tmp = NEWS_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp, NEWS_FILE)
    log.info("Written %d articles to %s", len(articles), NEWS_FILE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    scrape()
