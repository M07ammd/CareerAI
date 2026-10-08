"""
CareerPilot AI - Agent Runner

Centralised exception handling for all agents.

Design:
- Transient errors (timeout, 429, 5xx, connection) are RE-RAISED so that
  LangGraph's RetryPolicy can retry the node. They are converted to error
  state ONLY once retries are exhausted (LangGraph catches the final raise
  and stores it; we handle that in the graph result → AnalysisResponse
  conversion layer).
- Validation / input errors (bad data, missing prereqs) are non-retryable
  and are returned immediately as error state.
- After all retries are exhausted the graph node raises; the analysis
  service catches that and marks the run as failed.
"""

from __future__ import annotations

import functools
import logging
from typing import Callable, Awaitable, Any

import httpx

logger = logging.getLogger(__name__)

# Exception types that indicate transient failures worth retrying.
_TRANSIENT_BASES = (
    TimeoutError,
    ConnectionError,
    OSError,
)

try:
    import openai as _oai

    _TRANSIENT_OPENAI = (
        _oai.APITimeoutError,
        _oai.APIConnectionError,
        _oai.RateLimitError,
        _oai.InternalServerError,
    )
except ImportError:  # pragma: no cover
    _TRANSIENT_OPENAI = ()  # type: ignore[assignment]


def is_transient(exc: BaseException) -> bool:
    """Return True if *exc* is a transient error that should be retried."""
    if isinstance(exc, _TRANSIENT_BASES):
        return True
    if _TRANSIENT_OPENAI and isinstance(exc, _TRANSIENT_OPENAI):
        return True
    # httpx errors (used by langchain-openai internally)
    try:
        import httpx as _httpx

        if isinstance(exc, (_httpx.TimeoutException, _httpx.NetworkError)):
            return True
    except ImportError:
        pass
    # Fallback: inspect message for HTTP status codes
    msg = str(exc).lower()
    if any(code in msg for code in ("429", "500", "502", "503", "504")):
        return True
    return False