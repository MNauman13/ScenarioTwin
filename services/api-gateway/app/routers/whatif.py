from __future__ import annotations

import json
import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..config import settings
from ..database import get_db
from ..limiter import limiter
from ..models import AgentLog, Profile, SimulationRun, User
from ..schemas import WhatIfRequest, WhatIfResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/v1", tags=["whatif"])


@router.post("/whatif", response_model=WhatIfResponse)
@limiter.limit("10/minute")
def whatif(
    request: Request,
    req: WhatIfRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> WhatIfResponse:
    profile = db.query(Profile).filter(
        Profile.id == req.profile_id,
        Profile.user_id == user.id,
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_dict = {
        "age":              profile.age,
        "sector":           profile.sector,
        "region":           profile.region,
        "risk_tolerance":   profile.risk_tolerance,
        "current_savings":  profile.current_savings,
        "monthly_income":   profile.monthly_income,
        "monthly_expenses": profile.monthly_expenses,
    }

    try:
        with httpx.Client(timeout=60.0) as client:
            resp = client.post(
                f"{settings.agent_orchestration_url}/orchestrate",
                json={"user_message": req.user_message, "existing_profile": profile_dict},
            )
        resp.raise_for_status()
        result = resp.json()
    except httpx.HTTPError:
        logger.exception("Agent orchestration unreachable")
        raise HTTPException(status_code=502, detail="Agent orchestration unavailable")

    # Persist run + agent logs in a single transaction
    run = SimulationRun(
        profile_id=profile.id,
        params_json=json.dumps(result.get("sim_params", {})),
        percentile_results_json=json.dumps(result.get("fan_chart", {})),
    )
    db.add(run)
    db.flush()  # get run.id before inserting agent logs

    for log in result.get("agent_logs", []):
        db.add(AgentLog(
            run_id=run.id,
            agent_name=log.get("agent", "unknown"),
            output_summary=json.dumps(log),
            guardrail_flag=result["guardrail"].get("flag"),
        ))
    db.commit()

    return WhatIfResponse(
        narrative=result["narrative"],
        fan_chart=result["fan_chart"],
        regime_fractions=result["regime_fractions"],
        shock_summary=result["shock_summary"],
        guardrail=result["guardrail"],
    )
