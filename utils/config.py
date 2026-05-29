"""Runtime configuration helpers for provider API keys."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class RuntimeConfig:
    llm_api_key: str | None
    llm_provider: str
    llm_model: str | None


def _normalized_model_name() -> str | None:
    """Return a backend model override safe for CrewAI/LiteLLM, if configured."""
    model_name = os.getenv("LLM_MODEL", "").strip()
    if not model_name:
        return None
    return re.sub(r"\s+", "-", model_name)


def load_runtime_config() -> RuntimeConfig:
    """Load environment configuration and infer active provider key.

    CrewAI commonly relies on LiteLLM-compatible provider keys, with OPENAI_API_KEY
    being the default for many setups.
    """
    load_dotenv()
    llm_model = _normalized_model_name()

    if os.getenv("OPENAI_API_KEY"):
        return RuntimeConfig(
            llm_api_key=os.getenv("OPENAI_API_KEY"),
            llm_provider="openai",
            llm_model=llm_model,
        )
    if os.getenv("ANTHROPIC_API_KEY"):
        return RuntimeConfig(
            llm_api_key=os.getenv("ANTHROPIC_API_KEY"),
            llm_provider="anthropic",
            llm_model=llm_model,
        )
    if os.getenv("GROQ_API_KEY"):
        return RuntimeConfig(
            llm_api_key=os.getenv("GROQ_API_KEY"),
            llm_provider="groq",
            llm_model=llm_model,
        )

    return RuntimeConfig(llm_api_key=None, llm_provider="unconfigured", llm_model=llm_model)


def missing_api_key_message() -> str:
    return (
        "No LLM API key detected. Set OPENAI_API_KEY (recommended) or another provider key "
        "such as ANTHROPIC_API_KEY or GROQ_API_KEY in your environment/.env file."
    )
