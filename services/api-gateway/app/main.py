from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .database import Base, engine
from . import models  # noqa: F401 — registers all tables with Base.metadata before create_all
from .limiter import limiter
from .routers import auth, profile, simulate, whatif

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Creating DB tables if needed")
    Base.metadata.create_all(bind=engine)
    logger.info("API gateway ready")
    yield
    logger.info("Shutdown")


app = FastAPI(
    title="ScenarioTwin API Gateway",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(simulate.router)
app.include_router(whatif.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
