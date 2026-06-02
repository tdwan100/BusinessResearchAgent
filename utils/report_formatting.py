"""Formatting helpers for concise UI rendering and markdown export."""

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

NOISE_LABELS = {
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


def _clean_text(value: str) -> str:
    return " ".join(value.strip().split())


def _strip_list_prefix(value: str) -> str:
    return re.sub(r"^\s*(?:[-*•]+|\d+[.)])\s*", "", value).strip()


def _clean_point(value: str) -> str:
    return re.sub(r"\s+", " ", _strip_list_prefix(value)).strip(" -*•\t")


def _is_noise_point(value: str) -> bool:
    text = _clean_point(value)
    if not text or re.fullmatch(r"\d+\.?", text):
        return True
    lowered = text.lower().rstrip(":")
    return lowered in NOISE_LABELS or any(lowered.startswith(f"{label}:") for label in NOISE_LABELS)


def _content_lines(value: str) -> list[str]:
    lines = []
    for raw_line in value.replace("\r\n", "\n").split("\n"):
        line = _clean_point(raw_line)
        if line and not _is_noise_point(line):
            lines.append(line)
    return lines


def _split_points(value: str, max_items: int = 3) -> list[str]:
    """Return clean, concise points from model-generated narrative."""
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
    if len(lines) > 1:
        return lines[:max_items]

    text = _clean_text(value)
    if not text:
        return []
    candidates = re.split(r"(?:;|(?<=[.!?])\s+(?=[A-Z]))", text)
    points = [_clean_point(candidate) for candidate in candidates]
    return [point for point in points if point and not _is_noise_point(point)][:max_items]


def _first_point(value: str, fallback: str) -> str:
    return (_split_points(value, max_items=1) or [fallback])[0]


def _bold_keywords(value: str) -> str:
    text = value
    for keyword in KEY_TERMS:
        text = re.sub(rf"\b({re.escape(keyword)})\b", r"**\1**", text, flags=re.IGNORECASE)
    return text


def _bullet_lines(value: str, max_items: int = 3) -> list[str]:
    points = _split_points(value, max_items=max_items)
    return [f"- {_bold_keywords(point)}" for point in points]


def _roadmap_phase_labels(report: FinalReport) -> list[str]:
    phases = []
    for line in _content_lines(report.prioritized_ai_roadmap):
        if re.match(r"^\d+\s*-\s*\d+\s+days?:", line, flags=re.IGNORECASE):
            phases.append(line)
    return phases[:3]


def _roadmap_deliverables(report: FinalReport) -> list[str]:
    deliverables = []
    phase_seen = False
    for line in _content_lines(report.prioritized_ai_roadmap):
        if re.match(r"^\d+\s*-\s*\d+\s+days?:", line, flags=re.IGNORECASE):
            phase_seen = True
            continue
        if phase_seen:
            deliverables.append(line)
            phase_seen = False
    return deliverables[:3]


def _dynamic_action_items(report: FinalReport) -> list[str]:
    roadmap = _roadmap_deliverables(report) or _split_points(report.prioritized_ai_roadmap, max_items=2)
    opportunities = _split_points(report.ai_automation_opportunities, max_items=1)
    engagement = _split_points(report.suggested_engagement_angle, max_items=1)
    actions = [
        ("Start", roadmap[0] if roadmap else "Confirm scope and baseline KPIs"),
        ("Prioritize", opportunities[0] if opportunities else "Select one high-value AI pilot"),
        ("Validate", engagement[0] if engagement else "Validate the pilot with internal stakeholders"),
    ]
    return [f"- **{label}:** {_bold_keywords(text)}" for label, text in actions]


def _opportunity_rows(report: FinalReport) -> list[str]:
    bottlenecks = _split_points(report.likely_operational_bottlenecks, max_items=3)
    opportunities = _split_points(report.ai_automation_opportunities, max_items=3)
    phases = _roadmap_phase_labels(report)
    rows = []
    for index in range(3):
        bottleneck = bottlenecks[index] if index < len(bottlenecks) else "Validate next bottleneck"
        opportunity = opportunities[index] if index < len(opportunities) else "Define the matching AI pilot"
        phase = phases[index] if index < len(phases) else "Sequence after validation"
        rows.append(f"| {index + 1} | {_bold_keywords(bottleneck)} | {_bold_keywords(opportunity)} | {_bold_keywords(phase)} |")
    return rows


def _process_rows(report: FinalReport) -> list[str]:
    steps = [
        ("1. Observe", _first_point(report.likely_operational_bottlenecks, "Validate primary workflow friction")),
        ("2. Assist", _first_point(report.ai_automation_opportunities, "Define best-fit AI opportunity")),
        ("3. Pilot", (_roadmap_deliverables(report) or ["Confirm scope and baseline KPIs"])[0]),
        ("4. Validate", _first_point(report.suggested_engagement_angle, "Review results with stakeholders")),
    ]
    return [f"| **{stage}** | {_bold_keywords(detail)} |" for stage, detail in steps]


def _timeline_rows(report: FinalReport) -> list[str]:
    phases = _roadmap_phase_labels(report) or [
        "0-30 days: Confirm scope and baseline KPIs",
        "31-60 days: Pilot the highest-value automation opportunity",
        "61-90 days: Harden governance and scale the measured winner",
    ]
    deliverables = _roadmap_deliverables(report)
    opportunities = _split_points(report.ai_automation_opportunities, max_items=3)
    day_ranges = ["0-30", "31-60", "61-90"]

    rows = []
    for index, phase in enumerate(phases[:3]):
        focus = re.sub(r"^\d+\s*-\s*\d+\s+days?:\s*", "", phase, flags=re.IGNORECASE)
        deliverable = deliverables[index] if index < len(deliverables) else (
            opportunities[index] if index < len(opportunities) else focus
        )
        rows.append(f"| **{day_ranges[index]} days** | {_bold_keywords(focus)} | {_bold_keywords(deliverable)} |")
    return rows


def _strength_label(value: str) -> str:
    signal_count = len(_content_lines(value))
    if signal_count >= 4:
        return "High"
    if signal_count >= 2:
        return "Medium"
    return "Low"


def _signal_strength_rows(report: FinalReport) -> list[str]:
    categories = [
        ("Market clarity", report.market_positioning),
        ("Operational pressure", report.likely_operational_bottlenecks),
        ("Automation fit", report.ai_automation_opportunities),
        ("Execution readiness", report.prioritized_ai_roadmap),
    ]
    return [
        f"| **{label}** | **{_strength_label(text)}** | {_bold_keywords(_first_point(text, 'Validate with stakeholders'))} |"
        for label, text in categories
    ]


def _concise_disclaimer(value: str) -> str:
    normalized = value.strip().replace("as of 2025", "as of 2026")
    return " ".join(_split_points(normalized, max_items=2)) or normalized


def to_markdown(report: FinalReport) -> str:
    """Render an executive-ready report with concise, wrapping markdown tables."""
    lines = [
        '<h1 style="margin-bottom:0.2rem;">AI Business Workflow Analyst Report</h1>',
        '<p style="color:#6b7280; margin-top:0;">Concise decision brief for business stakeholders.</p>',
        "",
        "## 1) Executive Snapshot",
        *_bullet_lines(report.executive_summary, max_items=3),
        "",
        "### Recommended Actions",
        *_dynamic_action_items(report),
        "",
        "### Opportunity-at-a-Glance",
        "| # | Current Friction | AI Opportunity | Roadmap Phase |",
        "|---:|---|---|---|",
        *_opportunity_rows(report),
        "",
        "### Signal Strength Snapshot",
        "| Dimension | Strength | Supporting Signal |",
        "|---|---|---|",
        *_signal_strength_rows(report),
        "",
        "> **How to read this:** Strength reflects the amount of public evidence available, not business performance.",
        "",
        "---",
        "## 2) Business Context",
        "### Company Overview",
        *_bullet_lines(report.company_overview, max_items=3),
        "",
        "### Products / Services",
        *_bullet_lines(report.products_services, max_items=4),
        "",
        "### Target Market",
        *_bullet_lines(report.target_market, max_items=4),
        "",
        "### Market Positioning",
        *_bullet_lines(report.market_positioning, max_items=3),
        "",
        "---",
        "## 3) Key Insights & Risk Areas",
        "### Overlooked Signals",
        *_bullet_lines(report.overlooked_signals, max_items=4),
        "",
        "### Likely Operational Bottlenecks",
        *_bullet_lines(report.likely_operational_bottlenecks, max_items=4),
        "",
        "---",
        "## 4) AI Opportunity Map",
        *_bullet_lines(report.ai_automation_opportunities, max_items=5),
        "",
        "### Process Flow",
        "| Step | Focus |",
        "|---|---|",
        *_process_rows(report),
        "",
        "---",
        "## 5) 90-Day Roadmap",
        "| Timing | Focus | Key Deliverable |",
        "|---|---|---|",
        *_timeline_rows(report),
        "",
        "---",
        "## 6) Suggested Engagement Angle",
        *_bullet_lines(report.suggested_engagement_angle, max_items=4),
        "",
        "---",
        f"*{_concise_disclaimer(report.disclaimer)}*",
    ]
    return "\n".join(lines)
