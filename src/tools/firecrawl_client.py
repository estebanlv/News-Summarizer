# src/tools/firecrawl_client.py
from firecrawl import FirecrawlApp
from typing import List

class FireCrawlClient:
    """Thin wrapper around the Firecrawl SDK."""

    def __init__(self, api_key: str) -> None:
        self.app = FirecrawlApp(api_key=api_key)

    def fetch_top_headlines(self, source_url: str, limit: int = 5) -> List[str]:
        """
        Scrape the front page and return up to *limit* distinct article URLs.

        Firecrawl returns `links` automatically when we request the `links`
        format, so no extra HTML parsing is required.
        """
        resp = self.app.scrape_url(source_url, params={"formats": ["links"]})
        links = resp.get("links", [])
        # Keep unique, fully-qualified links
        seen, cleaned = set(), []
        for link in links:
            if link.startswith("http") and link not in seen:
                seen.add(link)
                cleaned.append(link)
            if len(cleaned) >= limit:
                break
        return cleaned

    def fetch_article_body(self, url: str) -> str:
        """Return markdown for a single article."""
        data = self.app.scrape_url(url, params={"formats": ["markdown"]})
        return data.get("markdown", "")
