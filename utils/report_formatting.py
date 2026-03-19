"""Formatting helpers for UI rendering and markdown export."""

from __future__ import annotations

from schemas.workflow_models import FinalReport


def to_markdown(report: FinalReport) -> str:
    sections = [
        ("Executive Summary", report.executive_summary),
        ("Company Overview", report.company_overview),
        ("Products / Services", report.products_services),
        ("Target Market", report.target_market),
        ("Market Positioning", report.market_positioning),
        ("Overlooked Signals / Non-Obvious Insights", report.overlooked_signals),
        ("Likely Operational Bottlenecks", report.likely_operational_bottlenecks),
        ("AI Automation Opportunities", report.ai_automation_opportunities),
        ("90-Day Prioritized AI Roadmap", report.prioritized_ai_roadmap),
        ("Suggested Engagement Angle", report.suggested_engagement_angle),
    ]

    lines = ["# AI Business Workflow Analyst Report", ""]
    for heading, body in sections:
        lines.extend([f"## {heading}", body.strip(), ""])

    lines.extend(["---", f"*{report.disclaimer.strip()}*"])
    return "\n".join(lines)
