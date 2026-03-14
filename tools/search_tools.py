"""Optional lightweight search enrichment placeholder."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SearchSnippet:
    title: str
    url: str
    snippet: str


class SearchEnricher:
    """Safe no-op enricher used when no search provider is configured."""

    def enrich(self, company_name: str, industry_context: str | None = None) -> list[SearchSnippet]:
        context = industry_context or ""
        synthesized = (
            f"Public market signals for {company_name} {context}. "
            "No external search provider configured, so this enrichment is limited."
        )
        return [
            SearchSnippet(
                title=f"Context note for {company_name}",
                url="about:blank",
                snippet=synthesized,
            )
        ]
