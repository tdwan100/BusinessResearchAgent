"""Formatting helpers for UI rendering and markdown export."""

from __future__ import annotations

import re

from schemas.workflow_models import FinalReport

AGENTIC_APPROACH_NOTE = (
    "Our multi-agent AI pipeline gathers, analyzes, and synthesizes company data to produce "
    "these actionable insights."
)


def _bold_percentages(text: str) -> str:
    return re.sub(r"(?<!\*)\b\d{1,3}\s*[–-]\s*\d{1,3}%\b(?!\*)", lambda m: f"**{m.group(0)}**", text)


def to_bulleted_markdown(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return text

    bullet_lines: list[str] = []
    for line in lines:
        cleaned = re.sub(r"^[-*]\s+", "", line)
        bullet_lines.append(f"- {cleaned}")
    return "\n".join(bullet_lines)


def to_markdown(report: FinalReport) -> str:
    sections = [
        ("Executive Summary", report.executive_summary),
        ("Company Overview", report.company_overview),
        ("Products / Services", report.products_services),
        ("Target Market", report.target_market),
        ("Market Positioning", report.market_positioning),
        ("Overlooked Signals / Non-Obvious Insights", report.overlooked_signals),
        ("Current Pain Points", report.likely_operational_bottlenecks),
        ("AI Automation Opportunities", to_bulleted_markdown(report.ai_automation_opportunities)),
        ("90-Day Prioritized AI Roadmap", report.prioritized_ai_roadmap),
        ("Suggested Engagement Angle", report.suggested_engagement_angle),
    ]

    lines = ["# AI Business Workflow Analyst Report", "", f"> {AGENTIC_APPROACH_NOTE}", ""]
    for heading, body in sections:
        lines.extend([f"## {heading}", _bold_percentages(body.strip()), ""])

    lines.extend(
        [
            "## Recommended First Automation Pilot",
            _bold_percentages(to_bulleted_markdown(report.recommended_first_automation_pilot.strip())),
            "",
        ]
    )
    lines.extend(["---", f"*{report.disclaimer.strip()}*"])
    return "\n".join(lines)
