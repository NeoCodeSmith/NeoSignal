"""
NeoSignal PDF Generator
Reads data/news_feed.json and produces a dated PDF intelligence report.

FIX vs old code:
  - Uses fpdf2 modern API (XPos/YPos instead of deprecated ln=1)
  - Uses fpdf2's built-in UTF-8 support via add_font() with a system TTF font
  - Falls back to ASCII sanitisation if no TTF font available
  - Handles missing/empty news feed gracefully
"""

import json
import logging
import os
import unicodedata
from datetime import datetime
from pathlib import Path

from fpdf import FPDF, XPos, YPos

log = logging.getLogger(__name__)

BASE_DIR   = Path(__file__).resolve().parent.parent
DATA_DIR   = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
NEWS_FILE  = DATA_DIR / "news_feed.json"
HISTORY_FILE = BASE_DIR / "history.log"

# System TTF font candidates (linux/CI compatible — installed via apt or fonts package)
TTF_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _find_ttf() -> str | None:
    """Return path to the first available Unicode TTF font."""
    for path in TTF_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def _sanitize(text: str) -> str:
    """
    Normalize unicode text to ASCII-safe equivalent.
    Replaces smart punctuation with ASCII equivalents, then strips remaining
    non-Latin-1 characters so fpdf2 core fonts never crash.
    """
    replacements = {
        "\u2013": "-",   # en dash
        "\u2014": "--",  # em dash
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2026": "...", # ellipsis
        "\u00b7": ".",   # middle dot
        "\u2022": "*",   # bullet
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    # Final pass: strip any remaining non-Latin-1
    return unicodedata.normalize("NFKD", text).encode("latin-1", errors="ignore").decode("latin-1")


class ReportPDF(FPDF):
    """NeoSignal intelligence report PDF."""

    def __init__(self, use_unicode_font: bool = False, font_path: str | None = None):
        super().__init__()
        self._unicode = use_unicode_font
        if use_unicode_font and font_path:
            self.add_font("DejaVu", style="", fname=font_path)
            self.add_font("DejaVu", style="B", fname=font_path)
            self._font_name = "DejaVu"
        else:
            self._font_name = "Helvetica"

    def _t(self, text: str) -> str:
        """Return text as-is for unicode fonts, sanitised for core fonts."""
        return text if self._unicode else _sanitize(text)

    def header(self):
        """Page header with report title and timestamp."""
        self.set_font(self._font_name, style="B", size=14)
        self.set_fill_color(15, 15, 35)
        self.set_text_color(255, 255, 255)
        self.cell(
            0, 12,
            self._t(f"NeoSignal  |  AI Intelligence Report  |  {datetime.now().strftime('%Y-%m-%d')}"),
            border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C", fill=True,
        )
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def footer(self):
        """Page number footer."""
        self.set_y(-12)
        self.set_font(self._font_name, size=8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)

    def article_block(self, title: str, url: str, source: str, score: int, date: str):  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Render one article with title, metadata, and URL."""
        # Title
        self.set_font(self._font_name, style="B", size=10)
        self.set_fill_color(240, 244, 255)
        self.multi_cell(
            0, 6, self._t(title),
            border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        # Metadata line
        self.set_font(self._font_name, size=8)
        self.set_text_color(90, 90, 90)
        meta = self._t(f"{source}  |  Score: {score}  |  {date}")
        self.cell(0, 5, meta, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # URL
        self.set_text_color(0, 80, 200)
        self.cell(0, 5, self._t(url[:100]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        self.ln(4)
        # Divider
        self.set_draw_color(200, 200, 220)
        self.line(self.get_x(), self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def summary_block(self, total: int, new: int):
        """Stats summary at top of report."""
        self.set_font(self._font_name, size=9)
        self.set_fill_color(230, 240, 255)
        self.set_draw_color(150, 180, 255)
        self.cell(
            0, 8,
            self._t(f"  {total} articles in feed   |   {new} new this report"),
            border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, fill=True,
        )
        self.ln(5)


def load_history() -> set:
    """Return the set of already-reported article IDs."""
    if HISTORY_FILE.exists():
        return {line.strip() for line in HISTORY_FILE.read_text(encoding="utf-8").splitlines() if line.strip()}
    return set()


def update_history(ids: list[str]) -> None:
    """Append newly reported IDs to history file."""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for item_id in ids:
            f.write(f"{item_id}\n")


def generate_report() -> str | None:
    """
    Generate a PDF report from the latest news feed.
    Returns the PDF path, or None if there's nothing to report.
    """
    if not NEWS_FILE.exists():
        log.error("news_feed.json not found at %s. Run scraper first.", NEWS_FILE)
        return None

    try:
        data = json.loads(NEWS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log.error("Invalid JSON in news_feed.json: %s", exc)
        raise

    # Support both new structured format and legacy flat list
    if isinstance(data, dict):
        articles = data.get("articles", data.get("news_feed", []))
    elif isinstance(data, list):
        articles = data
    else:
        log.error("Unexpected news_feed.json format.")
        return None

    if not articles:
        log.info("No articles in feed — skipping PDF generation.")
        return None

    # Deduplicate against history
    history = load_history()
    new_articles = [a for a in articles if str(a.get("id", a.get("url", ""))) not in history]

    if not new_articles:
        log.info("All %d articles already reported. Nothing new.", len(articles))
        return None

    # Build PDF
    ttf = _find_ttf()
    use_unicode = ttf is not None
    if not use_unicode:
        log.warning("No Unicode TTF font found — falling back to ASCII sanitisation.")

    pdf = ReportPDF(use_unicode_font=use_unicode, font_path=ttf)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.summary_block(len(articles), len(new_articles))

    for article in new_articles:
        pdf.article_block(
            title=article.get("title", "Untitled"),
            url=article.get("url", "N/A"),
            source=article.get("source", "Unknown"),
            score=article.get("score", 0),
            date=article.get("date", "N/A"),
        )

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    pdf_path = REPORTS_DIR / f"neosignal_report_{stamp}.pdf"
    pdf.output(str(pdf_path))

    update_history([str(a.get("id", a.get("url", ""))) for a in new_articles])
    log.info("Report generated: %s  (%d articles)", pdf_path, len(new_articles))
    return str(pdf_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    generate_report()
