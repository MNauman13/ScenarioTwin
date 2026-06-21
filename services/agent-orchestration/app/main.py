from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException

from .config import settings
from .schemas import GuardrailResult, OrchestrationRequest, OrchestrationResponse
from .agents.graph import OrchestrationState, orchestration_graph

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Agent orchestration service ready")
    yield
    logger.info("Shutdown")

app = FastAPI(
    title="ScenarioTwin - Agent Orchestration",
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/orchestrate", response_model=OrchestrationResponse)
def orchestrate(req: OrchestrationRequest) -> OrchestrationResponse:
    initial: OrchestrationState = {
        "user_message": req.user_message,
        "existing_profile": req.existing_profile,
        "existing_params": req.existing_params,
        "profile": None,
        "sim_params": None,
        "sim_results": None,
        "raw_narrative": None,
        "final_narrative": None,
        "guardrail_flag": None,
        "agent_logs": []
    }

    try:
        final: OrchestrationState = orchestration_graph.invoke(initial)
    except Exception as e:
        logger.exception("Orchestration pipeline failed")
        raise HTTPException(status_code=500, detail=str(e))
    
    
    sim = final["sim_results"]
    return OrchestrationResponse(
        profile=final["profile"],
        sim_params=final["sim_params"],
        narrative=final["final_narrative"],
        fan_chart=sim["fan_chart"],
        regime_fractions=sim["regime_fractions"],
        shock_summary=sim["shock_summary"],
        guardrail=GuardrailResult(
            passed=final["guardrail_flag"] is None,
            flag=final["guardrail_flag"],
        ),
        agent_logs=final["agent_logs"]
    )