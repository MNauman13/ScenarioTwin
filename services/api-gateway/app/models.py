from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]      = mapped_column(primary_key=True)
    username:        Mapped[str]      = mapped_column(String(64), unique=True, index=True)
    hashed_password: Mapped[str]      = mapped_column(String(128))
    created_at:      Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    profiles: Mapped[list[Profile]] = relationship(back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id:               Mapped[int]      = mapped_column(primary_key=True)
    user_id:          Mapped[int]      = mapped_column(ForeignKey("users.id"), index=True)
    age:              Mapped[int]
    sector:           Mapped[str]      = mapped_column(String(100))
    region:           Mapped[str]      = mapped_column(String(100))
    dependents:       Mapped[int]      = mapped_column(default=0)
    risk_tolerance:   Mapped[float]
    monthly_income:   Mapped[float]
    monthly_expenses: Mapped[float]
    current_savings:  Mapped[float]
    created_at:       Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    user:            Mapped[User]                = relationship(back_populates="profiles")
    simulation_runs: Mapped[list[SimulationRun]] = relationship(back_populates="profile")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id:                      Mapped[int]      = mapped_column(primary_key=True)
    profile_id:              Mapped[int]      = mapped_column(ForeignKey("profiles.id"), index=True)
    params_json:             Mapped[str]      = mapped_column(Text)
    percentile_results_json: Mapped[str]      = mapped_column(Text)
    created_at:              Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    profile:    Mapped[Profile]        = relationship(back_populates="simulation_runs")
    agent_logs: Mapped[list[AgentLog]] = relationship(back_populates="run")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id:             Mapped[int]        = mapped_column(primary_key=True)
    run_id:         Mapped[int]        = mapped_column(ForeignKey("simulation_runs.id"), index=True)
    agent_name:     Mapped[str]        = mapped_column(String(64))
    input_summary:  Mapped[str | None] = mapped_column(Text)
    output_summary: Mapped[str | None] = mapped_column(Text)
    guardrail_flag: Mapped[str | None] = mapped_column(Text)
    created_at:     Mapped[datetime]   = mapped_column(default=lambda: datetime.now(timezone.utc))

    run: Mapped[SimulationRun] = relationship(back_populates="agent_logs")
