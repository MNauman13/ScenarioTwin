from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict

class OrchestrationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_message: str
    existing_profile: dict[str, Any] | None = None
    existing_params: dict[str, Any] | None = None


class GuardrailResult(BaseModel):
    passed: bool
    flag: str | None = None


class OrchestrationResponse(BaseModel):
    profile: dict[str, Any]
    sim_params: dict[str, Any]
    narrative: str
    fan_chart: dict[str, Any]
    regime_fractions: dict[str, float]
    shock_summary: dict[str, float]
    guardrail: GuardrailResult
    agent_logs: list[dict[str, Any]]
    