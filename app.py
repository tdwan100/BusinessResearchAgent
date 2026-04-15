"""Streamlit app for AI Business Workflow Analyst."""

from __future__ import annotations

import re

import streamlit as st

from services.workflow_service import WorkflowService
from schemas.workflow_models import FinalReport
from utils.config import load_runtime_config, missing_api_key_message
from utils.report_formatting import RECOMMENDED_PILOT_SECTION, to_markdown


st.set_page_config(
    page_title="AI Business Workflow Analyst",
    page_icon="📊",
    layout="wide",
)


def _valid_url(url: str) -> bool:
    return bool(re.match(r"^https?://", url.strip()))


def render_report(report: FinalReport) -> None:
    st.markdown(
        """
        <style>
        .section-chip {
            padding: 0.5rem 0.8rem;
            border-radius: 999px;
            background: linear-gradient(90deg, rgba(95,125,255,0.18), rgba(0,197,172,0.18));
            border: 1px solid rgba(255,255,255,0.18);
            font-size: 0.82rem;
            margin-bottom: 0.65rem;
            display: inline-block;
            font-weight: 600;
            letter-spacing: 0.01em;
        }
        .highlight-box {
            border-radius: 14px;
            padding: 1rem 1.1rem;
            background: rgba(26, 29, 41, 0.55);
            border: 1px solid rgba(130, 148, 255, 0.25);
            min-height: 220px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Strategic Snapshot")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown('<span class="section-chip">Executive Summary</span>', unsafe_allow_html=True)
        st.markdown(report.executive_summary)
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown('<span class="section-chip">Target Market</span>', unsafe_allow_html=True)
        st.markdown(report.target_market)
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown('<span class="section-chip">Market Positioning</span>', unsafe_allow_html=True)
        st.markdown(report.market_positioning)
        st.markdown("</div>", unsafe_allow_html=True)

    tab_context, tab_operations, tab_execution = st.tabs(
        ["Business Context", "Operations & AI", "Execution Plan"]
    )
    with tab_context:
        st.container(border=True).markdown(f"#### Company Overview\n{report.company_overview}")
        st.container(border=True).markdown(f"#### Products / Services\n{report.products_services}")
        st.container(border=True).markdown(
            f"#### Overlooked Signals / Non-Obvious Insights\n{report.overlooked_signals}"
        )
    with tab_operations:
        st.container(border=True).markdown(
            f"#### Likely Operational Bottlenecks\n{report.likely_operational_bottlenecks}"
        )
        st.container(border=True).markdown(
            f"#### AI Automation Opportunities\n{report.ai_automation_opportunities}"
        )
    with tab_execution:
        st.container(border=True).markdown(
            f"#### Recommended Pilot (Company-Specific)\n{report.recommended_first_automation_pilot}"
        )
        st.container(border=True).markdown(f"#### 90-Day Prioritized AI Roadmap\n{report.prioritized_ai_roadmap}")
        st.container(border=True).markdown(f"#### Suggested Engagement Angle\n{report.suggested_engagement_angle}")

    st.markdown("---")
    st.container(border=True).markdown(RECOMMENDED_PILOT_SECTION)
    st.caption(report.disclaimer)


st.title("AI Business Workflow Analyst")
st.caption(
    "Analyze a company website with a multi-agent workflow to identify likely pain points "
    "and concrete AI automation opportunities."
)

with st.sidebar:
    st.subheader("Input")
    company_name = st.text_input("Company name", placeholder="e.g., Acme Logistics")
    website_url = st.text_input("Website URL", placeholder="https://example.com")
    industry_context = st.text_area(
        "Optional industry/context",
        placeholder="Anything useful: vertical, geography, business model, constraints...",
    )
    run_clicked = st.button("Run Analysis", type="primary", use_container_width=True)

    st.caption("LLM key env var: `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY` / `GROQ_API_KEY`).")

runtime_config = load_runtime_config()

st.markdown("---")

if not runtime_config.llm_api_key:
    st.warning(missing_api_key_message())

if "report_markdown" not in st.session_state:
    st.session_state.report_markdown = ""
if "report_data" not in st.session_state:
    st.session_state.report_data = None

if run_clicked:
    if not company_name.strip() or not website_url.strip():
        st.error("Please provide both company name and website URL.")
    elif not _valid_url(website_url):
        st.error("Website URL must start with http:// or https://")
    else:
        service = WorkflowService()
        progress_box = st.container(border=True)
        progress_bar = progress_box.progress(0)
        status_placeholder = progress_box.empty()

        step_progress = {
            "fetch": 15,
            "research": 35,
            "offering": 55,
            "opportunity": 75,
            "synthesis": 92,
            "fallback": 92,
            "done": 100,
        }

        def progress_callback(stage: str, message: str) -> None:
            progress_bar.progress(step_progress.get(stage, 5))
            status_placeholder.info(message)

        report = service.run(
            company_name=company_name,
            website_url=website_url,
            industry_context=industry_context,
            progress=progress_callback,
        )

        st.session_state.report_data = report.model_dump()
        st.session_state.report_markdown = to_markdown(report)
        status_placeholder.success("Report ready.")

if st.session_state.report_data:
    st.subheader("Final Report")
    render_report(FinalReport.model_validate(st.session_state.report_data))

    st.download_button(
        "Export Markdown",
        data=st.session_state.report_markdown,
        file_name="ai_business_workflow_report.md",
        mime="text/markdown",
        use_container_width=True,
    )
elif st.session_state.report_markdown:
    st.subheader("Final Report")
    st.markdown(st.session_state.report_markdown)
else:
    st.info("Run an analysis to generate a report.")
