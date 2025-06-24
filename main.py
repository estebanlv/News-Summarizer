#!/usr/bin/env python
"""
Example:
    python main.py https://techcrunch.com -n 5 -o digest.md
"""
import os
import argparse
from pathlib import Path

from src.config import Settings
from src.tools.firecrawl_client import FireCrawlClient
from src.tools.summarizer import Summarizer
from src.agents.news_agent import run_news_report

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a news digest.")
    parser.add_argument("source_url", help="Homepage of the news site")
    parser.add_argument("-n", "--limit", type=int, default=None, help="Number of headlines")
    parser.add_argument("-o", "--output", help="Write markdown to this file")
    args = parser.parse_args()

    # Load configuration (from .env or environment)
    cfg = Settings()

    limit = args.limit or cfg.default_limit

    fc = FireCrawlClient(cfg.firecrawl_api_key)
    sz = Summarizer(cfg.gemini_api_key, cfg.gemini_model)

    # run_news_report returns a CrewOutput; cast to str for I/O
    report_obj = run_news_report(args.source_url, limit, fc, sz)
    markdown_report = str(report_obj)

    if args.output:
        Path(args.output).write_text(markdown_report, encoding="utf-8")
        print(f"Written digest to {args.output}")
    else:
        print(markdown_report)


if __name__ == "__main__":
    main()
