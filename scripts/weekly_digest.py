#!/usr/bin/env python3
# Weekly Digest Generator for AI News Syndicate
# Consolidates, filters, and categorizes top-tier news

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
from fpdf import FPDF

# Constants
HISTORY_LOG_PATH = "history.log"
ARCHIVE_DIR = "archive"

# Categories for Executive Summary
CATEGORIES = {
    "Strategic Shifts": ["strategic", "partnership", "acquisition", "investment"],
    "Model Releases": ["model", "release", "launch", "update"],
    "Regulatory/Security Risks": ["regulation", "security", "risk", "ban", "vulnerability"]
}

# Load history log for the past week
def load_weekly_history():
    if not os.path.exists(HISTORY_LOG_PATH):
        return []
    
    with open(HISTORY_LOG_PATH, "r") as f:
        lines = f.readlines()
    
    # Mock: Assume each line is a JSON string of the article (simplified for demo)
    articles = []
    for line in lines:
        try:
            article = json.loads(line.strip())
            article_date = datetime.strptime(article["date"], "%Y-%m-%d")
            if article_date >= (datetime.now() - timedelta(days=7)):
                articles.append(article)
        except (json.JSONDecodeError, KeyError):
            continue
    
    return articles

# Filter top-tier news (VERIFIED_TRUTH and high impact)
def filter_top_tier(articles):
    top_tier = []
    for article in articles:
        if article.get("tag") == "[VERIFIED_TRUTH]" and any(
            keyword in article["snippet"].lower()
            for category in CATEGORIES.values()
            for keyword in category
        ):
            top_tier.append(article)
    
    # Mock: Sort by impact (simplified for demo)
    return sorted(top_tier, key=lambda x: len(x["snippet"]), reverse=True)[:5]

# Categorize articles
def categorize_articles(articles):
    categorized = defaultdict(list)
    for article in articles:
        for category, keywords in CATEGORIES.items():
            if any(keyword in article["snippet"].lower() for keyword in keywords):
                categorized[category].append(article)
                break
    return categorized

# Generate Executive Summary PDF
class ExecutiveSummaryPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"AI News Weekly Digest - Week {datetime.now().strftime('%Y-%W')}", 0, 1, "C")
        self.ln(10)

    def chapter_title(self, title):
        self.set_font("Arial", "B", 10)
        self.cell(0, 10, title, 0, 1)
        self.ln(5)

    def chapter_body(self, articles):
        self.set_font("Arial", size=8)
        for article in articles:
            self.multi_cell(0, 5, f"• {article['title']} ({article['source']}) - {article['url']}")
        self.ln(5)

# Main function
def generate_weekly_digest():
    # Load and filter articles
    articles = load_weekly_history()
    top_tier = filter_top_tier(articles)
    categorized = categorize_articles(top_tier)
    
    # Generate PDF
n    pdf = ExecutiveSummaryPDF()
    pdf.add_page()
    
    for category, articles in categorized.items():
        pdf.chapter_title(category)
        pdf.chapter_body(articles)
    
    # Save PDF
    week_number = datetime.now().strftime("%Y-%W")
    os.makedirs(f"{ARCHIVE_DIR}/{week_number}", exist_ok=True)
    pdf_path = f"{ARCHIVE_DIR}/{week_number}/weekly_digest_{week_number}.pdf"
    pdf.output(pdf_path)
    
    print(f"Weekly digest generated: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_weekly_digest()