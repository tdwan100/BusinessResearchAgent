from schemas.workflow_models import FinalReport
from utils.report_formatting import to_markdown


def _report() -> FinalReport:
    return FinalReport(
        executive_summary=(
            "Marvin's is a regional building materials retailer.\n"
            "AI can help associates answer questions faster.\n"
            "Start with a focused pilot."
        ),
        company_overview=(
            "Marvin's serves homeowners and contractors.\n"
            "It operates 27 locations across the Southeast.\n"
            "Its brand emphasizes hometown service."
        ),
        products_services="Hardware\nLumber\nPlywood\nPromotions and rewards",
        target_market="Homeowners\nContractors\nLocal communities",
        market_positioning="Service-oriented hometown alternative.\nRegional footprint with local service.",
        overlooked_signals=(
            "Careers content points to training needs.\n"
            "Rewards and promotions create personalization opportunities."
        ),
        likely_operational_bottlenecks=(
            "1. Multi-location service consistency\n"
            "2. Contractor quote complexity\n"
            "3. Broad inventory complexity"
        ),
        ai_automation_opportunities=(
            "1. Location-aware customer and associate assistant\n"
            "2. Contractor quote drafting\n"
            "3. Inventory exception alerts"
        ),
        prioritized_ai_roadmap=(
            "0-30 days: Quick wins and data readiness\n"
            "Build the AI readiness map\n"
            "31-60 days: Customer and contractor pilots\n"
            "Pilot a website project assistant\n"
            "61-90 days: Operational scale pilots\n"
            "Deploy inventory exception alerts"
        ),
        suggested_engagement_angle=(
            "Lead with hometown service amplification.\n"
            "Select 3-5 pilot stores.\n"
            "Validate with store managers."
        ),
        disclaimer="This report uses published data as of 2025. Validate inferred opportunities with stakeholders.",
    )


def test_report_uses_wrapping_tables_without_truncated_cells() -> None:
    markdown = to_markdown(_report())

    assert "…" not in markdown
    assert "| **0-30 days** | Quick wins and **data** readiness | Build the **AI** readiness map |" in markdown
    assert "| **1. Observe** | Multi-location service consistency |" in markdown


def test_signal_strength_uses_words_and_report_is_concise() -> None:
    markdown = to_markdown(_report())

    assert "| **Market clarity** | **Medium** |" in markdown
    assert "Visual Weight" not in markdown
    assert "█" not in markdown
    assert "as of 2026" in markdown
