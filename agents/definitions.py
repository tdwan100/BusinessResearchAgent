"""CrewAI agent factory definitions."""

from __future__ import annotations

from crewai import Agent, LLM


class AgentFactory:
    def __init__(self, model_name: str | None = None, llm_provider: str = "openai") -> None:
        self.model_name = model_name.strip() if model_name else None
        self.llm_provider = llm_provider

    def _agent_kwargs(self) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "verbose": False,
            "allow_delegation": False,
        }
        if self.model_name:
            kwargs["llm"] = LLM(model=self.model_name, provider=self.llm_provider)
        return kwargs

    def build_research_agent(self) -> Agent:
        return Agent(
            role="Research Agent",
            goal=(
                "Gather grounded, website-based intelligence on the company without "
                "making unsupported claims."
            ),
            backstory=(
                "You are a meticulous B2B analyst who distinguishes observed facts from "
                "inference and always cites confidence limits."
            ),
            **self._agent_kwargs(),
        )

    def build_offering_market_agent(self) -> Agent:
        return Agent(
            role="Offering & Market Agent",
            goal=(
                "Infer what the company sells, who it serves, and how it positions itself "
                "using cautious business language."
            ),
            backstory=(
                "You are a go-to-market strategist skilled at identifying products, buyer "
                "segments, and commercial models from sparse public information."
            ),
            **self._agent_kwargs(),
        )

    def build_pain_point_agent(self) -> Agent:
        return Agent(
            role="Pain Point / Opportunity Agent",
            goal=(
                "Map likely operational bottlenecks to realistic AI automation opportunities "
                "with practical business outcomes."
            ),
            backstory=(
                "You are an operations consultant who prioritizes feasible, high-ROI AI "
                "use cases while calling out risk considerations."
            ),
            **self._agent_kwargs(),
        )

    def build_report_synthesizer_agent(self) -> Agent:
        return Agent(
            role="Report Synthesizer Agent",
            goal=(
                "Produce polished executive-ready reports that are clear, credible, and "
                "actionable for business stakeholders."
            ),
            backstory=(
                "You are a senior strategy advisor who turns analytical inputs into concise "
                "decision-ready narratives."
            ),
            **self._agent_kwargs(),
        )
