"""
NeoSignal PDF Report Generator v3.0

Produces a premium-quality, multi-section PDF intelligence report:
  - Cover page with branding, date, and stats summary
  - Executive summary with source breakdown
  - Articles grouped by authenticity tier (Verified / Confirmed / Emerging)
  - Colour-coded source badges (media vs community)
  - Clean typography with DejaVu Unicode font
  - Page headers and footers with issue number
"""

import json
import logging
import os
import unicodedata
from datetime import datetime
from pathlib import Path

from fpdf import FPDF, XPos, YPos

log = logging.getLogger(__name__)

BASE_DIR     = Path(__file__).resolve().parent.parent
DATA_DIR     = BASE_DIR / "data"
REPORTS_DIR  = BASE_DIR / "reports"
NEWS_FILE    = DATA_DIR / "news_feed.json"
HISTORY_FILE = BASE_DIR / "history.log"

# ── Colour palette (R,G,B) ────────────────────────────────────────────────────
C_DARK       = (10,  18,  40)     # deep navy   - headers
C_ACCENT     = (0,   122, 255)    # signal blue - accents
C_VERIFIED   = (16,  122, 64)     # green       - verified tier
C_CONFIRMED  = (220, 120, 0)      # amber       - confirmed tier
C_EMERGING   = (120, 120, 140)    # slate       - emerging tier
C_MEDIA      = (0,   100, 200)    # blue        - media badge
C_COMMUNITY  = (100, 60,  200)    # purple      - community badge
C_LIGHT_BG   = (245, 247, 252)    # light blue-grey bg
C_DIVIDER    = (210, 215, 230)    # divider lines
C_WHITE      = (255, 255, 255)
C_BODY       = (30,  30,  50)     # body text

TTF_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
]


def _find_font(bold=False):
    """Return path to DejaVuSans or DejaVuSans-Bold TTF if available."""
    for p in TTF_PATHS:
        if bold and "Bold" in p and os.path.exists(p):
            return p
        if not bold and "Bold" not in p and os.path.exists(p):
            return p
    return None


def _sanitize(text):
    """Normalise text: smart punctuation → ASCII, then strip non-Latin-1."""
    for src, dst in {
        "\u2013": "-", "\u2014": "--", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00b7": ".",
        "\u2022": "*", "\u2192": "->", "\u00d7": "x",
    }.items():
        text = text.replace(src, dst)
    return unicodedata.normalize("NFKD", text).encode("latin-1", errors="ignore").decode("latin-1")


def _auth_tier(score):
    """Return (tier_label, colour) for an authenticity score."""
    if score >= 0.8:
        return "VERIFIED",   C_VERIFIED
    if score >= 0.5:
        return "CONFIRMED",  C_CONFIRMED
    return "EMERGING",   C_EMERGING


class NeoSignalPDF(FPDF):
    """Premium NeoSignal intelligence report PDF."""

    def __init__(self, issue_date, article_count, raw_count):
        super().__init__()
        self.issue_date    = issue_date
        self.article_count = article_count
        self.raw_count     = raw_count
        self._fn           = "Helvetica"
        self._unicode      = False
        self._load_fonts()
        self.set_auto_page_break(auto=True, margin=20)

    def _load_fonts(self):
        """Load DejaVu if available for Unicode support."""
        reg = _find_font(bold=False)
        bld = _find_font(bold=True)
        if reg and bld:
            try:
                self.add_font("DejaVu",  style="",  fname=reg)
                self.add_font("DejaVu",  style="B", fname=bld)
                self._fn      = "DejaVu"
                self._unicode = True
                log.info("PDF: DejaVu Unicode font loaded.")
                return
            except Exception as exc:  # pylint: disable=broad-exception-caught
                log.warning("DejaVu load failed: %s — using Helvetica", exc)
        log.warning("PDF: No Unicode TTF found — ASCII sanitisation active.")

    def _t(self, text):
        """Return text unchanged for unicode fonts, sanitised otherwise."""
        return text if self._unicode else _sanitize(str(text))

    def _set(self, r, g, b, fill=False):
        """Convenience: set draw/fill colour."""
        if fill:
            self.set_fill_color(r, g, b)
        else:
            self.set_text_color(r, g, b)

    def header(self):
        """Minimal running header on pages 2+."""
        if self.page_no() == 1:
            return
        self.set_font(self._fn, "B", 7)
        self._set(*C_ACCENT)
        self.cell(0, 6, self._t(f"NeoSignal  |  AI Intelligence Digest  |  {self.issue_date}"),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        self._set(*C_DIVIDER, fill=True)
        self.set_draw_color(*C_DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        self._set(*C_BODY)

    def footer(self):
        """Page number footer."""
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_font(self._fn, size=7)
        self._set(160, 165, 180)
        self.cell(0, 8, self._t(f"NeoSignal Daily Report  ·  {self.issue_date}  ·  Page {self.page_no()}"),
                  align="C")
        self._set(*C_BODY)

    # ── Cover page ────────────────────────────────────────────────────────────

    def cover_page(self, sources_hit, verified, confirmed, emerging):
        """Full-bleed cover page with brand bar, stats, and issue info."""
        self.add_page()

        # Brand bar — full width navy
        self._set(*C_DARK, fill=True)
        self.rect(0, 0, self.w, 52, "F")

        # Logo text
        self.set_xy(14, 10)
        self.set_font(self._fn, "B", 28)
        self._set(*C_WHITE)
        self.cell(0, 12, "NeoSignal", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self.set_x(14)
        self.set_font(self._fn, size=9)
        self._set(160, 195, 255)
        self.cell(0, 7, self._t("AI Intelligence Daily  ·  Multi-Source  ·  Cross-Verified"))

        # Issue info block — right side of brand bar
        self.set_xy(self.w - 70, 14)
        self.set_font(self._fn, "B", 10)
        self._set(*C_WHITE)
        self.cell(60, 6, self._t(self.issue_date), align="R",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_xy(self.w - 70, 22)
        self.set_font(self._fn, size=8)
        self._set(160, 195, 255)
        self.cell(60, 5, self._t(f"{self.article_count} stories  ·  {sources_hit} sources"),
                  align="R")

        # ── Stats cards row ───────────────────────────────────────────────────
        self.set_y(60)
        card_w   = (self.w - 28 - 3 * 4) / 4
        cards    = [
            ("STORIES",   str(self.article_count),  C_ACCENT),
            ("VERIFIED",  str(verified),              C_VERIFIED),
            ("CONFIRMED", str(confirmed),             C_CONFIRMED),
            ("EMERGING",  str(emerging),              C_EMERGING),
        ]
        x = 14
        for label, value, colour in cards:
            self._set(*C_LIGHT_BG, fill=True)
            self.set_draw_color(*colour)
            self.set_line_width(0.8)
            self.rect(x, 60, card_w, 26, "FD")
            # Top colour strip
            self._set(*colour, fill=True)
            self.rect(x, 60, card_w, 3.5, "F")
            # Value
            self.set_xy(x, 66)
            self.set_font(self._fn, "B", 18)
            self._set(*colour)
            self.cell(card_w, 9, value, align="C",
                      new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            # Label
            self.set_x(x)
            self.set_font(self._fn, size=6.5)
            self._set(100, 105, 120)
            self.cell(card_w, 5, label, align="C")
            x += card_w + 4
        self.set_line_width(0.2)

        # ── Pipeline info ─────────────────────────────────────────────────────
        self.set_y(96)
        self.set_font(self._fn, "B", 9)
        self._set(*C_DARK)
        self.cell(0, 7, self._t("How stories are selected"),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font(self._fn, size=8)
        self._set(60, 65, 85)
        steps = [
            "1  Scrape — HackerNews, Reddit (r/artificial, r/MachineLearning, r/singularity, r/LocalLLaMA), "
            "TechCrunch AI, VentureBeat AI, MIT Technology Review, The Verge AI, Wired AI, ArXiv CS.AI",
            "2  Filter — 30+ AI keyword patterns (LLMs, safety, research, tooling, business)",
            "3  Deduplicate — Title similarity matching across all sources (45%+ match = same story)",
            "4  Score — Authenticity = base 0.5 + 0.3 per additional source + diversity bonus + HN score bonus",
            "5  Rank — Highest authenticity first. Stories below 0.25 threshold are dropped.",
        ]
        for step in steps:
            self.multi_cell(0, 5, self._t(step), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(1)

        # ── Legend ────────────────────────────────────────────────────────────
        self.ln(3)
        self._set(*C_DARK)
        self.set_font(self._fn, "B", 9)
        self.cell(0, 7, "Authenticity Tiers",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        legend_items = [
            (C_VERIFIED,  "VERIFIED  (0.8–1.0)",  "Covered by 3+ independent sources including media outlets"),
            (C_CONFIRMED, "CONFIRMED (0.5–0.79)", "Covered by 2 sources or 1 high-quality media source"),
            (C_EMERGING,  "EMERGING  (0.25–0.49)","Single-source but passes AI keyword filter"),
        ]
        for colour, tier, desc in legend_items:
            self._set(*colour, fill=True)
            self.rect(14, self.get_y() + 1, 3.5, 3.5, "F")
            self.set_x(20)
            self.set_font(self._fn, "B", 8)
            self._set(*colour)
            self.cell(28, 5, self._t(tier))
            self.set_font(self._fn, size=8)
            self._set(80, 85, 100)
            self.cell(0, 5, self._t(desc), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Section header ────────────────────────────────────────────────────────

    def section_header(self, title, count, colour):
        """Full-width section header band."""
        self.ln(3)
        self._set(*colour, fill=True)
        self.rect(0, self.get_y(), self.w, 9, "F")
        self.set_font(self._fn, "B", 9)
        self._set(*C_WHITE)
        self.cell(0, 9, self._t(f"  {title.upper()}  ({count} stories)"),
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self._set(*C_BODY)
        self.ln(2)

    # ── Article card ──────────────────────────────────────────────────────────

    def article_card(self, article, index):  # pylint: disable=too-many-statements
        """Render one article card with all metadata."""
        tier_label, tier_colour = _auth_tier(article.get("authenticity_score", 0))
        source_type  = article.get("source_type", "media")
        badge_colour = C_MEDIA if source_type == "media" else C_COMMUNITY
        n_sources    = article.get("source_count", 1)
        score        = article.get("score", 0)
        auth         = article.get("authenticity_score", 0)

        # Card background
        bg = C_LIGHT_BG if index % 2 == 0 else C_WHITE
        card_y = self.get_y()
        card_h = 28 if len(article.get("title", "")) < 80 else 33

        self._set(*bg, fill=True)
        self.set_draw_color(*C_DIVIDER)
        self.rect(12, card_y, self.w - 24, card_h, "FD")

        # Left authenticity stripe
        self._set(*tier_colour, fill=True)
        self.rect(12, card_y, 2.5, card_h, "F")

        # Index number
        self.set_xy(16, card_y + 2)
        self.set_font(self._fn, "B", 7)
        self._set(150, 155, 170)
        self.cell(8, 4, str(index))

        # Title
        self.set_xy(24, card_y + 2)
        self.set_font(self._fn, "B", 9)
        self._set(*C_DARK)
        title = article.get("title", "Untitled")
        if len(title) > 120:
            title = title[:117] + "..."
        self.multi_cell(self.w - 50, 5, self._t(title),
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Source badge
        meta_y = card_y + card_h - 9
        self.set_xy(24, meta_y)
        self._set(*badge_colour, fill=True)
        self.set_font(self._fn, "B", 6.5)
        self._set(*C_WHITE)
        badge_text = self._t(article.get("source", "?"))[:28]
        badge_w = self.get_string_width(badge_text) + 4
        self.rect(24, meta_y, badge_w, 5, "F")
        self.cell(badge_w, 5, badge_text)

        # Cross-source count
        if n_sources > 1:
            self.set_x(24 + badge_w + 3)
            self.set_font(self._fn, size=6.5)
            self._set(*tier_colour)
            self.cell(0, 5, self._t(f"+{n_sources - 1} other source{'s' if n_sources > 2 else ''}"))

        # Auth score pill (right side)
        pill_x = self.w - 48
        self.set_xy(pill_x, meta_y)
        self._set(*tier_colour, fill=True)
        self.rect(pill_x, meta_y, 18, 5, "F")
        self.set_font(self._fn, "B", 6)
        self._set(*C_WHITE)
        self.cell(18, 5, self._t(f"{tier_label[:4]}  {auth:.0%}"), align="C")

        # HN score if notable
        if score > 0:
            self.set_x(pill_x + 20)
            self.set_font(self._fn, size=6.5)
            self._set(130, 135, 150)
            self.cell(0, 5, self._t(f"HN: {score}"))

        # URL
        self.set_xy(24, meta_y + 5.5)
        self.set_font(self._fn, size=6.5)
        self._set(*C_ACCENT)
        url = article.get("url", "")
        if len(url) > 90:
            url = url[:87] + "..."
        self.cell(0, 4, self._t(url), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        self._set(*C_BODY)
        self.set_y(card_y + card_h + 2)

    # ── Source breakdown table ────────────────────────────────────────────────

    def source_breakdown(self, articles):
        """Mini table showing how many articles came from each source."""
        from collections import Counter  # pylint: disable=import-outside-toplevel
        counts = Counter(
            src for a in articles for src in a.get("all_sources", [a.get("source", "?")])
        )
        self.add_page()
        self.set_font(self._fn, "B", 11)
        self._set(*C_DARK)
        self.cell(0, 8, "Source Breakdown", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*C_DIVIDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

        col_w = [100, 30, 50]
        hdrs  = ["Source", "Stories", "Type"]
        self.set_font(self._fn, "B", 8)
        self._set(*C_DARK, fill=True)
        self._set(*C_LIGHT_BG, fill=True)
        for i, hdr in enumerate(hdrs):
            self.cell(col_w[i], 7, hdr, border=1, fill=True)
        self.ln()

        self.set_font(self._fn, size=8)
        alt = False
        for source, cnt in sorted(counts.items(), key=lambda x: -x[1]):
            bg = C_LIGHT_BG if alt else C_WHITE
            self._set(*bg, fill=True)
            src_type = "Community" if "Reddit" in source or source == "HackerNews" else "Media"
            colour   = C_COMMUNITY if src_type == "Community" else C_MEDIA
            self._set(*C_BODY)
            self.cell(col_w[0], 6, self._t(source), border=1, fill=True)
            self._set(*colour)
            self.cell(col_w[1], 6, str(cnt), border=1, fill=True, align="C")
            self._set(*C_BODY)
            self.cell(col_w[2], 6, src_type, border=1, fill=True)
            self.ln()
            alt = not alt

        self._set(*C_BODY)


# ── History / deduplication ───────────────────────────────────────────────────

def load_history():
    """Return set of already-reported article IDs."""
    if HISTORY_FILE.exists():
        return {l.strip() for l in HISTORY_FILE.read_text(encoding="utf-8").splitlines() if l.strip()}
    return set()


def update_history(ids):
    """Append newly reported article IDs."""
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        for item_id in ids:
            f.write(f"{item_id}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def generate_report():
    """
    Generate the premium PDF report. Returns PDF path or None.
    """
    if not NEWS_FILE.exists():
        log.error("news_feed.json missing — run scraper first.")
        return None
    try:
        data = json.loads(NEWS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log.error("Bad JSON: %s", exc)
        raise

    articles = data.get("articles", []) if isinstance(data, dict) else data
    raw_count = data.get("meta", {}).get("raw_count", len(articles)) if isinstance(data, dict) else len(articles)

    if not articles:
        log.info("No articles — skipping PDF.")
        return None

    history = load_history()
    new_articles = [a for a in articles if a.get("id", a.get("url", "")) not in history]
    if not new_articles:
        log.info("All %d articles already reported.", len(articles))
        # Re-use all articles so CI always produces a PDF for email
        new_articles = articles

    # Tier counts
    verified  = sum(1 for a in new_articles if a.get("authenticity_score", 0) >= 0.8)
    confirmed = sum(1 for a in new_articles if 0.5 <= a.get("authenticity_score", 0) < 0.8)
    emerging  = sum(1 for a in new_articles if a.get("authenticity_score", 0) < 0.5)
    sources_hit = len({s for a in new_articles for s in a.get("all_sources", [a.get("source", "")])})

    issue_date = datetime.now().strftime("%d %B %Y")
    pdf = NeoSignalPDF(
        issue_date=issue_date,
        article_count=len(new_articles),
        raw_count=raw_count,
    )

    # Cover page
    pdf.cover_page(sources_hit, verified, confirmed, emerging)

    # Source breakdown
    pdf.source_breakdown(new_articles)

    # Articles — sorted into tiers
    tiers = [
        ("Verified Intelligence", [a for a in new_articles if a.get("authenticity_score", 0) >= 0.8], C_VERIFIED),
        ("Confirmed Signals",     [a for a in new_articles if 0.5 <= a.get("authenticity_score", 0) < 0.8], C_CONFIRMED),
        ("Emerging Signals",      [a for a in new_articles if a.get("authenticity_score", 0) < 0.5], C_EMERGING),
    ]
    pdf.add_page()
    idx = 1
    for tier_name, tier_articles, colour in tiers:
        if not tier_articles:
            continue
        pdf.section_header(tier_name, len(tier_articles), colour)
        for article in tier_articles:
            pdf.article_card(article, idx)
            idx += 1

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp    = datetime.now().strftime("%Y%m%d_%H%M")
    pdf_path = REPORTS_DIR / f"neosignal_{stamp}.pdf"
    pdf.output(str(pdf_path))

    update_history([a.get("id", a.get("url", "")) for a in new_articles])
    log.info("Report: %s  (%d articles, %d verified)", pdf_path, len(new_articles), verified)
    return str(pdf_path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    generate_report()
