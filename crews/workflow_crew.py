"""Crew orchestration for the AI Business Workflow Analyst app."""

from __future__ import annotations

import json
from dataclasses import dataclass

from crewai import Crew, Process, Task
from pydantic import BaseModel

from agents.definitions import AgentFactory
from schemas.workflow_models import (
    FinalReport,
    OfferingMarketOutput,
    OpportunityOutput,
    ResearchOutput,
)
from tools.search_tools import SearchEnricher
from tools.web_tools import PageSelector, TextCleaner, WebsiteFetcher


@dataclass
class WorkflowInputs:
    company_name: str
    website_url: str
    industry_context: str = ""


class WorkflowEngine:
    def __init__(self, model_name: str | None = None, llm_provider: str = "openai") -> None:
        self.agent_factory = AgentFactory(model_name=model_name, llm_provider=llm_provider)
        self.fetcher = WebsiteFetcher()
        self.selector = PageSelector()
        self.cleaner = TextCleaner()
        self.enricher = SearchEnricher()

    def _extract_model(self, kickoff_result: object, model_cls: type[BaseModel]) -> BaseModel:
        if isinstance(kickoff_result, model_cls):
            return kickoff_result

        for attr in ("pydantic", "json_dict"):
            value = getattr(kickoff_result, attr, None)
            if isinstance(value, model_cls):
                return value
            if isinstance(value, dict):
                return model_cls.model_validate(value)

        raw = getattr(kickoff_result, "raw", kickoff_result)
        if isinstance(raw, dict):
            return model_cls.model_validate(raw)
        if isinstance(raw, str):
            return model_cls.model_validate(json.loads(raw))

        raise ValueError(f"Unable to parse Crew output into {model_cls.__name__}")

    def collect_company_context(self, inputs: WorkflowInputs) -> dict[str, object]:
        homepage_html = self.fetcher.fetch_html(inputs.website_url)
        focus_urls = self.selector.extract_priority_urls(homepage_html, inputs.website_url)

        pages = [self.fetcher.scrape_page(inputs.website_url)]
        for url in focus_urls:
            try:
                pages.append(self.fetcher.scrape_page(url))
            except Exception:
                continue

        page_blobs = [
            {
                "url": p.url,
                "title": p.title,
                "text": self.cleaner.clean(p.text),
            }
            for p in pages
        ]

        enrichment = [s.__dict__ for s in self.enricher.enrich(inputs.company_name, inputs.industry_context)]

        return {
            "company_name": inputs.company_name,
            "website_url": inputs.website_url,
            "industry_context": inputs.industry_context,
            "pages": page_blobs,
            "enrichment": enrichment,
        }

    def run_research_stage(self, context: dict[str, object]) -> ResearchOutput:
        agent = self.agent_factory.build_research_agent()
        task = Task(
            description=(
                "Analyze the provided website page excerpts and produce grounded company "
                "research. Focus on factual observations from the source pages.\n"
                "Return valid JSON matching this schema exactly: "
                f"{ResearchOutput.model_json_schema()}\n"
                "Use careful language for uncertain points and include confidence notes.\n"
                f"Context: {json.dumps(context)}"
            ),
            expected_output="JSON object with research findings.",
            output_json=ResearchOutput,
            agent=agent,
        )
        result = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff()
        return self._extract_model(result, ResearchOutput)

    def run_offering_stage(
        self,
        context: dict[str, object],
        research: ResearchOutput,
    ) -> OfferingMarketOutput:
        agent = self.agent_factory.build_offering_market_agent()
        task = Task(
            description=(
                "Using the research output and company context, infer offerings, target "
                "market, and market positioning. Distinguish fact vs inference and avoid "
                "hard claims.\n"
                "Return valid JSON matching this schema exactly: "
                f"{OfferingMarketOutput.model_json_schema()}\n"
                f"Research: {research.model_dump_json()}\n"
                f"Context: {json.dumps(context)}"
            ),
            expected_output="JSON object describing offerings and market.",
            output_json=OfferingMarketOutput,
            agent=agent,
        )
        result = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff()
        return self._extract_model(result, OfferingMarketOutput)

    def run_opportunity_stage(
        self,
        context: dict[str, object],
        research: ResearchOutput,
        offering: OfferingMarketOutput,
    ) -> OpportunityOutput:
        agent = self.agent_factory.build_pain_point_agent()
        task = Task(
            description=(
                "Identify likely operational bottlenecks and map each one to concrete AI "
                "automation opportunities. Avoid generic advice: tie each opportunity to specific "
                "signals from the provided pages/enrichment and state why it is differentiated. "
                "Include practical KPIs and implementation constraints.\n"
                "Return valid JSON matching this schema exactly: "
                f"{OpportunityOutput.model_json_schema()}\n"
                f"Research: {research.model_dump_json()}\n"
                f"Offering: {offering.model_dump_json()}\n"
                f"Context: {json.dumps(context)}"
            ),
            expected_output="JSON object describing bottlenecks and opportunities.",
            output_json=OpportunityOutput,
            agent=agent,
        )
        result = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff()
        return self._extract_model(result, OpportunityOutput)

    def run_report_stage(
        self,
        research: ResearchOutput,
        offering: OfferingMarketOutput,
        opportunity: OpportunityOutput,
    ) -> FinalReport:
        agent = self.agent_factory.build_report_synthesizer_agent()
        task = Task(
            description=(
                "Synthesize a polished report for business stakeholders. Keep language clear, non-technical, "
                "credible, and actionable. Avoid redundancy and avoid generic consulting phrasing. "
                "Highlight non-obvious signals a typical reader may overlook, and provide a "
                "prioritized 90-day roadmap (quick wins first) with expected KPI impact. Keep each "
                "field concise: use short headings and bullets, limit supporting detail to the most "
                "decision-relevant points, and avoid long paragraphs. Include uncertainty language "
                "where needed.\n"
                "Return valid JSON matching this schema exactly: "
                f"{FinalReport.model_json_schema()}\n"
                f"Research: {research.model_dump_json()}\n"
                f"Offering: {offering.model_dump_json()}\n"
                f"Opportunity: {opportunity.model_dump_json()}"
            ),
            expected_output="JSON object for a polished final report.",
            output_json=FinalReport,
            agent=agent,
        )
        result = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff()
        report = self._extract_model(result, FinalReport)

        if not report.disclaimer.strip():
            report.disclaimer = (
                "This assessment is based on publicly visible information and analyst inference; "
                "it should be validated with internal stakeholder interviews and operational data."
            )
        return report
