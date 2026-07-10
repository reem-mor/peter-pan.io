# AGENTS.md — PETER PAN

Agentic **incident-response platform**: n8n orchestration (Layer 2) over six FastAPI
microservices (Layer 3), task-routed models behind one `LLMClient` seam (Layer 4), Streamlit
WebUI (Layer 1). **Not** the legacy PITER AiOps project — see
[ADR 0001](docs/adr/0001-piter-carryover.md) for the split.

## Conventions

- Python **3.12** · repo venv `.venv/` · `pip install -r requirements-dev.txt`
- **Diagrams are source of truth** (`docs/*.mmd` + `docs/BUILD_PLAN.md`); out-of-diagram
  work is out of scope, one stage per approval
- **Contracts are frozen** (`docs/contracts/`) — changing one requires an ADR; each service
  vendors an identical copy checked by a contract test
- `services/<name>/` is a self-contained deployment unit and import root — **no `services.*`
  cross-imports**, services talk HTTP only
- n8n: re-export the flow to `n8n/peter-flow.json` **on every change**; credentials by name
  only, URLs from env vars — the export must carry no secrets
- **Never commit** `.env`, SPA bundles, or live AWS/n8n resource IDs
- `ruff check .` must pass before PRs. Migrated pytest suites are **expected RED** until
  Stage A re-packaging (ADR 0001 limitation 1); CI is lint-only until then

## Scope

Production-minded ops code — observability, grounded/cited RAG, deterministic guardrail
floors, preview-first escalation. Models propose; unit-tested code and schemas decide.
Model/memory/storage choices: [ADR 0002](docs/adr/0002-model-memory-db.md).
