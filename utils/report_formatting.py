"""Formatting helpers for UI rendering and markdown export."""

from __future__ import annotations

from schemas.workflow_models import FinalReport

RECOMMENDED_PILOT_SECTION = """## Recommended First Automation Pilot

Workflow: Employment Verification Document Generation

Current State:
Verification documents are manually created and customized for each client, leading to inconsistencies and significant time investment.

Proposed System:
Develop an AI-assisted document generation pipeline that:

- takes structured user inputs (role, company, timeline)
- generates standardized verification documents
- enforces formatting and consistency rules
- logs outputs for internal review and quality control

Expected Impact:

- Reduce manual effort by ~60–80%
- Improve consistency and quality of outputs
- Enable higher client throughput without proportional staffing increases

Why This First:
This workflow is repetitive, high-frequency, and central to the company’s service offering, making it the highest-leverage starting point for automation.
"""


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
        ("Recommended Pilot (Company-Specific)", report.recommended_first_automation_pilot),
        ("90-Day Prioritized AI Roadmap", report.prioritized_ai_roadmap),
        ("Suggested Engagement Angle", report.suggested_engagement_angle),
    ]

    lines = ["# AI Business Workflow Analyst Report", ""]
    for heading, body in sections:
        lines.extend([f"## {heading}", body.strip(), ""])

    lines.extend([RECOMMENDED_PILOT_SECTION.strip(), ""])
    lines.extend(["---", f"*{report.disclaimer.strip()}*"])
    return "\n".join(lines)
