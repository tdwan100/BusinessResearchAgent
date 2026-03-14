"""Pydantic models for structured data passed between workflow stages."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ResearchOutput(BaseModel):
    company_name: str = Field(..., description="Company legal or brand name")
    website_url: str = Field(..., description="Primary website analyzed")
    business_snapshot: str = Field(..., description="Concise understanding of the company")
    notable_facts: list[str] = Field(
        default_factory=list,
        description="Grounded facts observed from website content",
    )
    evidence_pages: list[str] = Field(
        default_factory=list,
        description="Website page URLs used for evidence",
    )
    confidence_notes: str = Field(
        ...,
        description="Caveats and confidence level based on available information",
    )


class OfferingMarketOutput(BaseModel):
    products_services: list[str] = Field(
        default_factory=list,
        description="Primary offerings described in business-friendly language",
    )
    target_market: list[str] = Field(
        default_factory=list,
        description="Likely buyer segments, industries, and personas",
    )
    market_positioning: str = Field(
        ...,
        description="How the company appears to position itself in the market",
    )
    commercial_model: str = Field(
        ...,
        description="Likely commercial model (e.g., subscription, services, hybrid)",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Inferences with uncertainty language",
    )


class OpportunityOutput(BaseModel):
    operational_bottlenecks: list[str] = Field(
        default_factory=list,
        description="Likely friction points that impact efficiency or growth",
    )
    ai_automation_opportunities: list[str] = Field(
        default_factory=list,
        description="Concrete AI opportunities mapped to bottlenecks",
    )
    expected_business_impact: list[str] = Field(
        default_factory=list,
        description="Likely measurable outcomes and KPIs",
    )
    risk_considerations: list[str] = Field(
        default_factory=list,
        description="Execution and data-risk considerations",
    )


class FinalReport(BaseModel):
    executive_summary: str
    company_overview: str
    products_services: str
    target_market: str
    market_positioning: str
    likely_operational_bottlenecks: str
    ai_automation_opportunities: str
    suggested_engagement_angle: str
    disclaimer: str
