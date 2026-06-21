from __future__ import annotations

import json
import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..cache import get as cache_get, set as cache_set
from ..config import settings
from ..database import get_db
from ..limiter import limiter
from ..models import Profile, SimulationRun, User
from ..schemas import SimulateRequest, SimulationResult

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["simulation"])


@router.post("/simulate", response_model=SimulationResult)
@limiter.limit("20/minute")
def simulate(
    request: Request,
    req: SimulateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SimulationResult:
    profile = db.query(Profile).filter(
        Profile.id == req.profile_id,
        Profile.user_id == user.id,
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    scenario = req.scenario.model_dump()

    # Cache hit — skip simulation entirely
    cached = cache_get(profile.id, scenario)
    if cached:
        logger.info("simulate: cache hit profile=%d", profile.id)
        return SimulationResult(id=cached["id"], cached=True, **cached["result"])

    # Forward to simulation engine
    payload = {
        "profile": {
            "age":              profile.age,
            "sector":           profile.sector,
            "region":           profile.region,
            "risk_tolerance":   profile.risk_tolerance,
            "current_savings":  profile.current_savings,
            "monthly_income":   profile.monthly_income,
            "monthly_expenses": profile.monthly_expenses,
        },
        "scenario": scenario,
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(f"{settings.simulation_engine_url}/simulate", json=payload)
        resp.raise_for_status()
        sim = resp.json()
    except httpx.HTTPError:
        logger.exception("Simulation engine unreachable")
        raise HTTPException(status_code=502, detail="Simulation engine unavailable")

    # Persist
    run = SimulationRun(
        profile_id=profile.id,
        params_json=json.dumps(scenario),
        percentile_results_json=json.dumps(sim["fan_chart"]),
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    result = {
        "fan_chart":        sim["fan_chart"],
        "regime_fractions": sim["regime_fractions"],
        "shock_summary":    sim["shock_summary"],
    }
    cache_set(profile.id, scenario, {"id": run.id, "result": result})

    return SimulationResult(id=run.id, **result)


@router.get("/results/{run_id}", response_model=SimulationResult)
def get_result(
    run_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SimulationResult:
    run = (
        db.query(SimulationRun)
        .join(Profile)
        .filter(SimulationRun.id == run_id, Profile.user_id == user.id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail="Result not found")

    return SimulationResult(
        id=run.id,
        fan_chart=json.loads(run.percentile_results_json),
        regime_fractions={},
        shock_summary={},
    )
