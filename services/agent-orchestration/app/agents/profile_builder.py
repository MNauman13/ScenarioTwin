from __future__ import annotations

import json
import logging
from typing import Any

from ._llm import chat
from ..config import settings

logger = logging.getLogger(__name__)

_SYSTEM = """
Extract a structured financial profile from the user message.
Return ONLY valid JSON with these exact keys:
{
    "age": <integer or null>,
    "sector": <string matching ONS sector names or null>,
    "region": <UK region name or null>,
    "risk_tolerance": <float 0.0–1.0 or null — conservative=0.2, moderate=0.5, aggressive=0.8>,
    "current_savings": <float GBP or null>,
    "monthly_income": <float GBP or null>,
    "monthly_expenses": <float GBP or null>
}
Return null for any field not mentioned. Do not guess.
""".strip()

_DEFAULTS: dict[str, Any] = {
    "age": 35,
    "sector": "All",
    "region": "Great Britain",
    "risk_tolerance": 0.5,
    "current_savings": 0.0,
    "monthly_income": 2500.0,
    "monthly_expenses": 1800.0
}


def run(state: dict[str, Any]) -> dict[str, Any]:
    # What-if mode: profile already known, skip extraction
    if state.get("existing_profile"):
        logger.info("profile_builder: skipping — existing profile present")
        return {
            "profile": state["existing_profile"],
            "agent_logs": state["agent_logs"] + [
                {"agent": "profile_builder", "skipped": True}
            ]
        }
    
    logger.info("profile_builder: extracting profile from message")
    raw = chat(
        model=settings.fast_model,
        system=_SYSTEM,
        user=state["user_message"],
        json_mode=True,
        temperature=0.0
    )

    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("profile_builder: JSON parse failed - falling back to defaults")
        extracted = {}

    # Defaults fill any missing fields; extracted values override where present
    profile = {**_DEFAULTS, **{k: v for k, v in extracted.items() if v is not None}}

    return {
        "profile": profile,
        "agent_logs": state["agent_logs"] + [
            {"agent": "profile_builder", "input": state["user_message"], "output": profile},
        ]
    }