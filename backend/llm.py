"""
CareerPilot AI - LLM Configuration

Centralised LLM setup so the provider can be changed through env variables.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.1) -> BaseChatModel:
    """
    Return a configured LLM instance.

    The provider is controlled by the LLM_PROVIDER env var.
    Currently supports:
      - openai   → ChatOpenAI (default)
      - google   → ChatGoogleGenerativeAI
      - anthropic → ChatAnthropic
    """
    settings = get_settings()
    provider = settings.llm_provider.lower()

    logger.info("Initialising LLM: provider=%s, model=%s", provider, settings.llm_model)

    if provider == "openai":
        return ChatOpenAI(
            model=settings.llm_model,
            temperature=temperature,
            api_key=settings.openai_api_key,
            max_retries=3,
        )

    if provider == "google":
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore

            return ChatGoogleGenerativeAI(
                model=settings.llm_model,
                temperature=temperature,
                google_api_key=settings.google_api_key,
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
