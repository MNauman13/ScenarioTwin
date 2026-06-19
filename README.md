# ScenarioTwin

A multi-agent financial future simulator that models a person's financial future using Monte Carlo simulation with realistic, *correlated* shocks — job loss, market downturns, and major life events — instead of the static or independently-simulated projections most robo-advisors rely on.

> **Status**: Phase 0 scaffold complete. See [`docs/PRD.md`](docs/PRD.md) for the full specification and build roadmap.

## Architecture

| Service | Role |
|---|---|
| `api-gateway` | Single internet-facing entry point: auth, routing, rate limits |
| `simulation-engine` | Monte Carlo + HMM regime-switching model |
| `agent-orchestration` | LangGraph multi-agent layer (profile-builder, parameter-translator, narrator, guardrail) |
| `data-ingestion` | Scheduled job pulling ONS / BoE / market data |
| `llm-gateway` | Self-hosted LiteLLM: routes LLM calls, tracks cost |
| `frontend` | Next.js dashboard with probability fan chart and what-if chat |

## Quick start (development)

```bash
cp .env.example .env
# Fill in real values in .env (never commit this file)
docker compose up --build
```

Gateway available at `http://localhost:8000`. Docs at `http://localhost:8000/docs`.

## Repository layout

```
services/          # One folder per microservice
frontend/          # Next.js app
infra/caddy/       # Reverse proxy / TLS config
docs/              # PRD and architecture notes
evals/             # Calibration backtests and guardrail adversarial suite
```

## Development roadmap

See [`docs/PRD.md §15`](docs/PRD.md) for the full phase-by-phase build plan.

| Phase | Focus | Status |
|---|---|---|
| 0 | Scaffold, gitignore, env template | ✅ Done |
| 1 | Data ingestion (ONS, BoE, market returns) | 🔜 Next |
| 2 | Simulation engine (HMM, Monte Carlo) | — |
| 3 | Agent orchestration + RAG | — |
| 4 | API gateway + security hardening | — |
| 5 | Frontend | — |
| 6 | Evals + pre-deployment security review | — |
| 7 | Containerization + deployment | — |
| 8 | Polish + framing | — |
