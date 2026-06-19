from __future__ import annotations
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field


class ProfileInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    age: Annotated[int, Field(ge=18, le=80)]
    sector: str
    region: str
    risk_tolerance: Annotated[float, Field(ge=0.0, le=1.0)]
    current_savings: Annotated[float, Field(ge=0.0)]
    monthly_income: Annotated[float, Field(ge=0.0)]
    monthly_expenses: Annotated[float, Field(ge=0.0)]


class ScenarioParams(BaseModel):
    model_config = ConfigDict(frozen=True)

    years_to_simulate: Annotated[int, Field(ge=1, le=50)] = 30
    extra_monthly_contribution: Annotated[float, Field(ge=0.0)] = 0.0


class SimulationRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    profile: ProfileInput
    scenario: ScenarioParams = ScenarioParams()


class FanChart(BaseModel):
    years: list[int]
    p10: list[float]
    p25: list[float]
    p50: list[float]
    p75: list[float]
    p90: list[float]


class SimulationResponse(BaseModel):
    fan_chart: FanChart
    regime_fractions: dict[str, float]
    shock_summary: dict[str, float]
    regime_params: list[dict]