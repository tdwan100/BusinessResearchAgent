"""Runtime configuration helpers for provider API keys."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class RuntimeConfig:
    llm_api_key: str | None
    llm_provider: str
    llm_model: str | None


def load_runtime_config() -> RuntimeConfig:
    """Load environment configuration and infer active provider key.

    CrewAI commonly relies on LiteLLM-compatible provider keys, with OPENAI_API_KEY
    being the default for many setups.
    """
    load_dotenv()

    if os.getenv("OPENAI_API_KEY"):
        return RuntimeConfig(
            llm_api_key=os.getenv("OPENAI_API_KEY"),
            llm_provider="openai",
            llm_model=os.getenv("LLM_MODEL"),
        )
    if os.getenv("ANTHROPIC_API_KEY"):
        return RuntimeConfig(
            llm_api_key=os.getenv("ANTHROPIC_API_KEY"),
            llm_provider="anthropic",
            llm_model=os.getenv("LLM_MODEL"),
        )
    if os.getenv("GROQ_API_KEY"):
        return RuntimeConfig(
            llm_api_key=os.getenv("GROQ_API_KEY"),
            llm_provider="groq",
            llm_model=os.getenv("LLM_MODEL"),
        )

    return RuntimeConfig(llm_api_key=None, llm_provider="unconfigured", llm_model=os.getenv("LLM_MODEL"))


def missing_api_key_message() -> str:
    return (
        "No LLM API key detected. Set OPENAI_API_KEY (recommended) or another provider key "
        "such as ANTHROPIC_API_KEY or GROQ_API_KEY in your environment/.env file."
    )
