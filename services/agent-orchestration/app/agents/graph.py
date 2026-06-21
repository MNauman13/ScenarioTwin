from __future__ import annotations

import logging
from typing import Any, TypedDict

import httpx
from langgraph.graph import StateGraph, START, END

from ..config import settings
from . import profile_builder, parameter_translator, narrator, guardrail

logger = logging.getLogger(__name__)

class OrchestrationState(TypedDict):
    user_message: str
    existing_profile: dict[str, Any] | None
    existing_params: dict[str, Any] | None
    profile: dict[str, Any] | None
    sim_params: dict[str, Any] | None
    sim_results: dict[str, Any] | None
    raw_narrative: str | None
    final_narrative: str | None
    guardrail_flag: str | None
    agent_logs: list[dict[str, Any]]


def _call_simulation(state: OrchestrationState) -> dict[str, Any]:
    """
    HTTP node - not an LLM agent, just a synchronous call to 
    the sim engine.
    """
    payload = {
        "profile": state["profile"],
        "scenario": state["sim_params"]
    }
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{settings.simulation_engine_url}/simulate",
            json=payload
        )
    response.raise_for_status()

    return {
        "sim_results": response.json(),
        "agent_logs": state["agent_logs"] + [
            {"agent": "simulation_engine", "status": "ok"}
        ]
    }


def _build() -> StateGraph:
    builder = StateGraph(OrchestrationState)

    builder.add_node("profile_builder", profile_builder.run)
    builder.add_node("parameter_translator", parameter_translator.run)
    builder.add_node("call_simulation", _call_simulation)
    builder.add_node("narrator", narrator.run)
    builder.add_node("guardrail", guardrail.run)

    builder.add_edge(START, "profile_builder")
    builder.add_edge("profile_builder", "parameter_translator")
    builder.add_edge("parameter_translator", "call_simulation")
    builder.add_edge("call_simulation", "narrator")
    builder.add_edge("narrator", "guardrail")
    builder.add_edge("guardrail", END)

    return builder.compile()


# Compiled once at import time - reused across all requests
orchestration_graph = _build()