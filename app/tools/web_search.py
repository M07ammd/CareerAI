"""
CareerPilot AI - Web Search Tool

Provides a simple web search function used by the Roadmap and Gap agents.
Supports Tavily (primary) with a Serper.dev fallback.
Uses httpx and async.
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
from datetime import datetime
from typing import List

import httpx
from app.config import get_settings

logger = logging.getLogger(__name__)

# Simple in-memory cache to prevent duplicate searches on retries
_search_cache: dict[str, List[str]] = {}


def _get_current_year() -> str:
    return str(datetime.now().year)


async def async_web_search(query: str, max_results: int = 5) -> List[str]:
    """
    Search the web asynchronously and return a list of result snippets.
    Automatically replaces "2024" with current year.
    Uses exponential backoff with jitter on retries.
    """
    query = query.replace("2024", _get_current_year())
    cache_key = f"{query}_{max_results}"

    if cache_key in _search_cache:
        logger.debug("Returning cached web search for: %r", query)
        return _search_cache[cache_key]

    for attempt in range(3):
        try:
            results = await _try_tavily(query, max_results)
            if results:
                _search_cache[cache_key] = results
                return results

            results = await _try_serper(query, max_results)
            if results:
                _search_cache[cache_key] = results
                return results

            break # Both failed cleanly, don't blindly retry if no exception
        except httpx.TimeoutException:
            delay = (2 ** attempt) + random.uniform(0, 1)
            logger.warning("Search timeout (attempt %d). Retrying in %.2fs", attempt + 1, delay)
            await asyncio.sleep(delay)
        except Exception as exc:
            logger.warning("Search error: %s", exc)
            break

    logger.warning("All web search providers failed for query: %r", query)
    return []


def web_search(query: str, max_results: int = 5) -> List[str]:
    """Sync wrapper for legacy code (will be removed when agents are async)."""
    try:
        loop = asyncio.get_running_loop()
        # If we are already in an event loop, we shouldn't use the sync wrapper
        # But this works for testing or if we haven't converted everything yet
        raise RuntimeError("web_search called from async context; use async_web_search")
    except RuntimeError:
        return asyncio.run(async_web_search(query, max_results))


async def _try_tavily(query: str, max_results: int) -> List[str]:
    settings = get_settings()
    if not settings.tavily_api_key:
        return []

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={"api_key": settings.tavily_api_key, "query": query, "max_results": max_results},
        )
        response.raise_for_status()
        data = response.json()
        snippets = []
        for r in data.get("results", []):
            title = r.get("title", "")
            content = r.get("content", "")
            url = r.get("url", "")
            snippets.append(f"[{title}] {content} ({url})")
        logger.info("Tavily returned %d results for: %r", len(snippets), query)
        return snippets[:max_results]


async def _try_serper(query: str, max_results: int) -> List[str]:
    settings = get_settings()
    if not settings.serper_api_key:
        return []

    headers = {"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"}
    payload = {"q": query, "num": max_results}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            "https://google.serper.dev/search", headers=headers, json=payload
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
