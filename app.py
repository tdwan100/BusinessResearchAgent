"""Streamlit app for AI Business Workflow Analyst."""

from __future__ import annotations

import re

import streamlit as st

from services.workflow_service import WorkflowService
from tools.web_tools import WebsiteFetcher
from utils.config import load_runtime_config, missing_api_key_message
from utils.report_formatting import to_markdown


st.set_page_config(
    page_title="AI Business Workflow Analyst",
    page_icon="📊",
    layout="wide",
)


def _valid_url(url: str) -> bool:
    return bool(re.match(r"^https?://", url.strip()))


def render_report(markdown_report: str) -> None:
    st.markdown(markdown_report, unsafe_allow_html=True)


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

    st.caption("LLM env vars: `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY` / `GROQ_API_KEY`) and optional `LLM_MODEL`.")

runtime_config = load_runtime_config()

st.markdown("---")

if not runtime_config.llm_api_key:
    st.warning(missing_api_key_message())

if "report_markdown" not in st.session_state:
    st.session_state.report_markdown = ""
if "report_company_name" not in st.session_state:
    st.session_state.report_company_name = ""

if run_clicked:
    if not company_name.strip() or not website_url.strip():
        st.error("Please provide both company name and website URL.")
    elif not _valid_url(website_url):
        st.error("Website URL must start with http:// or https://")
    else:
        service = WorkflowService(
            model_name=runtime_config.llm_model,
            llm_provider=runtime_config.llm_provider,
        )
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

        st.session_state.report_markdown = to_markdown(report)
        st.session_state.report_company_name = company_name.strip()
        status_placeholder.success("Report ready.")

if st.session_state.report_markdown:
    st.subheader("Final Report")

    try:
        identity_icon_url = WebsiteFetcher().extract_site_identity_image(website_url)
        if identity_icon_url:
            left, right = st.columns([1, 5])
            with left:
                st.image(identity_icon_url, width=64)
            with right:
                st.markdown(f"**{st.session_state.report_company_name or company_name.strip()}**")
    except Exception:
        pass

    render_report(st.session_state.report_markdown)

    st.download_button(
        "Export Markdown",
        data=st.session_state.report_markdown,
        file_name="ai_business_workflow_report.md",
        mime="text/markdown",
        use_container_width=True,
    )
else:
    st.info("Run an analysis to generate a report.")
