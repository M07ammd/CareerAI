"""
CareerPilot AI - LLM Configuration

Centralised LLM setup. Provider, model and timeout are controlled by env
variables (LLM_PROVIDER, LLM_MODEL, LLM_BASE_URL, agent_timeout_seconds).
No API keys are read from os.getenv here — use settings only.
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

    Provider is selected by LLM_PROVIDER env var (openai | google | anthropic).
    Model is selected by LLM_MODEL env var.
    An optional LLM_BASE_URL overrides the default API endpoint (e.g. OpenRouter).
    Timeout is taken from AGENT_TIMEOUT_SECONDS.
    Retries are managed by the LangGraph RetryPolicy — max_retries=0 here.
    """
    settings = get_settings()
    provider = settings.llm_provider.lower()
    timeout = float(settings.agent_timeout_seconds)

    logger.info(
        "Initialising LLM: provider=%s, model=%s, base_url=%s, timeout=%ss",
        provider,
        settings.llm_model,
        settings.llm_base_url or "(default)",
        timeout,
    )

    if provider == "openai":
        kwargs: dict = dict(
            model=settings.llm_model,
            temperature=temperature,
            api_key=settings.openai_api_key,
            timeout=timeout,
            max_retries=0,  # Retries handled by LangGraph RetryPolicy
        )
        if settings.llm_base_url:
            kwargs["base_url"] = settings.llm_base_url
        return ChatOpenAI(**kwargs)

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
            raise ImportError(
                "Install langchain-google-genai to use the Google provider."
            ) from exc

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
            raise ImportError(
                "Install langchain-anthropic to use the Anthropic provider."
            ) from exc

    raise ValueError(f"Unsupported LLM provider: {provider!r}")


def get_structured_llm(schema, temperature: float = 0.1):
    """Return an LLM bound to a structured output schema."""
    llm = get_llm(temperature=temperature)
    return llm.with_structured_output(schema)
