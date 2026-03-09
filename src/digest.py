"""
NeoSignal Weekly Digest Generator
Reads history.log + news_feed.json to produce a categorised weekly summary PDF.
"""

import json
import logging
import os
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fpdf import FPDF, XPos, YPos

log = logging.getLogger(__name__)

BASE_DIR     = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "history.log"
NEWS_FILE    = BASE_DIR / "data" / "news_feed.json"
ARCHIVE_DIR  = BASE_DIR / "archive"

CATEGORIES = {
    "Model Releases & Research": ["model", "release", "paper", "benchmark", "gpt", "claude", "gemini", "llm"],
    "Strategic & Business": ["startup", "funding", "acquisition", "partnership", "investment", "revenue"],
    "Safety & Regulation": ["safety", "alignment", "regulation", "ban", "risk", "policy", "governance"],
    "Tools & Engineering": ["open source", "framework", "library", "tool", "sdk", "api", "deployment"],
}

TTF_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]


def _sanitize(text: str) -> str:
    """Replace smart punctuation, then strip non-Latin-1."""
    for src, dst in {"\u2013": "-", "\u2014": "--", "\u2018": "'", "\u2019": "'",
                     "\u201c": '"', "\u201d": '"', "\u2026": "..."}.items():
        text = text.replace(src, dst)
    return unicodedata.normalize("NFKD", text).encode("latin-1", errors="ignore").decode("latin-1")


def _find_ttf() -> str | None:
    return next((p for p in TTF_CANDIDATES if os.path.exists(p)), None)


def load_recent_articles(days: int = 7) -> list[dict]:
    """Load articles from news_feed.json that fall within the past N days."""
    if not NEWS_FILE.exists():
        log.warning("news_feed.json not found.")
        return []
    try:
        data = json.loads(NEWS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log.error("JSON parse error: %s", exc)
        return []

    articles = data.get("articles", []) if isinstance(data, dict) else data
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).date()
    recent = []
    for a in articles:
        try:
            if datetime.fromisoformat(a.get("date", "2000-01-01")).date() >= cutoff:
                recent.append(a)
        except ValueError:
            recent.append(a)  # include if date unparseable
    log.info("Loaded %d articles from past %d days.", len(recent), days)
    return recent


def categorize(articles: list[dict]) -> dict:
    """Assign each article to its first matching category."""
    result = defaultdict(list)
    for article in articles:
        text = (article.get("title", "") + " " + article.get("url", "")).lower()
        matched = False
        for category, keywords in CATEGORIES.items():
            if any(kw in text for kw in keywords):
                result[category].append(article)
                matched = True
                break
        if not matched:
            result["General AI News"].append(article)
    return dict(result)


class DigestPDF(FPDF):
    """Weekly AI intelligence digest PDF."""

    def __init__(self, week: str, use_unicode: bool = False, font_path: str | None = None):
        super().__init__()
        self._week = week
        self._unicode = use_unicode
        if use_unicode and font_path:
            self.add_font("DejaVu", style="", fname=font_path)
            self.add_font("DejaVu", style="B", fname=font_path)
            self._fn = "DejaVu"
        else:
            self._fn = "Helvetica"
        self.font_name = self._fn  # public alias for external access

    def _t(self, text: str) -> str:
        """Return text as-is for unicode fonts, sanitised otherwise."""
        return text if self._unicode else _sanitize(text)

    def header(self):
        """Render the page header."""
        self.set_font(self._fn, "B", 15)
        self.set_fill_color(10, 20, 50)
        self.set_text_color(255, 255, 255)
        self.cell(0, 13, self._t(f"NeoSignal  |  Weekly AI Digest  |  Week {self._week}"),
                  border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True)
        self.ln(5)
        self.set_text_color(0, 0, 0)

    def footer(self):
        """Render the page number footer."""
        self.set_y(-12)
        self.set_font(self._fn, size=8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    def section_header(self, title: str, count: int):
        """Render a bold category section header."""
        self.set_font(self._fn, "B", 11)
        self.set_fill_color(220, 230, 255)
        self.cell(0, 9, self._t(f"  {title}  ({count})"),
                  border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
        self.ln(2)

    def article_entry(self, article: dict):
        """Render a single article entry."""
        self.set_font(self._fn, size=9)
        title = self._t(article.get("title", "Untitled"))
        url = self._t(article.get("url", "")[:90])
        score = article.get("score", 0)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 5, f"* {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(80, 80, 80)
        self.cell(0, 4, f"  Score: {score}  |  {url}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(2)


def generate_digest() -> str | None:
    """Generate weekly digest PDF. Returns path or None."""
    articles = load_recent_articles()
    if not articles:
        log.warning("No articles found — skipping digest.")
        return None

    categorized = categorize(articles)
    week = datetime.now().strftime("%Y-W%W")

    ttf = _find_ttf()
    pdf = DigestPDF(week=week, use_unicode=ttf is not None, font_path=ttf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    total = sum(len(v) for v in categorized.values())
    pdf.set_font(pdf.font_name, size=9)
    pdf.set_fill_color(240, 248, 255)
    pdf.cell(0, 7, f"  {total} AI stories categorised this week",
             border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True)
    pdf.ln(5)

    for category, cat_articles in sorted(categorized.items()):
        pdf.section_header(category, len(cat_articles))
        for article in cat_articles[:10]:  # cap at 10 per category
            pdf.article_entry(article)
        pdf.ln(3)

    week_dir = ARCHIVE_DIR / week
    week_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = week_dir / f"neosignal_digest_{week}.pdf"
    pdf.output(str(pdf_path))
    log.info("Digest generated: %s", pdf_path)
    return str(pdf_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    generate_digest()
