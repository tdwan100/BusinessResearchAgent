"""Minimal website fetching and processing utilities."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "Mozilla/5.0 (compatible; AI-Business-Workflow-Analyst/1.0; +https://example.local)"
)


@dataclass
class WebPage:
    url: str
    title: str
    text: str


class WebsiteFetcher:
    """Fetches a website and linked pages with defensive defaults."""

    def __init__(self, timeout: int = 12, max_chars: int = 30000) -> None:
        self.timeout = timeout
        self.max_chars = max_chars

    def fetch_html(self, url: str) -> str:
        response = requests.get(
            url,
            timeout=self.timeout,
            headers={"User-Agent": USER_AGENT},
        )
        response.raise_for_status()
        return response.text

    def scrape_page(self, url: str) -> WebPage:
        html = self.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        title = (soup.title.string or "Untitled").strip() if soup.title else "Untitled"

        for script in soup(["script", "style", "noscript"]):
            script.extract()

        text = " ".join(soup.get_text(separator=" ").split())
        if len(text) > self.max_chars:
            text = text[: self.max_chars] + " ..."

        return WebPage(url=url, title=title, text=text)


class PageSelector:
    """Selects likely high-signal pages from homepage links."""

    PRIORITY_TOKENS = (
        "about",
        "company",
        "services",
        "solutions",
        "products",
        "platform",
        "industries",
        "customers",
    )

    def extract_priority_urls(self, homepage_html: str, base_url: str, max_pages: int = 5) -> list[str]:
        soup = BeautifulSoup(homepage_html, "html.parser")
        base_domain = urlparse(base_url).netloc

        candidates: list[str] = []
        for anchor in soup.find_all("a", href=True):
            absolute = urljoin(base_url, anchor["href"])
            parsed = urlparse(absolute)
            if not parsed.scheme.startswith("http") or parsed.netloc != base_domain:
                continue

            path = parsed.path.lower()
            if any(token in path for token in self.PRIORITY_TOKENS):
                candidates.append(absolute.split("#")[0])

        deduped = []
        seen = set()
        for url in candidates:
            if url not in seen:
                seen.add(url)
                deduped.append(url)
            if len(deduped) >= max_pages:
                break

        return deduped


class TextCleaner:
    """Simple text clean-up helper to reduce prompt noise."""

    def clean(self, text: str, max_chars: int = 12000) -> str:
        normalized = " ".join(text.split())
        return normalized[:max_chars]
