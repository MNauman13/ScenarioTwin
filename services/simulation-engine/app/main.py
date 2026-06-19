from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text

from .config import settings
from .engine import hmm_model as _hmm
from .engine import monte_carlo as _mc
from .schemas import FanChart, SimulationRequest, SimulationResponse

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


# ONS unemployment rate cache
_ons_rates: dict[str, float] = {}

def _load_ons_rates() -> None:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT sector, region, rate_pct "
                "FROM unemployment_rates WHERE age_band = 'All'"
            )
        ).fetchall()
    engine.dispose()
    for row in rows:
        _ons_rates[f"{row.sector}|{row.region}"] = float(row.rate_pct)
    logger.info("Loaded %d ONS unemployment rate entries", len(_ons_rates))

def _base_job_loss_rate(sector: str, region: str) -> float:
    """
    Combines sector and region unemployment rates multiplicatively.
    If a dimension is missing from ONS cache, falls back to national average.
    """
    national_pct = _ons_rates.get("All|Great Britain", 4.0)
    sector_pct   = _ons_rates.get(f"{sector}|Great Britain", national_pct)
    region_pct   = _ons_rates.get(f"All|{region}", national_pct)

    national = national_pct / 100
    # Multiplicative combination: adjust national baseline by sector and region factors
    combined = national * (sector_pct / national_pct) * (region_pct / national_pct)
    return float(combined)


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: training HMM regime model")
    _hmm.regime_model.train(settings.database_url)
    logger.info("Startup: loading ONS unemployment rates")
    _load_ons_rates()
    logger.info("Startup complete — ready to simulate")
    yield
    logger.info("Shutdown")


app = FastAPI(
    title="ScenarioTwin — Simulation Engine",
    version="0.1.0",
    lifespan=lifespan,
)


# Endpoints
@app.get("/health")
def health() -> dict[str, str]:
    if not _hmm.regime_model.is_trained:
        raise HTTPException(status_code=503, detail="HMM model not yet ready")
    return {"status": "ok"}


@app.post("/simulate", response_model=SimulationResponse)
def simulate(req: SimulationRequest) -> SimulationResponse:
    if not _hmm.regime_model.is_trained:
        raise HTTPException(status_code=503, detail="HMM model not yet ready")

    p = req.profile
    s = req.scenario

    result = _mc.run(
        _mc.SimulationInput(
            age=p.age,
            monthly_income=p.monthly_income,
            monthly_expenses=p.monthly_expenses,
            current_savings=p.current_savings,
            base_annual_job_loss_rate=_base_job_loss_rate(p.sector, p.region),
            risk_tolerance=p.risk_tolerance,
            years=s.years_to_simulate,
            extra_monthly=s.extra_monthly_contribution,
            n_paths=settings.n_simulation_paths,
            seed=settings.random_seed,
        ),
        _hmm.regime_model,
    )

    return SimulationResponse(
        fan_chart=FanChart(
            years=result.years,
            p10=result.percentiles["p10"],
            p25=result.percentiles["p25"],
            p50=result.percentiles["p50"],
            p75=result.percentiles["p75"],
            p90=result.percentiles["p90"],
        ),
        regime_fractions=result.regime_fractions,
        shock_summary=result.shock_summary,
        regime_params=result.regime_params,
    )