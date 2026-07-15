---
name: fastapi-service-conventions
description: Use when creating or modifying any FastAPI microservice (RAG, Predictor, Guardrails, LangGraph, Ingestion, Dashboard Generator) — structure, contracts, tests, Docker, performance.
---

# FastAPI Service Conventions

New services must be indistinguishable in shape from existing ones. Before
writing a new service, `ls` an existing one and mirror its layout exactly.

## Layout (mirror the existing services — verify against repo before assuming)
```
services/<name>/
  app/main.py          # FastAPI app, routes only — no business logic in routes
  app/logic.py         # the actual work
  app/models.py        # imports shared models from contracts.py, service-locals here
  tests/test_<name>.py # pytest, runs in scripts/run_all_tests.py
  Dockerfile
  requirements.txt     # pinned versions, minimal deps
```

## Contracts
- Shared request/response models live in `contracts.py` (repo root), Pydantic
  with `extra="forbid"`. A service NEVER declares its own copy of a shared
  model — import it.
- Every endpoint returns a typed response model. No bare dicts.
- Errors: structured `{error: str, detail: str}` with correct HTTP codes.
  No stack traces in responses.

## Tests
- Every endpoint: happy path + one malformed-input case + one contract-shape
  assertion (response validates against the Pydantic model).
- Tests must pass on Python 3.12 (the CI target). Fixture-based — no network,
  no live LLM calls in tests.
- New service = registered in `scripts/run_all_tests.py` in the same commit.

## Docker
- Base: `python:3.12-slim`. One process per container. Port from env.
- Added to `docker-compose.yml` in the same commit as the service.
- `docker compose config --quiet` must stay silent after any compose change.

## Performance & optimization (demo-scale rules — do NOT over-engineer)
- Target: any endpoint responds < 2s on t3.large with fixtures. That's the
  whole performance budget. No caching layers, no connection pools tuning,
  no async gymnastics unless a measured number says otherwise.
- Heavy objects (models, datasource uid, ChromaDB client) load ONCE at
  startup (lifespan handler), never per-request.
- If something is slow: measure first (`time.perf_counter` around the block,
  log it), fix the measured thing, stop. Karpathy rule: no speculative
  optimization — 100 lines that are fast enough beat 1000 clever ones.
