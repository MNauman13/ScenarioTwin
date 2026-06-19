# ScenarioTwin — Claude working context

Full PRD is at `docs/PRD.md`. This file is the quick-reference so you don't re-read the PRD every session.

## What this project is

Multi-agent financial future simulator. Core value prop: Monte Carlo simulation with **correlated** shocks (job loss + market downturn at the same time, via an HMM regime-switching model) — unlike typical robo-advisor calculators that treat these as independent. Built as a portfolio/interview project for Nauman.

## Services (all in `services/`)

| Service | Port (internal) | Tech | Purpose |
|---|---|---|---|
| `api-gateway` | 8000 (only public port) | FastAPI | Auth, routing, rate limiting |
| `simulation-engine` | 8001 | FastAPI + numpy/hmmlearn | Monte Carlo + HMM |
| `agent-orchestration` | 8002 | FastAPI + LangGraph | 4 agents: profile-builder, parameter-translator, narrator, guardrail |
| `data-ingestion` | — (one-shot script) | Python | ONS, BoE, market data |
| `llm-gateway` | 4000 | LiteLLM | LLM routing + cost tracking |
| `frontend` | 3000 | Next.js + Recharts | Fan chart + what-if chat UI |

## Key design decisions

- **Only `api-gateway` is internet-facing** — all other services are on a private Docker network with no exposed ports.
- **Secrets** are never committed — `.env.example` has placeholders, real `.env` is gitignored. Pre-commit secret scanning (gitleaks) added in Phase 3 before any real API keys enter the project.
- **LLM routing** via LiteLLM: cheap models (Groq/Gemini Flash) for parameter translation; stronger model (Anthropic Claude Haiku) for guardrail. Cost target: under £5/month LLM spend.
- **Redis cache** key = SHA256(profile_id + scenario_params), TTL 1h. Cache hit skips simulation entirely.
- **HMM states**: "normal", "recession", "crisis" — drives both market returns AND job-loss probability jointly (correlation is the key differentiator).
- **Guardrail agent**: compliance control, not a nice-to-have. Zero advice-framed outputs is a hard success metric. Disallowed phrasings include "you should", "I recommend", "buy X".

## Database schema

```sql
profiles(id, age, sector, region, dependents, risk_tolerance, created_at)
simulation_runs(id, profile_id, params_json, percentile_results_json, created_at)
shock_events(id, run_id, shock_type, path_index, year_offset)
agent_logs(id, run_id, agent_name, input_summary, output_summary, guardrail_flag, created_at)
```

## Real data sources

| Source | What it provides |
|---|---|
| ONS Labour Force Survey | Unemployment probability by age, sector, region |
| Bank of England database API | Historical interest rate paths |
| Stooq / Yahoo Finance | Historical market return series (block-bootstrapped) |
| ONS life-event statistics | Redundancy, illness probabilities |
| FCA Handbook (PERG) | Advice-vs-guidance rules for guardrail |

## API endpoints (gateway)

```
POST /v1/profile
POST /v1/simulate
POST /v1/whatif
GET  /v1/results/{id}
GET  /health
```

## Build phases

| Phase | Status | Branch pattern |
|---|---|---|
| 0 — Scaffold | ✅ Done | main |
| 1 — Data ingestion | 🔜 Next | feature/data-ingestion |
| 2 — Simulation engine | — | feature/simulation-engine |
| 3 — Agent orchestration + RAG | — | feature/agent-orchestration |
| 4 — API gateway + security | — | feature/api-gateway |
| 5 — Frontend | — | feature/frontend |
| 6 — Evals + security review | — | feature/evals |
| 7 — Containerization + deploy | — | feature/deploy |
| 8 — Polish | — | main |

## Security controls timeline

| Control | Phase introduced |
|---|---|
| `.gitignore`, `.env.example` | 0 ✅ |
| gitleaks pre-commit hook | 3 (before first real API key) |
| Input validation on gateway endpoints | 4 |
| JWT auth + rate limiting | 4 |
| HTTPS/TLS via Caddy | 7 |
| `pip-audit` + `npm audit` in CI | 6 |
| Full git history secret scan | 6 |
| Guardrail adversarial test suite | 6 |

## Testing strategy

- **Unit** (`pytest`): simulation math, agent parameter parsing, guardrail phrase matching
- **Integration** (`pytest` + Docker Compose): gateway-to-service calls, cache hit/miss
- **Eval** (custom harness in `evals/`): calibration accuracy, narrator faithfulness, guardrail adversarial suite
- **CI** (GitHub Actions): runs all of the above on every push; blocks merge on failure

## Performance targets

- What-if on cache hit: < 6s end-to-end
- What-if on full re-run: < 20s
- Cost: < £10/month total (LLM spend < £5/month)

## Infra

- Compute: Oracle Cloud free-tier ARM VM
- Reverse proxy/TLS: Caddy (auto Let's Encrypt)
- DB: self-hosted Postgres 16 + Redis 7 on same VM
- CI/CD: GitHub Actions free tier
- Data ingestion: GitHub Actions scheduled jobs (not always-on container)
