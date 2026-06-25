"""
Web search service — wraps Exa AI and Serper.
Used to find publicly available accepted resumes for context.
"""
from __future__ import annotations

import logging
import httpx

from app.utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Exa AI ────────────────────────────────────────────────────────────────────

async def _search_exa(query: str, num_results: int = 5) -> list[dict]:
    """
    Use Exa's neural search to find resume examples.
    Returns list of {url, title, snippet} dicts.
    """
    if not settings.exa_api_key:
        raise ValueError("EXA_API_KEY is not set.")

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            "https://api.exa.ai/search",
            headers={"x-api-key": settings.exa_api_key, "Content-Type": "application/json"},
            json={
                "query": query,
                "numResults": num_results,
                "type": "neural",
                "useAutoprompt": True,
                "contents": {"text": {"maxCharacters": 3000}},
            },
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("results", []):
        results.append({
            "url": item.get("url", ""),
            "title": item.get("title", ""),
            "snippet": item.get("text", "")[:2000],
        })
    return results


# ── Serper ────────────────────────────────────────────────────────────────────

async def _search_serper(query: str, num_results: int = 5) -> list[dict]:
    """
    Use Serper.dev Google Search API.
    Returns list of {url, title, snippet} dicts.
    """
    if not settings.serper_api_key:
        raise ValueError("SERPER_API_KEY is not set.")

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
            json={"q": query, "num": num_results},
        )
        resp.raise_for_status()
        data = resp.json()

    results = []
    for item in data.get("organic", [])[:num_results]:
        results.append({
            "url": item.get("link", ""),
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
        })
    return results


# ── Public interface ──────────────────────────────────────────────────────────

async def search_accepted_resumes(target_role: str, company: str = "") -> list[dict]:
    """
    Build a targeted query and dispatch to the configured search provider.
    Returns up to 5 result dicts with url/title/snippet.
    """
    company_clause = f'at "{company}" ' if company else ""
    query = (
        f'site:linkedin.com OR site:github.com OR site:resume.io '
        f'"{target_role}" resume {company_clause}accepted hired example'
    )

    logger.info("Searching for accepted resume examples: %s", query)

    try:
        provider = settings.search_provider.lower()
        if provider == "exa":
            results = await _search_exa(query)
        else:
            results = await _search_serper(query)

        logger.info("Found %d web results", len(results))
        return results

    except Exception as exc:
        logger.warning("Web search failed (%s); continuing without results: %s", type(exc).__name__, exc)
        return []
