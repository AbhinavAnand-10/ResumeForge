"""
LLM client factory.
Returns a callable that accepts (system_prompt, user_prompt) → str.
Supports OpenAI (GPT-4o) and Anthropic (Claude 3.5 Sonnet).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Callable

from app.utils.config import get_settings

logger = logging.getLogger(__name__)


def _clean_json(raw: str) -> str:
    """Strip markdown code fences and stray text before/after JSON."""
    raw = raw.strip()
    # Remove ```json ... ``` wrappers
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def _make_openai_client(settings) -> Callable:
    from openai import OpenAI
    client = OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1",
    )

    def call(system_prompt: str, user_prompt: str) -> str:
        response = client.chat.completions.create(
            model=settings.openai_model,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""

    return call


def _make_anthropic_client(settings) -> Callable:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def call(system_prompt: str, user_prompt: str) -> str:
        message = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text if message.content else ""

    return call


def get_llm() -> Callable:
    """Return the configured LLM callable."""
    settings = get_settings()
    if settings.llm_provider == "anthropic":
        logger.info("Using Anthropic %s", settings.anthropic_model)
        return _make_anthropic_client(settings)
    else:
        logger.info("Using OpenAI %s", settings.openai_model)
        return _make_openai_client(settings)


def call_llm_json(system_prompt: str, user_prompt: str) -> dict:
    """
    Call the LLM and parse the result as JSON.
    Raises ValueError if the response is not valid JSON.
    """
    llm = get_llm()
    raw = llm(system_prompt, user_prompt)
    cleaned = _clean_json(raw)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("LLM returned non-JSON:\n%s", cleaned[:500])
        raise ValueError(f"LLM did not return valid JSON: {exc}") from exc
