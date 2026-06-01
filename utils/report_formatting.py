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


def _strip_list_prefix(value: str) -> str:
    return re.sub(r"^\s*(?:[-*•]+|\d+[.)])\s*", "", value).strip()


def _is_noise_point(value: str) -> bool:
    text = _strip_list_prefix(value).strip()
    if not text or re.fullmatch(r"\d+\.?", text):
        return True

    lowered = text.lower().rstrip(":")
    noisy_labels = {
        "action items",
        "best fit",
        "best fit categories",
        "expected kpi impact",
        "human control",
        "inferred service role",
        "key uncertainty",
        "kpi impact to track",
        "primary markets stated on the website",
        "strategic implication",
        "suggested first conversation",
        "what it does",
        "why it matters",
        "why this angle fits",
    }
    return lowered in noisy_labels or any(lowered.startswith(f"{label}:") for label in noisy_labels)


def _clean_point(value: str) -> str:
    text = _strip_list_prefix(value)
    text = re.sub(r"\s+", " ", text).strip(" -*•\t")
    return text


def _content_lines(value: str) -> list[str]:
    lines = []
    for raw_line in value.replace("\r\n", "\n").split("\n"):
        line = _clean_point(raw_line)
        if not _is_noise_point(line):
            lines.append(line)
    return lines


def _split_points(value: str, max_items: int = 3) -> list[str]:
    """Split model-generated narrative into compact stakeholder bullets without keeping list numbers."""
    numbered_items = []
    for raw_line in value.replace("\r\n", "\n").split("\n"):
        match = re.match(r"^\s*\d+[.)]\s+(.+)$", raw_line.strip())
        if match:
            point = _clean_point(match.group(1))
            if point and not _is_noise_point(point):
                numbered_items.append(point)
    if numbered_items:
        return numbered_items[:max_items]

    lines = _content_lines(value)
    if lines:
        return lines[:max_items]

    text = _clean_text(value)
    if not text:
        return []

    candidates = re.split(r"(?:;|(?<=[.!?])\s+(?=[A-Z]))", text)
    points = [_clean_point(candidate) for candidate in candidates]
    return [point for point in points if point and not _is_noise_point(point)][:max_items]


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
    roadmap_items = _split_points(report.prioritized_ai_roadmap, max_items=4)
    opportunity_items = _split_points(report.ai_automation_opportunities, max_items=2)
    engagement_items = _split_points(report.suggested_engagement_angle, max_items=1)

    raw_actions = [
        ("Start", roadmap_items[0] if roadmap_items else "Confirm scope and baseline KPIs"),
        ("Prioritize", opportunity_items[0] if opportunity_items else "Select one high-value AI pilot"),
        ("Validate", engagement_items[0] if engagement_items else "Validate with internal stakeholders"),
        ("Sequence", roadmap_items[1] if len(roadmap_items) > 1 else "Move from pilot to governed rollout"),
    ]
    return [f"**{label}:** {_bold_keywords(_shorten(text, 120))}" for label, text in raw_actions]


def _opportunity_rows(report: FinalReport) -> list[str]:
    bottlenecks = _split_points(report.likely_operational_bottlenecks, max_items=3)
    opportunities = _split_points(report.ai_automation_opportunities, max_items=3)
    outcomes = _roadmap_phase_labels(report)

    row_count = max(len(bottlenecks), len(opportunities), len(outcomes), 1)
    rows = []
    for index in range(min(row_count, 3)):
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
    bottleneck = _shorten(_first_point(report.likely_operational_bottlenecks, "Validate primary workflow friction"), 70)
    opportunity = _shorten(_first_point(report.ai_automation_opportunities, "Define best-fit AI opportunity"), 70)
    roadmap = _shorten(_first_roadmap_deliverable(report), 70)
    engagement = _shorten(_first_point(report.suggested_engagement_angle, "Confirm with stakeholders"), 70)

    steps = [
        f"Observed friction: {bottleneck}",
        f"AI-enabled response: {opportunity}",
        f"First execution step: {roadmap}",
        f"Validation loop: {engagement}",
    ]

    diagram = ["```text"]
    for index, step in enumerate(steps):
        diagram.append(step)
        if index < len(steps) - 1:
            diagram.append("        ↓")
    diagram.append("```")
    return diagram


def _roadmap_phase_labels(report: FinalReport) -> list[str]:
    phases = []
    for line in _content_lines(report.prioritized_ai_roadmap):
        if re.match(r"^\d+\s*-\s*\d+\s+days?:", line, flags=re.IGNORECASE):
            phases.append(line)
    return phases[:3] or _split_points(report.prioritized_ai_roadmap, max_items=3)


def _roadmap_deliverables(report: FinalReport) -> list[str]:
    deliverables = []
    phase_seen = False
    for line in _content_lines(report.prioritized_ai_roadmap):
        if re.match(r"^\d+\s*-\s*\d+\s+days?:", line, flags=re.IGNORECASE):
            phase_seen = True
            continue
        if phase_seen and not line.lower().startswith(("action items:", "expected kpi impact:")):
            deliverables.append(line)
            phase_seen = False
    return deliverables[:3]


def _first_roadmap_deliverable(report: FinalReport) -> str:
    deliverables = _roadmap_deliverables(report)
    if deliverables:
        return deliverables[0]
    return _first_point(report.prioritized_ai_roadmap, "Confirm scope and baseline KPIs")


def _timeline_rows(report: FinalReport) -> list[str]:
    phases = _roadmap_phase_labels(report) or [
        "0-30 days: Confirm scope and baseline KPIs",
        "31-60 days: Pilot the highest-value automation opportunity",
        "61-90 days: Harden governance and scale the measured winner",
    ]
    deliverables = _roadmap_deliverables(report)
    opportunities = _split_points(report.ai_automation_opportunities, max_items=3)
    day_ranges = ["0-30", "31-60", "61-90"]
    labels = ["Phase 1", "Phase 2", "Phase 3"]

    rows = []
    for index, phase in enumerate(phases[:3]):
        focus = re.sub(r"^\d+\s*-\s*\d+\s+days?:\s*", "", phase, flags=re.IGNORECASE)
        deliverable = deliverables[index] if index < len(deliverables) else (
            opportunities[index] if index < len(opportunities) else focus
        )
        rows.append(
            f"| {labels[index]} | {day_ranges[index]} | {_bold_keywords(_shorten(focus, 72))} | {_bold_keywords(_shorten(deliverable, 86))} |"
        )
    return rows


def _decision_snapshot(report: FinalReport) -> list[str]:
    categories = [
        ("Market read", report.market_positioning),
        ("Main friction", report.likely_operational_bottlenecks),
        ("Best first AI move", report.ai_automation_opportunities),
        ("Near-term plan", report.prioritized_ai_roadmap),
    ]
    rows = ["| Lens | Clean Readout |", "|---|---|"]
    for label, text in categories:
        rows.append(f"| **{label}** | {_bold_keywords(_shorten(_first_point(text, 'Validate with stakeholders'), 120))} |")
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
        "### Decision Snapshot",
        *_decision_snapshot(report),
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
