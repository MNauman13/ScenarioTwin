# Product Requirements Document: ScenarioTwin

**A multi-agent financial future simulator**

| | |
|---|---|
| Version | 1.0 |
| Status | Draft for implementation |
| Owner | Nauman |
| Last updated | 18 June 2026 |

---

## 1. Executive summary

ScenarioTwin models a person's financial future using Monte Carlo simulation with realistic, *correlated* shocks — job loss, market downturns, major life events — instead of the static or independently-simulated projections most robo-advisors and retirement calculators rely on. A multi-agent AI layer sits on top of the simulation core to translate plain-English questions into scenario parameters and to narrate results faithfully, with guardrails keeping every output on the "guidance," not "advice," side of UK financial regulation. The whole system is built as a set of independently deployable microservices, runs entirely on free public data, and is designed to cost under £10/month indefinitely.

This document is both a specification and a build plan: it covers what the system does, how its components fit together, and — section 15 in particular — exactly what to build in what order, including when security controls, tests, and repository practices get introduced.

## 2. Problem statement

Robo-advisor projections and retirement calculators have a well-known, rarely-discussed flaw: they treat market returns and personal income shocks as statistically independent. In reality they are not — job losses cluster during recessions, which is exactly when markets are also down. This is called sequence-of-returns risk in actuarial literature, and it is one of the most damaging real risks in financial planning, yet almost no consumer-facing tool models it. People are left choosing between an oversimplified single number ("you'll have £350,000 at 65") or a spreadsheet too complex to act on, with no calibrated sense of how confident that number actually is.

## 3. Goals

| ID | Goal |
|---|---|
| G1 | Demonstrate genuine statistical modeling — regime-switching, bootstrapped returns, correlated shocks — not just an LLM wrapper around a simple formula |
| G2 | Demonstrate a real multi-agent AI system with tool use, retrieval, guardrails, and evaluation — not a single prompt |
| G3 | Demonstrate production-style engineering: microservices, containerization, CI/CD, and security hygiene |
| G4 | Run entirely on real, free, public data — no synthetic data, no privacy-sensitive data |
| G5 | Stay under £10/month in running costs indefinitely |
| G6 | Be explainable in one paragraph and defensible in depth across data science, AI engineering, and software engineering interview questions |

## 4. Non-goals

- Not regulated financial advice, and must never present itself as such.
- No live Open Banking integration with real user accounts at v1 — that is a stretch goal, not part of the MVP.
- Not built for production multi-tenant scale; the architecture demonstrates the pattern rather than serving large concurrent load.
- Web only; no native mobile app.

## 5. Target audience

The primary audience for this document and the project itself is technical interviewers and recruiters evaluating data science, AI engineering, and software engineering internship applications. The secondary, in-product persona is a person exploring how different decisions and shocks could affect their financial future — this persona is used to ground UX and copy decisions, even though the project has no real user base.

## 6. Success metrics

| Metric | Target |
|---|---|
| Calibration accuracy | Stated probabilities (e.g. "70% chance of X") hold within a defined tolerance when backtested against historical cohorts |
| Guardrail integrity | Zero advice-framed outputs across the adversarial guardrail test set |
| What-if response latency | Under 6 seconds for a cached simulation re-run, end to end |
| Engineering hygiene | Clean CI, no secrets in git history, dependency scan passing, README complete with working demo |
| Cost | Under £10/month measured across a full month of operation |

## 7. System architecture

![System architecture overview](data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNzAwIiBoZWlnaHQ9IjY0MCIgdmlld0JveD0iMCAwIDcwMCA2NDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgo8ZGVmcz4KPG1hcmtlciBpZD0iYXJyb3ciIHZpZXdCb3g9IjAgMCAxMCAxMCIgcmVmWD0iOCIgcmVmWT0iNSIgbWFya2VyV2lkdGg9IjYiIG1hcmtlckhlaWdodD0iNiIgb3JpZW50PSJhdXRvLXN0YXJ0LXJldmVyc2UiPgo8cGF0aCBkPSJNMiAxTDggNUwyIDkiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzVGNUU1QSIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L21hcmtlcj4KPC9kZWZzPgo8cmVjdCB3aWR0aD0iNzAwIiBoZWlnaHQ9IjY0MCIgZmlsbD0iI0ZGRkZGRiIvPgoKPHJlY3QgeD0iMjAwIiB5PSI0MCIgd2lkdGg9IjMwMCIgaGVpZ2h0PSI1NiIgcng9IjgiIGZpbGw9IiNGMUVGRTgiIHN0cm9rZT0iIzg4ODc4MCIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjx0ZXh0IHg9IjM1MCIgeT0iNjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMyQzJDMkEiPkZyb250ZW5kPC90ZXh0Pgo8dGV4dCB4PSIzNTAiIHk9IjgwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj5OZXh0LmpzIGRhc2hib2FyZCwgZmFuIGNoYXJ0czwvdGV4dD4KCjxsaW5lIHgxPSIzNTAiIHkxPSI5NiIgeDI9IjM1MCIgeTI9IjE1NiIgc3Ryb2tlPSIjNUY1RTVBIiBzdHJva2Utd2lkdGg9IjEuNSIgbWFya2VyLWVuZD0idXJsKCNhcnJvdykiLz4KCjxyZWN0IHg9IjIwMCIgeT0iMTU2IiB3aWR0aD0iMzAwIiBoZWlnaHQ9IjU2IiByeD0iOCIgZmlsbD0iI0YxRUZFOCIgc3Ryb2tlPSIjODg4NzgwIiBzdHJva2Utd2lkdGg9IjEiLz4KPHRleHQgeD0iMzUwIiB5PSIxNzYiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMyQzJDMkEiPkFQSSBnYXRld2F5PC90ZXh0Pgo8dGV4dCB4PSIzNTAiIHk9IjE5NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+QXV0aCwgcm91dGluZywgcmF0ZSBsaW1pdHM8L3RleHQ+Cgo8bGluZSB4MT0iMjgwIiB5MT0iMjEyIiB4Mj0iMjAwIiB5Mj0iMjcyIiBzdHJva2U9IiM1RjVFNUEiIHN0cm9rZS13aWR0aD0iMS41IiBtYXJrZXItZW5kPSJ1cmwoI2Fycm93KSIvPgo8bGluZSB4MT0iNDIwIiB5MT0iMjEyIiB4Mj0iNTAwIiB5Mj0iMjcyIiBzdHJva2U9IiM1RjVFNUEiIHN0cm9rZS13aWR0aD0iMS41IiBtYXJrZXItZW5kPSJ1cmwoI2Fycm93KSIvPgoKPHJlY3QgeD0iNjAiIHk9IjI3MiIgd2lkdGg9IjI4MCIgaGVpZ2h0PSI1NiIgcng9IjgiIGZpbGw9IiNFMUY1RUUiIHN0cm9rZT0iIzVEQ0FBNSIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjx0ZXh0IHg9IjIwMCIgeT0iMjkyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iNjAwIiBmaWxsPSIjMDQzNDJDIj5TaW11bGF0aW9uIGVuZ2luZTwvdGV4dD4KPHRleHQgeD0iMjAwIiB5PSIzMTIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiMwRjZFNTYiPk1vbnRlIENhcmxvICsgSE1NIHJlZ2ltZXM8L3RleHQ+Cgo8cmVjdCB4PSIzNjAiIHk9IjI3MiIgd2lkdGg9IjI4MCIgaGVpZ2h0PSI1NiIgcng9IjgiIGZpbGw9IiNFRUVERkUiIHN0cm9rZT0iI0FGQTlFQyIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjx0ZXh0IHg9IjUwMCIgeT0iMjkyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iNjAwIiBmaWxsPSIjMjYyMTVDIj5BZ2VudCBvcmNoZXN0cmF0aW9uPC90ZXh0Pgo8dGV4dCB4PSI1MDAiIHk9IjMxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzUzNEFCNyI+TGFuZ0dyYXBoIG11bHRpLWFnZW50IGxheWVyPC90ZXh0PgoKPGxpbmUgeDE9IjIwMCIgeTE9IjMyOCIgeDI9IjM1MCIgeTI9IjM4OCIgc3Ryb2tlPSIjNUY1RTVBIiBzdHJva2Utd2lkdGg9IjEuNSIgbWFya2VyLWVuZD0idXJsKCNhcnJvdykiLz4KPGxpbmUgeDE9IjUwMCIgeTE9IjMyOCIgeDI9IjM1MCIgeTI9IjM4OCIgc3Ryb2tlPSIjNUY1RTVBIiBzdHJva2Utd2lkdGg9IjEuNSIgbWFya2VyLWVuZD0idXJsKCNhcnJvdykiLz4KCjxyZWN0IHg9IjIwMCIgeT0iMzg4IiB3aWR0aD0iMzAwIiBoZWlnaHQ9IjU2IiByeD0iOCIgZmlsbD0iI0YxRUZFOCIgc3Ryb2tlPSIjODg4NzgwIiBzdHJva2Utd2lkdGg9IjEiLz4KPHRleHQgeD0iMzUwIiB5PSI0MDgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMyQzJDMkEiPkRhdGEgbGF5ZXI8L3RleHQ+Cjx0ZXh0IHg9IjM1MCIgeT0iNDI4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj5Qb3N0Z3JlcyAocmVzdWx0cykgKyBSZWRpcyBjYWNoZTwvdGV4dD4KCjxsaW5lIHgxPSIzNTAiIHkxPSI1MDQiIHgyPSIzNTAiIHkyPSI0NDQiIHN0cm9rZT0iIzVGNUU1QSIgc3Ryb2tlLXdpZHRoPSIxLjUiIG1hcmtlci1lbmQ9InVybCgjYXJyb3cpIi8+Cgo8cmVjdCB4PSIyMDAiIHk9IjUwNCIgd2lkdGg9IjMwMCIgaGVpZ2h0PSI1NiIgcng9IjgiIGZpbGw9IiNGMUVGRTgiIHN0cm9rZT0iIzg4ODc4MCIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjx0ZXh0IHg9IjM1MCIgeT0iNTI0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iNjAwIiBmaWxsPSIjMkMyQzJBIj5EYXRhIGluZ2VzdGlvbiBzZXJ2aWNlPC90ZXh0Pgo8dGV4dCB4PSIzNTAiIHk9IjU0NCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+UHVsbHMgcmVhbCBPTlMsIEJvRSwgbWFya2V0IGRhdGE8L3RleHQ+Cgo8dGV4dCB4PSIzNTAiIHk9IjYwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+R3JheSA9IGludGVyZmFjZS9pbmZyYXN0cnVjdHVyZSAgfCAgVGVhbCA9IHNpbXVsYXRpb24vTUwgIHwgIFB1cnBsZSA9IEFJIGFnZW50czwvdGV4dD4KPC9zdmc+Cg==)

| Service | Responsibility | Internet-facing? |
|---|---|---|
| Frontend | Next.js dashboard rendering the probability fan chart and the what-if chat interface | Yes, via gateway only |
| API gateway | Single entry point: authentication, routing, rate limiting | Yes — the only service that is |
| Simulation engine | Monte Carlo + regime-switching model, stateless compute | No |
| Agent orchestration | LangGraph multi-agent layer (profile-builder, parameter-translator, narrator, guardrail) | No |
| Data layer | Postgres (results, profiles) + Redis (cache) | No |
| Data ingestion | Scheduled job pulling real ONS/BoE/market data | No |
| LLM gateway | Self-hosted LiteLLM instance routing/caching/cost-tracking LLM calls | No |

## 8. Detailed service specifications

### 8.1 Frontend

- **Tech**: Next.js, React, Tailwind, a charting library (Recharts) for the percentile fan chart.
- **Responsibilities**: render the simulation's outcome distribution, host the conversational what-if interface, never call any internal service directly — every request goes through the API gateway.
- **Key screens**: profile setup, fan chart + narrative summary, what-if chat panel.

### 8.2 API gateway

- **Tech**: FastAPI (or a lightweight reverse proxy like Caddy in front of FastAPI for TLS termination).
- **Responsibilities**: validate auth tokens, enforce per-user rate limits, route requests to the simulation engine or agent orchestration service, and is the only container with an open inbound port.
- **Key endpoints**: `POST /v1/profile`, `POST /v1/simulate`, `POST /v1/whatif`, `GET /v1/results/{id}`.

### 8.3 Simulation engine service

- **Tech**: Python, numpy/numba for vectorized Monte Carlo, `hmmlearn` or a custom regime-switching implementation, exposed internally via gRPC or a simple internal REST API.
- **Responsibilities**: given a profile and scenario parameters, run N simulated life paths and return percentile bands, not raw paths, to keep payloads small.
- **Inputs**: age, sector, region, dependents, savings rate, risk tolerance, and any what-if overrides.
- **Outputs**: percentile distribution of net worth over time, plus metadata on which shocks drove the worst-case paths.

### 8.4 Agent orchestration service

- **Tech**: Python, LangGraph, calling the simulation engine and the RAG/knowledge store as tools.
- **Agents**:
  - *Profile-builder* — turns a short conversation or onboarding form into simulation parameters.
  - *Parameter-translator (what-if)* — turns a natural-language follow-up into a parameter delta and re-invokes the simulation engine.
  - *Narrator* — turns raw percentile output into a plain-English explanation, citing the specific shocks behind worst-case paths.
  - *Guardrail* — reviews every outbound message against the advice-vs-guidance rule before it is returned.
- **Dependencies**: calls the LLM gateway for all model calls, never an LLM API directly, so cost and latency are tracked centrally.

### 8.5 Data layer

- **Postgres**: `profiles`, `simulation_runs`, `shock_events`, `agent_logs` tables (see section 9.2).
- **Redis**: caches simulation results keyed by a hash of profile + scenario parameters, with a short TTL, so a repeated what-if doesn't recompute from scratch.

### 8.6 Data ingestion service

- **Tech**: Python, scheduled via GitHub Actions (not an always-on container, to save cost).
- **Responsibilities**: pull and refresh ONS unemployment-by-sector data, Bank of England interest rate history, and historical market return series; validate against expected ranges before writing to Postgres.

### 8.7 LLM gateway

- **Tech**: self-hosted LiteLLM.
- **Responsibilities**: route cheap tasks (parameter translation) to free-tier models (Groq, Gemini Flash) and reserve a stronger model only for the narrator and guardrail steps; log cost and latency per call.

## 9. Data architecture

### 9.1 Real data sources

| Source | Provides | Access | Cost |
|---|---|---|---|
| ONS Labour Force Survey | Unemployment probability by age, sector, region | Free bulk download / API | Free |
| Bank of England database | Historical interest rate paths | Free API | Free |
| Historical market index returns | Real return series for bootstrapping | Free (Stooq, Yahoo Finance) | Free |
| ONS life-event statistics | Probabilities for major life events | Free publications | Free |
| FCA Handbook (PERG / advice guidance) | Advice-vs-guidance rules for the guardrail agent | Public, free | Free |

### 9.2 Database schema (sketch)

```
profiles(id, age, sector, region, dependents, risk_tolerance, created_at)
simulation_runs(id, profile_id, params_json, percentile_results_json, created_at)
shock_events(id, run_id, shock_type, path_index, year_offset)
agent_logs(id, run_id, agent_name, input_summary, output_summary, guardrail_flag, created_at)
```

### 9.3 Caching policy

Cache key = SHA256 hash of `(profile_id, scenario_params)`. TTL of 1 hour. A cache hit skips the simulation engine entirely and returns straight from Redis, which is what keeps the what-if loop fast.

## 10. Agent design and request lifecycle

![What-if request lifecycle](data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNzAwIiBoZWlnaHQ9IjYwMCIgdmlld0JveD0iMCAwIDcwMCA2MDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgo8ZGVmcz4KPG1hcmtlciBpZD0iYXJyb3ciIHZpZXdCb3g9IjAgMCAxMCAxMCIgcmVmWD0iOCIgcmVmWT0iNSIgbWFya2VyV2lkdGg9IjYiIG1hcmtlckhlaWdodD0iNiIgb3JpZW50PSJhdXRvLXN0YXJ0LXJldmVyc2UiPgo8cGF0aCBkPSJNMiAxTDggNUwyIDkiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzVGNUU1QSIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L21hcmtlcj4KPC9kZWZzPgo8cmVjdCB3aWR0aD0iNzAwIiBoZWlnaHQ9IjYwMCIgZmlsbD0iI0ZGRkZGRiIvPgoKPHJlY3QgeD0iMjAwIiB5PSI0MCIgd2lkdGg9IjMwMCIgaGVpZ2h0PSI1NiIgcng9IjgiIGZpbGw9IiNGMUVGRTgiIHN0cm9rZT0iIzg4ODc4MCIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjx0ZXh0IHg9IjM1MCIgeT0iNjAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMyQzJDMkEiPlVzZXIgcXVlc3Rpb248L3RleHQ+Cjx0ZXh0IHg9IjM1MCIgeT0iODAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPmUuZy4gc3dpdGNoaW5nIHRvIGEgc2FmZXIgam9iPC90ZXh0PgoKPGxpbmUgeDE9IjM1MCIgeTE9Ijk2IiB4Mj0iMzUwIiB5Mj0iMTU2IiBzdHJva2U9IiM1RjVFNUEiIHN0cm9rZS13aWR0aD0iMS41IiBtYXJrZXItZW5kPSJ1cmwoI2Fycm93KSIvPgoKPHJlY3QgeD0iMjAwIiB5PSIxNTYiIHdpZHRoPSIzMDAiIGhlaWdodD0iNTYiIHJ4PSI4IiBmaWxsPSIjRUVFREZFIiBzdHJva2U9IiNBRkE5RUMiIHN0cm9rZS13aWR0aD0iMSIvPgo8dGV4dCB4PSIzNTAiIHk9IjE3NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjYwMCIgZmlsbD0iIzI2MjE1QyI+UGFyYW1ldGVyLWJ1aWxkaW5nIGFnZW50PC90ZXh0Pgo8dGV4dCB4PSIzNTAiIHk9IjE5NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzUzNEFCNyI+VHVybnMgaW50ZW50IGludG8gc2ltdWxhdGlvbiBpbnB1dHM8L3RleHQ+Cgo8bGluZSB4MT0iMzUwIiB5MT0iMjEyIiB4Mj0iMzUwIiB5Mj0iMjcyIiBzdHJva2U9IiM1RjVFNUEiIHN0cm9rZS13aWR0aD0iMS41IiBtYXJrZXItZW5kPSJ1cmwoI2Fycm93KSIvPgoKPHJlY3QgeD0iMjAwIiB5PSIyNzIiIHdpZHRoPSIzMDAiIGhlaWdodD0iNTYiIHJ4PSI4IiBmaWxsPSIjRTFGNUVFIiBzdHJva2U9IiM1RENBQTUiIHN0cm9rZS13aWR0aD0iMSIvPgo8dGV4dCB4PSIzNTAiIHk9IjI5MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjYwMCIgZmlsbD0iIzA0MzQyQyI+U2ltdWxhdGlvbiBlbmdpbmU8L3RleHQ+Cjx0ZXh0IHg9IjM1MCIgeT0iMzEyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmaWxsPSIjMEY2RTU2Ij5SZXJ1bnMgTW9udGUgQ2FybG8gd2l0aCBuZXcgaW5wdXRzPC90ZXh0PgoKPGxpbmUgeDE9IjM1MCIgeTE9IjMyOCIgeDI9IjM1MCIgeTI9IjM4OCIgc3Ryb2tlPSIjNUY1RTVBIiBzdHJva2Utd2lkdGg9IjEuNSIgbWFya2VyLWVuZD0idXJsKCNhcnJvdykiLz4KCjxyZWN0IHg9IjIwMCIgeT0iMzg4IiB3aWR0aD0iMzAwIiBoZWlnaHQ9IjU2IiByeD0iOCIgZmlsbD0iI0VFRURGRSIgc3Ryb2tlPSIjQUZBOUVDIiBzdHJva2Utd2lkdGg9IjEiLz4KPHRleHQgeD0iMzUwIiB5PSI0MDgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMyNjIxNUMiPk5hcnJhdG9yICsgZ3VhcmRyYWlsIGFnZW50PC90ZXh0Pgo8dGV4dCB4PSIzNTAiIHk9IjQyOCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzUzNEFCNyI+RXhwbGFpbnMgcmVzdWx0LCBjaGVja3MgY29tcGxpYW5jZTwvdGV4dD4KCjxsaW5lIHgxPSIzNTAiIHkxPSI0NDQiIHgyPSIzNTAiIHkyPSI1MDQiIHN0cm9rZT0iIzVGNUU1QSIgc3Ryb2tlLXdpZHRoPSIxLjUiIG1hcmtlci1lbmQ9InVybCgjYXJyb3cpIi8+Cgo8cmVjdCB4PSIyMDAiIHk9IjUwNCIgd2lkdGg9IjMwMCIgaGVpZ2h0PSI1NiIgcng9IjgiIGZpbGw9IiNGMUVGRTgiIHN0cm9rZT0iIzg4ODc4MCIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjx0ZXh0IHg9IjM1MCIgeT0iNTI0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iNjAwIiBmaWxsPSIjMkMyQzJBIj5SZXNwb25zZSBzaG93biB0byB1c2VyPC90ZXh0Pgo8dGV4dCB4PSIzNTAiIHk9IjU0NCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzVGNUU1QSI+UGxhaW4tRW5nbGlzaCBleHBsYW5hdGlvbiArIGNoYXJ0PC90ZXh0PgoKPHRleHQgeD0iMzUwIiB5PSI1ODAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPkdyYXkgPSB1c2VyLWZhY2luZyBzdGVwICB8ICBQdXJwbGUgPSBBSSBhZ2VudCBzdGVwICB8ICBUZWFsID0gc2ltdWxhdGlvbi9NTCBzdGVwPC90ZXh0Pgo8L3N2Zz4K)

When a user asks a what-if question, the API gateway forwards it to the agent orchestration service. The parameter-translator agent does not touch the simulation directly — it converts the natural-language intent into a structured parameter delta and calls the simulation engine as a tool. The simulation engine returns raw percentile numbers with no language attached. The narrator agent turns that into plain English, and in the same pass the guardrail agent checks the draft response against the advice-vs-guidance rule and against a list of disallowed phrasings (e.g. "you should," "I recommend buying"). Only after that check passes does the response return through the gateway.

## 11. ML and statistical methodology

- **Regime-switching model**: a Hidden Markov Model with "normal," "recession," and "crisis" states drives both market returns and job-loss probability simultaneously, so the two are correlated the way they are historically, rather than simulated independently.
- **Bootstrapped returns**: market returns are resampled in blocks from real historical data (preserving autocorrelation and crash clustering) rather than drawn from a normal distribution.
- **Conditional life-event probabilities**: redundancy, illness, and other shocks are sampled from real probability tables conditioned on age, sector, and region, not generic averages.
- **Calibration testing**: the model's stated probabilities are checked against real historical cohorts — if it claims a 70% chance of an outcome, that should hold roughly 70% of the time in backtests. This is the same idea behind conformal prediction and reliability diagrams.

## 12. Security and compliance design

![Security and trust boundary](data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNzAwIiBoZWlnaHQ9IjUyMCIgdmlld0JveD0iMCAwIDcwMCA1MjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgZm9udC1mYW1pbHk9IkhlbHZldGljYSwgQXJpYWwsIHNhbnMtc2VyaWYiPgo8ZGVmcz4KPG1hcmtlciBpZD0iYXJyb3ciIHZpZXdCb3g9IjAgMCAxMCAxMCIgcmVmWD0iOCIgcmVmWT0iNSIgbWFya2VyV2lkdGg9IjYiIG1hcmtlckhlaWdodD0iNiIgb3JpZW50PSJhdXRvLXN0YXJ0LXJldmVyc2UiPgo8cGF0aCBkPSJNMiAxTDggNUwyIDkiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzVGNUU1QSIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L21hcmtlcj4KPC9kZWZzPgo8cmVjdCB3aWR0aD0iNzAwIiBoZWlnaHQ9IjUyMCIgZmlsbD0iI0ZGRkZGRiIvPgoKPHJlY3QgeD0iMjUwIiB5PSIyMCIgd2lkdGg9IjIwMCIgaGVpZ2h0PSI1MCIgcng9IjgiIGZpbGw9IiNGMUVGRTgiIHN0cm9rZT0iIzg4ODc4MCIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjx0ZXh0IHg9IjM1MCIgeT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMyQzJDMkEiPlVzZXIncyBicm93c2VyPC90ZXh0Pgo8dGV4dCB4PSIzNTAiIHk9IjU4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj5QdWJsaWMgaW50ZXJuZXQ8L3RleHQ+Cgo8bGluZSB4MT0iMzUwIiB5MT0iNzAiIHgyPSIzNTAiIHkyPSIxMDAiIHN0cm9rZT0iIzVGNUU1QSIgc3Ryb2tlLXdpZHRoPSIxLjUiIG1hcmtlci1lbmQ9InVybCgjYXJyb3cpIi8+Cgo8cmVjdCB4PSIyMDAiIHk9IjEwMCIgd2lkdGg9IjMwMCIgaGVpZ2h0PSI2MCIgcng9IjgiIGZpbGw9IiNGQUVFREEiIHN0cm9rZT0iI0VGOUYyNyIgc3Ryb2tlLXdpZHRoPSIxLjUiLz4KPHRleHQgeD0iMzUwIiB5PSIxMjIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiM0MTI0MDIiPkFQSSBnYXRld2F5PC90ZXh0Pgo8dGV4dCB4PSIzNTAiIHk9IjE0MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzg1NEYwQiI+T25seSBwdWJsaWMgZW50cnkgcG9pbnQ6IEhUVFBTLCBhdXRoLCByYXRlIGxpbWl0czwvdGV4dD4KCjxsaW5lIHgxPSIzNTAiIHkxPSIxNjAiIHgyPSIzNTAiIHkyPSIyMTAiIHN0cm9rZT0iIzVGNUU1QSIgc3Ryb2tlLXdpZHRoPSIxLjUiIG1hcmtlci1lbmQ9InVybCgjYXJyb3cpIi8+Cgo8cmVjdCB4PSI4MCIgeT0iMjEwIiB3aWR0aD0iNTQwIiBoZWlnaHQ9IjIxMCIgcng9IjEyIiBmaWxsPSJub25lIiBzdHJva2U9IiM4ODg3ODAiIHN0cm9rZS13aWR0aD0iMS41IiBzdHJva2UtZGFzaGFycmF5PSI2IDUiLz4KPHRleHQgeD0iMTAwIiB5PSIyMzUiIGZvbnQtc2l6ZT0iMTMiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiM0NDQ0NDEiPlByaXZhdGUgbmV0d29yayDigJQgbm90IHJlYWNoYWJsZSBmcm9tIHRoZSBpbnRlcm5ldDwvdGV4dD4KCjxyZWN0IHg9IjExMCIgeT0iMjUwIiB3aWR0aD0iMjMwIiBoZWlnaHQ9IjYwIiByeD0iOCIgZmlsbD0iI0UxRjVFRSIgc3Ryb2tlPSIjNURDQUE1IiBzdHJva2Utd2lkdGg9IjEiLz4KPHRleHQgeD0iMjI1IiB5PSIyNzIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTQiIGZvbnQtd2VpZ2h0PSI2MDAiIGZpbGw9IiMwNDM0MkMiPlNpbXVsYXRpb24gZW5naW5lPC90ZXh0Pgo8dGV4dCB4PSIyMjUiIHk9IjI5MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxMiIgZmlsbD0iIzBGNkU1NiI+Tm8gZXh0ZXJuYWwgYWNjZXNzPC90ZXh0PgoKPHJlY3QgeD0iMzcwIiB5PSIyNTAiIHdpZHRoPSIyMzAiIGhlaWdodD0iNjAiIHJ4PSI4IiBmaWxsPSIjRUVFREZFIiBzdHJva2U9IiNBRkE5RUMiIHN0cm9rZS13aWR0aD0iMSIvPgo8dGV4dCB4PSI0ODUiIHk9IjI3MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjYwMCIgZmlsbD0iIzI2MjE1QyI+QWdlbnQgb3JjaGVzdHJhdGlvbjwvdGV4dD4KPHRleHQgeD0iNDg1IiB5PSIyOTAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1MzRBQjciPkluY2x1ZGVzIGd1YXJkcmFpbCBjaGVja3BvaW50PC90ZXh0PgoKPHJlY3QgeD0iMTEwIiB5PSIzMzAiIHdpZHRoPSIyMzAiIGhlaWdodD0iNjAiIHJ4PSI4IiBmaWxsPSIjRjFFRkU4IiBzdHJva2U9IiM4ODg3ODAiIHN0cm9rZS13aWR0aD0iMSIvPgo8dGV4dCB4PSIyMjUiIHk9IjM1MiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9IjYwMCIgZmlsbD0iIzJDMkMyQSI+RGF0YSBsYXllcjwvdGV4dD4KPHRleHQgeD0iMjI1IiB5PSIzNzIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPlBvc3RncmVzICsgUmVkaXM8L3RleHQ+Cgo8cmVjdCB4PSIzNzAiIHk9IjMzMCIgd2lkdGg9IjIzMCIgaGVpZ2h0PSI2MCIgcng9IjgiIGZpbGw9IiNGMUVGRTgiIHN0cm9rZT0iIzg4ODc4MCIgc3Ryb2tlLXdpZHRoPSIxIi8+Cjx0ZXh0IHg9IjQ4NSIgeT0iMzUyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iNjAwIiBmaWxsPSIjMkMyQzJBIj5EYXRhIGluZ2VzdGlvbjwvdGV4dD4KPHRleHQgeD0iNDg1IiB5PSIzNzIiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPlNjaGVkdWxlZCwgbm8gaW5ib3VuZCB0cmFmZmljPC90ZXh0PgoKPHRleHQgeD0iMzUwIiB5PSI0NTUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZvbnQtc2l6ZT0iMTIiIGZpbGw9IiM1RjVFNUEiPkFsbCBzZWNyZXRzIChEQiBwYXNzd29yZCwgTExNIEFQSSBrZXlzKSBhcmUgaW5qZWN0ZWQgYXMgZW52aXJvbm1lbnQ8L3RleHQ+Cjx0ZXh0IHg9IjM1MCIgeT0iNDczIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmb250LXNpemU9IjEyIiBmaWxsPSIjNUY1RTVBIj52YXJpYWJsZXMgYXQgZGVwbG95IHRpbWUgYW5kIGFyZSBuZXZlciBjb21taXR0ZWQgdG8gdGhlIHJlcG9zaXRvcnkuPC90ZXh0Pgo8L3N2Zz4K)

### 12.1 Principles

- The API gateway is the only container with an open inbound port. Every other service is unreachable from outside the private network by design, not just by convention.
- Secrets (database password, LLM provider API keys) are never committed to the repository. They are injected as environment variables at deploy time, and a `.env.example` file with placeholder names is committed instead of a real `.env`.
- The guardrail agent is treated as a compliance control, not a nice-to-have feature — its test coverage is held to the same standard as the simulation math.

### 12.2 Security controls and when they are introduced

| Control | Why it matters | Introduced at |
|---|---|---|
| `.gitignore` for `.env`, `__pycache__`, `node_modules` | Prevents secrets and noise from ever entering git history | Phase 0, before the first commit |
| `.env.example` with placeholder keys | Documents required config without exposing real values | Phase 0 |
| Pre-commit secret scanning (e.g. `gitleaks`) | Catches an accidentally pasted API key before it's committed | Phase 3, the first time real LLM API keys enter the codebase |
| Input validation on all gateway endpoints | Prevents malformed or oversized requests reaching internal services | Phase 4, before any endpoint is internet-facing |
| Authentication (API key or JWT per session) | Prevents unauthenticated use of paid LLM calls | Phase 4, before deployment |
| Rate limiting | Prevents a runaway loop or abuse from blowing through the LLM budget | Phase 4, before deployment |
| HTTPS / TLS termination | Encrypts traffic to the only public-facing service | Phase 7, at first deployment |
| Dependency vulnerability scan (`pip-audit`, `npm audit`) | Catches known CVEs in third-party packages | Phase 6, and on every CI run thereafter |
| Full git history secret scan | Confirms nothing slipped through before going further | Phase 6, before deployment |
| Guardrail adversarial test suite | Confirms the compliance boundary holds under deliberate attempts to break it | Phase 6 |

The general rule used throughout: nothing is exposed to the internet until authentication, rate limiting, and input validation are in place for it — but basic hygiene (gitignore, environment variables, no hardcoded secrets) starts on day zero, before a single line of feature code is written.

## 13. Evals and QA plan

- **Calibration backtests**: run on a schedule, comparing stated probabilities against real historical cohort outcomes.
- **LLM-judge faithfulness check**: a separate model call verifies the narrator agent's explanation is consistent with the underlying simulation numbers, catching hallucinated causal stories.
- **Guardrail adversarial suite**: a fixed set of prompts deliberately trying to extract advice-framed language ("just tell me what to do," "should I buy index funds"), run on every CI pipeline.
- **Regression suite**: simulation outputs for a fixed set of test profiles are checked against known-good baselines so a refactor can't silently change the statistics.

## 14. Non-functional requirements

| Category | Requirement |
|---|---|
| Performance | What-if response under 6s on cache hit, under 20s on a full simulation re-run |
| Cost | Under £10/month, tracked via the LLM gateway's per-call cost logging |
| Availability | Best-effort; no formal SLA, acceptable downtime during redeploys |
| Browser support | Latest two versions of Chrome, Firefox, Safari |

## 15. Implementation roadmap

This is the step-by-step build order. Each phase ends with a concrete commit-and-push checkpoint, not just a vague "finish the feature" milestone.

### Phase 0 — Setup (before any feature code)

1. `git init`, create `.gitignore` (Python, Node, `.env`, `__pycache__`, `node_modules`, `*.db`).
2. Create the monorepo folder structure (see section 16).
3. Create `.env.example` with placeholder variable names only.
4. Write a one-paragraph README stub.
5. **Commit**: "Initial commit: project scaffold, gitignore, env template."
6. Create the remote repository and push immediately. Do not wait until something "works" — the habit of pushing early is part of what you're demonstrating.
7. Add an empty GitHub Actions workflow file that just runs `echo "ci placeholder"` — this gets CI wired up before there's anything meaningful to test, which is intentional.

### Phase 1 — Data ingestion service (week 1)

1. Build the ONS unemployment ingestion script; validate the output against a known published figure as a sanity check.
2. Build the Bank of England interest rate ingestion script.
3. Build the historical market return ingestion script.
4. Stand up Postgres locally via Docker for development.
5. **Commit and push after each working data source individually** — three or four small commits, not one large one. Example messages: "Add ONS unemployment ingestion," "Add BoE rate history ingestion."

### Phase 2 — Simulation engine (week 2)

1. Implement the regime-switching HMM.
2. Implement block-bootstrapped return sampling.
3. Implement the Monte Carlo path generator and percentile aggregation.
4. Write unit tests for the simulation math as you go, not after — these are pure functions and are the easiest part of the whole system to test, so there's no excuse to defer it.
5. Work in a feature branch (`feature/simulation-engine`), open a pull request into `main` even though you are the only reviewer — this builds the habit and gives you a clean diff to reference later.
6. **Push** at the end of each working sub-feature (HMM, then bootstrapping, then aggregation), merge the PR once the test suite passes.

### Phase 3 — Agent orchestration and RAG (week 3)

1. Stand up the self-hosted LiteLLM gateway first, before writing any agent code — this is the point real external API keys (LLM provider keys) enter the project for the first time.
2. **Add pre-commit secret scanning now** (`gitleaks` or `detect-secrets`), before adding the keys to your local `.env`. This is the single most important "when" in the whole roadmap: security tooling goes in immediately before, not after, secrets exist in the working directory.
3. Build the RAG ingestion pipeline over ONS/FCA source documents.
4. Build the profile-builder, parameter-translator, and narrator agents in LangGraph.
5. Build the guardrail agent and its disallowed-phrase test set.
6. **Commit and push per agent**, each with its own small test.

### Phase 4 — API gateway and security hardening (week 4)

1. Build the FastAPI gateway with the endpoints from section 8.2.
2. Add authentication (a simple API key or JWT scheme is sufficient at this scale).
3. Add rate limiting per user/key.
4. Add input validation on every endpoint.
5. This is the phase where the system first becomes a candidate for internet exposure — none of the previous phases needed this, because nothing was reachable from outside yet.
6. **Commit and push**, then write integration tests that exercise the gateway end-to-end against the other services running locally via Docker Compose.

### Phase 5 — Frontend (week 5)

1. Build the profile setup screen, the fan chart, and the what-if chat panel.
2. The frontend talks only to the API gateway, never to any internal service directly — enforce this in code review (of yourself), not just in the architecture diagram.
3. **Commit and push** incrementally per screen.

### Phase 6 — Evals, guardrail hardening, and pre-deployment security review (week 6)

1. Build the calibration backtest harness.
2. Build the LLM-judge faithfulness check.
3. Run a dependency vulnerability scan (`pip-audit`, `npm audit`) and fix anything flagged.
4. Run a full-history secret scan (`gitleaks detect --source .`) to confirm nothing was ever committed, even in an old commit that was later "fixed."
5. Review logs across all services to confirm no profile data or full prompts are logged in plaintext.
6. **This is the security gate** — do not proceed to deployment until this phase's checklist is clean.

### Phase 7 — Containerization and deployment (week 7)

1. Write a Dockerfile per service.
2. Write `docker-compose.yml` tying them together with the internal network from the security diagram.
3. Provision the free-tier VM, configure HTTPS via a reverse proxy (Caddy handles automatic TLS with minimal config).
4. Wire the GitHub Actions workflow to build and test on every push, and deploy on merge to `main`.
5. **Tag a release** (`v0.1.0`) once the deployed version is live and reachable.

### Phase 8 — Polish and framing (week 8)

1. Write the full README: architecture diagram, setup instructions, a short demo clip.
2. Write the resume bullet and project description, leading with the system property (calibration, multi-agent orchestration, microservices) rather than the domain.
3. **Tag `v1.0.0`.**

## 16. Repository structure

```
scenariotwin/
├── .github/workflows/ci.yml
├── .gitignore
├── .env.example
├── README.md
├── docker-compose.yml
├── services/
│   ├── api-gateway/
│   ├── simulation-engine/
│   ├── agent-orchestration/
│   ├── data-ingestion/
│   └── llm-gateway/
├── frontend/
├── infra/
│   └── caddy/
└── docs/
    └── PRD.md
```

## 17. Testing strategy

| Layer | Tool | What it covers |
|---|---|---|
| Unit | pytest | Simulation math, agent parameter parsing, guardrail phrase matching |
| Integration | pytest + Docker Compose | Gateway-to-service calls, cache hit/miss behavior |
| Eval | custom harness | Calibration accuracy, narrator faithfulness, guardrail adversarial suite |
| CI | GitHub Actions | Runs all of the above on every push; blocks merge on failure |

## 18. Deployment and infrastructure plan

| Component | Choice | Monthly cost |
|---|---|---|
| Compute | Oracle Cloud free-tier ARM VM | £0 |
| Reverse proxy / TLS | Caddy | £0 |
| LLM calls | Groq / Gemini Flash free tiers for routine tasks; a paid model only for narrator/guardrail steps | Under £5 |
| Database | Self-hosted Postgres + Redis on the same VM | £0 |
| CI/CD | GitHub Actions free tier | £0 |
| Scheduled jobs | GitHub Actions free minutes | £0 |

## 19. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Free-tier LLM rate limits throttle the demo during a live interview walkthrough | Cache aggressively; have a recorded demo as backup |
| Regime-switching model overfits to a specific historical period | Validate across multiple distinct historical crisis periods (2008, 2020) |
| Guardrail agent fails on a novel phrasing not in the test set | Treat the adversarial test set as a living document, add new cases as found |
| Free-tier VM is reclaimed or rate-limited | Keep infrastructure-as-code (docker-compose + setup script) so redeployment elsewhere is fast |

## 20. Appendix

### 20.1 Glossary

- **Sequence-of-returns risk**: the risk that a market downturn occurring early in retirement (or coinciding with job loss) is far more damaging than the same downturn occurring at another time, because withdrawals lock in losses.
- **Regime-switching model**: a model where the system can be in one of several hidden states (e.g. normal, recession, crisis), each with different statistical behavior.
- **Guidance vs advice**: under UK financial regulation, "guidance" provides information to help someone make their own decision; "advice" recommends a specific course of action and is a regulated activity requiring authorisation.

### 20.2 Key reference data sources

- ONS Labour Force Survey: ons.gov.uk
- Bank of England database: bankofengland.co.uk/boeapps/database
- FCA Handbook (PERG): handbook.fca.org.uk
