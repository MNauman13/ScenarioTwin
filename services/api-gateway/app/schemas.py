from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=64)]
    password: Annotated[str, Field(min_length=8)]


class ProfileCreate(BaseModel):
    model_config = ConfigDict(frozen=True)

    age:              Annotated[int,   Field(ge=18, le=80)]
    sector:           str
    region:           str
    dependents:       Annotated[int,   Field(ge=0)] = 0
    risk_tolerance:   Annotated[float, Field(ge=0.0, le=1.0)]
    monthly_income:   Annotated[float, Field(ge=0.0)]
    monthly_expenses: Annotated[float, Field(ge=0.0)]
    current_savings:  Annotated[float, Field(ge=0.0)]


class ProfileResponse(ProfileCreate):
    model_config = ConfigDict(frozen=False)

    id:         int
    created_at: datetime


class ScenarioParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    years_to_simulate:          Annotated[int,   Field(ge=1, le=50)] = 30
    extra_monthly_contribution: Annotated[float, Field(ge=0.0)]      = 0.0


class SimulateRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    profile_id: int
    scenario:   ScenarioParams = ScenarioParams()


class SimulationResult(BaseModel):
    id:               int
    fan_chart:        dict[str, Any]
    regime_fractions: dict[str, float]
    shock_summary:    dict[str, float]
    cached:           bool = False


class WhatIfRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    profile_id:   int
    user_message: str


class WhatIfResponse(BaseModel):
    narrative:        str
    fan_chart:        dict[str, Any]
    regime_fractions: dict[str, float]
    shock_summary:    dict[str, float]
    guardrail:        dict[str, Any]
