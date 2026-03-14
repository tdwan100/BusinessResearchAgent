"""High-level service orchestrating the multi-agent analysis workflow."""

from __future__ import annotations

from typing import Callable

from crews.workflow_crew import WorkflowEngine, WorkflowInputs
from schemas.workflow_models import FinalReport

ProgressCallback = Callable[[str, str], None]


class WorkflowService:
    def __init__(self) -> None:
        self.engine = WorkflowEngine()

    def run(
        self,
        company_name: str,
        website_url: str,
        industry_context: str = "",
        progress: ProgressCallback | None = None,
    ) -> FinalReport:
        progress = progress or (lambda _stage, _message: None)

        inputs = WorkflowInputs(
            company_name=company_name.strip(),
            website_url=website_url.strip(),
            industry_context=industry_context.strip(),
        )

        try:
            progress("fetch", "Collecting company website context...")
            context = self.engine.collect_company_context(inputs)

            progress("research", "Research Agent is analyzing the company...")
            research = self.engine.run_research_stage(context)

            progress("offering", "Offering & Market Agent is mapping products and buyers...")
            offering = self.engine.run_offering_stage(context, research)

            progress("opportunity", "Pain Point / Opportunity Agent is identifying automation potential...")
            opportunity = self.engine.run_opportunity_stage(context, research, offering)

            progress("synthesis", "Report Synthesizer Agent is producing the final report...")
            report = self.engine.run_report_stage(research, offering, opportunity)

            progress("done", "Analysis complete.")
            return report
        except Exception as exc:
            progress(
                "fallback",
                "Workflow used fallback synthesis due to runtime issue. "
                "Results are heuristic and should be validated.",
            )
            return self._fallback_report(inputs.company_name, inputs.website_url, str(exc))

    def _fallback_report(self, company_name: str, website_url: str, error_hint: str) -> FinalReport:
        return FinalReport(
            executive_summary=(
                f"{company_name} appears to maintain an active digital presence at {website_url}. "
                "Based on limited processing context, the organization likely has opportunities "
                "to streamline customer-facing and internal workflows with applied AI."
            ),
            company_overview=(
                f"The assessment used publicly available website material from {website_url}. "
                "Because the full agent workflow was partially constrained, this summary should "
                "be treated as directional rather than definitive."
            ),
            products_services=(
                "The company likely offers a focused set of products or services communicated "
                "through core website pages (e.g., solutions, services, or platform messaging)."
            ),
            target_market=(
                "The target market appears to include business decision-makers evaluating "
                "outsourced expertise, technology capabilities, or operational support."
            ),
            market_positioning=(
                "The brand appears to position itself on expertise, reliability, and outcomes. "
                "Further competitor analysis would sharpen differentiation insights."
            ),
            likely_operational_bottlenecks=(
                "Likely bottlenecks include repetitive lead qualification, fragmented customer "
                "communication, and manual knowledge retrieval for teams."
            ),
            ai_automation_opportunities=(
                "Practical opportunities likely include AI-assisted inbound triage, proposal "
                "drafting copilots, and internal knowledge assistants tied to SOP content."
            ),
            suggested_engagement_angle=(
                "Recommend a phased engagement starting with a discovery workshop, baseline KPI "
                "definition, and one pilot automation with measurable cycle-time impact."
            ),
            disclaimer=(
                "This report includes inferred content because the full model-driven workflow "
                f"was not fully available in the runtime environment ({error_hint[:180]}). "
                "Validate with stakeholder interviews and operational data before execution."
            ),
        )
