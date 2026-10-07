"""
CareerPilot AI - LLM Configuration

Centralised LLM setup. Provider and timeout are controlled by env variables.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.1) -> BaseChatModel:
    """
    Return a configured LLM instance.

    Timeout is taken from settings.agent_timeout_seconds.
    Supported providers: openai | google | anthropic (set LLM_PROVIDER env var).
    """
    settings = get_settings()
    provider = settings.llm_provider.lower()
    timeout = float(settings.agent_timeout_seconds)

    logger.info("Initialising LLM: provider=%s, model=%s, timeout=%ss", provider, settings.llm_model, timeout)

    if provider == "openai":
        import os
        return ChatOpenAI(
            model="openrouter/free",
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY") or settings.openai_api_key,
            base_url="https://openrouter.ai/api/v1",
            timeout=timeout,
            max_retries=0,  # Retries are managed by graph retry logic, not the LLM client
        )

    if provider == "google":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
            return ChatGoogleGenerativeAI(
                model=settings.llm_model,
                temperature=temperature,
                google_api_key=settings.google_api_key,
                request_timeout=timeout,
            )
        except ImportError as exc:
            raise ImportError("Install langchain-google-genai to use the Google provider.") from exc

    if provider == "anthropic":
        try:
            from langchain_anthropic import ChatAnthropic  # type: ignore
            return ChatAnthropic(
                model=settings.llm_model,
                temperature=temperature,
                anthropic_api_key=settings.anthropic_api_key,
                timeout=timeout,
                max_retries=0,
            )
        except ImportError as exc:
            raise ImportError("Install langchain-anthropic to use the Anthropic provider.") from exc

    raise ValueError(f"Unsupported LLM provider: {provider!r}")


def get_structured_llm(schema, temperature: float = 0.1):
    """Return an LLM bound to a structured output schema."""
    llm = get_llm(temperature=temperature)
    return llm.with_structured_output(schema)
