from __future__ import annotations

import logging
import re
from typing import Any

from ._llm import chat
from ..config import settings

logger = logging.getLogger(__name__)

# FCA PERG-derived patterns that cross the advice/information boundary
_DISALLOWED: list[re.Pattern] = [
    re.compile(r"\byou should\b",      re.IGNORECASE),
    re.compile(r"\bI recommend\b",     re.IGNORECASE),
    re.compile(r"\byou must\b",        re.IGNORECASE),
    re.compile(r"\bbest option\b",     re.IGNORECASE),
    re.compile(r"\bI (would )?advise\b", re.IGNORECASE),
    re.compile(r"\bmove your money\b", re.IGNORECASE),
    re.compile(r"\binvest in\b",       re.IGNORECASE),
    re.compile(r"\bbuy more\b",        re.IGNORECASE),
]

_REWRITE_SYSTEM = """
Rewrite the text below to remove all financial advice framing.
Replace advice phrases with purely informational equivalents:
    "you should save more" -> "the simulation results improve with higher savings rates"
    "I recommend" -> "the projections indicate that"
    "you must" -> "historically, portfolios that..."
Return ONLY the rewritten text. No explanation, no preamble.
""".strip()

def run(state: dict[str, Any]) -> dict[str, Any]:
    text = state["raw_narrative"]

    # Pass 1 - fast regex (no LLM call, no cost)
    violations = [p.pattern for p in _DISALLOWED if p.search(text)]

    if not violations:
        logger.info("guardrail: passed regex scan — no violations")
        return {
            "final_narrative": text,
            "guardrail_flag": None,
            "agent_logs": state["agent_logs"] + [
                {"agent": "guardrail", "passed": True, "method": "regex"}
            ]
        }
    
    # Pass 2 - LLM rewrite (only reached when regex fails)
    logger.warning("guardrail: violations %s — rewriting with LLM", violations)
    rewritten = chat(
        model=settings.guardrail_model,
        system=_REWRITE_SYSTEM,
        user=text,
        temperature=0.0,
        max_tokens=400
    )

    return {
        "final_narrative": rewritten,
        "guardrail_flag": f"Rewritten - violations: {violations}",
        "agent_logs": state["agent_logs"] + [
            {"agent": "guardrail", "passed": False, "violations": violations}
        ]
    }

