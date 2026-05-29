"""Formatting helpers for UI rendering and markdown export."""

from __future__ import annotations

import re

from schemas.workflow_models import FinalReport

KEY_TERMS = (
    "AI",
    "automation",
    "workflow",
    "KPI",
    "pilot",
    "governance",
    "risk",
    "data",
    "customer",
    "operational",
)


def _clean_text(value: str) -> str:
    return " ".join(value.strip().split())


def _split_points(value: str, max_items: int = 3) -> list[str]:
    """Split model-generated narrative into compact stakeholder bullets."""
    text = _clean_text(value)
    if not text:
        return []

    candidates = re.split(r"(?:\n+|;|(?<=[.!?])\s+|\s+-\s+)", text)
    points = [candidate.strip(" -*•\t") for candidate in candidates if candidate.strip(" -*•\t")]
    return points[:max_items] or [text]


def _shorten(value: str, max_chars: int = 96) -> str:
    text = _clean_text(value).replace("|", "/")
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip() + "…"


def _bold_keywords(value: str) -> str:
    text = value
    for keyword in KEY_TERMS:
        text = re.sub(rf"\b({re.escape(keyword)})\b", r"**\1**", text, flags=re.IGNORECASE)
    return text


def _dynamic_action_items(report: FinalReport) -> list[str]:
    roadmap_items = _split_points(report.prioritized_ai_roadmap, max_items=2)
    opportunity_items = _split_points(report.ai_automation_opportunities, max_items=1)
    engagement_items = _split_points(report.suggested_engagement_angle, max_items=1)

    actions = [
        f"**Start:** {_bold_keywords(_shorten(item, 120))}" for item in roadmap_items[:1]
    ]
    actions.extend(
        f"**Prioritize:** {_bold_keywords(_shorten(item, 120))}" for item in opportunity_items[:1]
    )
    actions.extend(
        f"**Validate:** {_bold_keywords(_shorten(item, 120))}" for item in engagement_items[:1]
    )
    actions.extend(
        f"**Sequence:** {_bold_keywords(_shorten(item, 120))}" for item in roadmap_items[1:2]
    )
    return actions[:4]


def _opportunity_rows(report: FinalReport) -> list[str]:
    bottlenecks = _split_points(report.likely_operational_bottlenecks, max_items=3)
    opportunities = _split_points(report.ai_automation_opportunities, max_items=3)
    outcomes = _split_points(report.prioritized_ai_roadmap, max_items=3)

    row_count = max(len(bottlenecks), len(opportunities), len(outcomes), 1)
    rows = []
    for index in range(row_count):
        current_state = _shorten(bottlenecks[index] if index < len(bottlenecks) else "Needs validation")
        ai_opportunity = _shorten(opportunities[index] if index < len(opportunities) else "Define AI pilot")
        outcome = _shorten(outcomes[index] if index < len(outcomes) else "Agree measurable KPI")
        rows.append(
            "| "
            f"{index + 1} | {_bold_keywords(current_state)} | {_bold_keywords(ai_opportunity)} | {_bold_keywords(outcome)} |"
        )
    return rows


def _first_point(value: str, fallback: str) -> str:
    return (_split_points(value, max_items=1) or [fallback])[0]


def _process_diagram(report: FinalReport) -> list[str]:
    bottleneck = _shorten(_first_point(report.likely_operational_bottlenecks, "Validate primary workflow friction"), 60)
    opportunity = _shorten(_first_point(report.ai_automation_opportunities, "Define best-fit AI opportunity"), 60)
    roadmap = _shorten(_first_point(report.prioritized_ai_roadmap, "Sequence the first implementation phase"), 60)
    engagement = _shorten(_first_point(report.suggested_engagement_angle, "Confirm with stakeholders"), 60)

    steps = [
        f"Observed friction: {bottleneck}",
        f"AI-enabled response: {opportunity}",
        f"Execution plan: {roadmap}",
        f"Stakeholder validation: {engagement}",
    ]

    diagram = ["```text"]
    for index, step in enumerate(steps):
        diagram.append(step)
        if index < len(steps) - 1:
            diagram.append("        ↓")
    diagram.append("```")
    return diagram


def _timeline_rows(report: FinalReport) -> list[str]:
    phases = _split_points(report.prioritized_ai_roadmap, max_items=3) or [
        "Confirm scope and baseline KPIs",
        "Pilot the highest-value automation opportunity",
        "Harden governance and scale the measured winner",
    ]
    deliverables = _split_points(report.ai_automation_opportunities, max_items=3)
    day_ranges = ["0-30", "31-60", "61-90"]
    labels = ["Phase 1", "Phase 2", "Phase 3"]

    rows = []
    for index, phase in enumerate(phases[:3]):
        focus = _shorten(phase, 86)
        deliverable = _shorten(deliverables[index] if index < len(deliverables) else phase, 86)
        rows.append(
            f"| {labels[index]} | {day_ranges[index]} | {_bold_keywords(focus)} | {_bold_keywords(deliverable)} |"
        )
    return rows


def _signal_scorecard(report: FinalReport) -> list[str]:
    categories = [
        ("Market clarity", report.market_positioning),
        ("Operational pressure", report.likely_operational_bottlenecks),
        ("Automation fit", report.ai_automation_opportunities),
        ("Execution readiness", report.prioritized_ai_roadmap),
    ]
    rows = ["| Dimension | Signal | Visual Weight |", "|---|---|---|"]
    for label, text in categories:
        points = len(_split_points(text, max_items=5))
        bar = "█" * min(max(points + 2, 3), 8)
        rows.append(f"| **{label}** | {_bold_keywords(_shorten(text, 95))} | `{bar}` |")
    return rows


def to_markdown(report: FinalReport) -> str:
    lines = [
        '<h1 style="margin-bottom:0.2rem;">AI Business Workflow Analyst Report</h1>',
        '<p style="color:#6b7280; margin-top:0;">Executive-ready analysis designed for fast decisions.</p>',
        "",
        "## 1) Executive Snapshot",
        _bold_keywords(report.executive_summary.strip()),
        "",
        f"> **Executive Takeaway:** {_bold_keywords(_shorten(_first_point(report.prioritized_ai_roadmap, 'Start with a focused pilot and scale based on KPI evidence.'), 150))}",
        "",
        "### Recommended Action Items",
        *[f"- {action}" for action in _dynamic_action_items(report)],
        "",
        "### Opportunity-at-a-Glance",
        "| # | Current State | AI Opportunity | Business Outcome |",
        "|---:|---|---|---|",
        *_opportunity_rows(report),
        "",
        "### Signal Strength Snapshot",
        *_signal_scorecard(report),
        "",
        "---",
        "## 2) Business Context",
        "### Company Overview",
        _bold_keywords(report.company_overview.strip()),
        "",
        "### Products / Services",
        _bold_keywords(report.products_services.strip()),
        "",
        "### Target Market",
        _bold_keywords(report.target_market.strip()),
        "",
        "### Market Positioning",
        _bold_keywords(report.market_positioning.strip()),
        "",
        "---",
        "## 3) Key Insights & Risk Areas",
        "### Overlooked Signals / Non-Obvious Insights",
        _bold_keywords(report.overlooked_signals.strip()),
        "",
        "### Likely Operational Bottlenecks",
        _bold_keywords(report.likely_operational_bottlenecks.strip()),
        "",
        "---",
        "## 4) AI Opportunity Map",
        _bold_keywords(report.ai_automation_opportunities.strip()),
        "",
        "### Process Diagram (Current → Future)",
        *_process_diagram(report),
        "",
        "---",
        "## 5) 90-Day Implementation Roadmap",
        _bold_keywords(report.prioritized_ai_roadmap.strip()),
        "",
        "### Timeline Chart",
        "| Phase | Day Range | Focus | Key Deliverable |",
        "|---|---:|---|---|",
        *_timeline_rows(report),
        "",
        "---",
        "## 6) Suggested Engagement Angle",
        _bold_keywords(report.suggested_engagement_angle.strip()),
        "",
    ]

    disclaimer = report.disclaimer.strip().replace("as of 2025", "as of 2026")
    lines.extend(["---", f"*{disclaimer}*"])
    return "\n".join(lines)
