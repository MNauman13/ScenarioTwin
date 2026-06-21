from __future__ import annotations

import logging
from typing import Any

from ._llm import chat
from ..config import settings

logger = logging.getLogger(__name__)

_SYSTEM = """
You are a financial information tool — NOT a financial advisor.
Describe simulation results in plain, factual English.

STRICT RULES — never use:
  "you should", "I recommend", "you must", "best option",
  "I advise", "move your money", "buy", "invest in"

ALWAYS use phrases like:
  "the simulation shows", "based on these projections",
  "historically", "across the modelled paths"

Present the full range (p10 to p90) honestly.
Mention that scenarios include correlated job loss and market downturns.
Keep response under 180 words.
""".strip()

def run(state: dict[str, Any]) -> dict[str, Any]:
    logger.info("narrator: generating narrative")
    p  = state["profile"]
    fc = state["sim_results"]["fan_chart"]
    sr = state["sim_results"]
    last = len(fc["years"]) - 1
    yr   = fc["years"][last]

    context = (
        f"Profile: age {p['age']}, {p['sector']}, {p['region']}. "
        f"Savings: £{p['current_savings']:,.0f}. "
        f"Income: £{p['monthly_income']:,.0f}/month, expenses: £{p['monthly_expenses']:,.0f}/month.\n"
        f"Simulation: {yr} years.\n"
        f"Year {yr} — pessimistic (p10): £{fc['p10'][last]:,.0f}, "
        f"median (p50): £{fc['p50'][last]:,.0f}, "
        f"optimistic (p90): £{fc['p90'][last]:,.0f}.\n"
        f"Average job disruptions per path: {sr['shock_summary']['avg_job_losses_per_path']:.1f}. "
        f"Regime split — normal: {sr['regime_fractions']['normal']:.0%}, "
        f"recession: {sr['regime_fractions']['recession']:.0%}, "
        f"crisis: {sr['regime_fractions']['crisis']:.0%}."
    )

    narrative = chat(
        model=settings.narrator_model,
        system=_SYSTEM,
        user=f"Describe these results:\n{context}",
        temperature=0.3,
        max_tokens=300,
    )

    return {
        "raw_narrative": narrative,
        "agent_logs":    state["agent_logs"] + [
            {"agent": "narrator", "chars": len(narrative)},
        ],
    }