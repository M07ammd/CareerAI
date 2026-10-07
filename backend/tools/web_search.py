"""
CareerPilot AI - Web Search Tool

Provides a simple web search function used by the Roadmap and Gap agents.
Supports Tavily (primary) with a SerpAPI/Serper.dev fallback.
"""

from __future__ import annotations

import logging
from typing import List

logger = logging.getLogger(__name__)


def web_search(query: str, max_results: int = 5) -> List[str]:
    """
    Search the web and return a list of result snippets.

    Args:
        query:       Search query string.
        max_results: Maximum number of results to return.

    Returns:
        List of text snippets from search results.
        Returns an empty list (never raises) so agents degrade gracefully.
    """
    results = _try_tavily(query, max_results)
    if results:
        return results

    results = _try_serper(query, max_results)
    if results:
        return results

    logger.warning("All web search providers failed for query: %r", query)
    return []


def _try_tavily(query: str, max_results: int) -> List[str]:
    """Tavily AI search (best quality for research tasks)."""
    try:
        from config import get_settings

        settings = get_settings()
        if not settings.tavily_api_key:
            return []

        from tavily import TavilyClient  # type: ignore

        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(query=query, max_results=max_results)
        snippets = []
        for r in response.get("results", []):
            title = r.get("title", "")
            content = r.get("content", "")
            url = r.get("url", "")
            snippets.append(f"[{title}] {content} ({url})")
        logger.info("Tavily returned %d results for: %r", len(snippets), query)
        return snippets[:max_results]

    except ImportError:
        logger.debug("Tavily package not installed")
        return []
    except Exception as exc:
        logger.warning("Tavily search failed: %s", exc)
        return []


def _try_serper(query: str, max_results: int) -> List[str]:
    """Serper.dev Google Search API."""
    try:
        import json

        import requests  # type: ignore

        from config import get_settings

        settings = get_settings()
        if not settings.serper_api_key:
            return []

        headers = {"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"}
        payload = json.dumps({"q": query, "num": max_results})
        response = requests.post(
            "https://google.serper.dev/search", headers=headers, data=payload, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        snippets = []
        for r in data.get("organic", []):
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            link = r.get("link", "")
            snippets.append(f"[{title}] {snippet} ({link})")
        logger.info("Serper returned %d results for: %r", len(snippets), query)
        return snippets[:max_results]

    except ImportError:
        return []
    except Exception as exc:
        logger.warning("Serper search failed: %s", exc)
        return []
