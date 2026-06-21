from __future__ import annotations

import json
import logging
from typing import Any

from ._llm import chat
from ..config import settings

logger = logging.getLogger(__name__)

_SYSTEM = """
Translate a user's message into financial simulation parameters.
Return ONLY valid JSON with these exact keys:
{
    "years_to_simulate": <integer 1–50>,
    "extra_monthly_contribution": <float — extra saving per month in GBP, 0 if not mentioned>
}
Derive years_to_simulate from age-to-retirement-67 if not stated.
Reflect any mentioned pay rise or extra saving in extra_monthly_contribution.
""".strip()

_DEFAULTS: dict[str, Any] = {
    "years_to_simulate": 30,
    "extra_monthly_contribution": 0.0
}

def run(state: dict[str, Any]) -> dict[str, Any]:
    # What-if: start from existing params and override only what changed
    base = {**_DEFAULTS, **(state.get("existing_params") or {})}

    logger.info("parameter_translator: translating parameters")
    raw = chat(
        model=settings.fast_model,
        system=_SYSTEM,
        user=f"Profile: {json.dumps(state['profile'])}\nMessage: {state['user_message']}",
        json_mode=True,
        temperature=0.0,
        max_tokens=256,
    )

    try:
        translated = json.loads(raw)
        merged = {**base, **{k: v for k, v in translated.items() if v is not None}}
    except (json.JSONDecodeError, TypeError):
        logger.warning("parameter_translator: parse failed — using base params")
        merged = base

    # Hard cap: can't simulate past retirement age
    max_years = max(1, 67 - state["profile"].get("age", 35))
    merged["years_to_simulate"] = min(merged["years_to_simulate"], max_years)

    return {
        "sim_params": merged,
        "agent_logs": state["agent_logs"] + [
            {"agent": "parameter_translator", "output": merged},
        ],
    }