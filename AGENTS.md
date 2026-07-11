# AGENTS.md — PETER PAN

Agentic **incident-response platform**: n8n orchestration (Layer 2) over six FastAPI
microservices (Layer 3), task-routed models behind one `LLMClient` seam (Layer 4), Streamlit
WebUI (Layer 1).

## Conventions

- Python **3.12** · repo venv `.venv/` · `pip install -r requirements-dev.txt`
- **Diagrams are source of truth** (`docs/*.mmd` + `docs/BUILD_PLAN.md`); out-of-diagram work is out of scope
- **Contracts are frozen** (`docs/contracts/`) — changing one requires an ADR
- `services/<name>/` is a self-contained deployment unit — **no `services.*` cross-imports**
- n8n: re-export the flow to `n8n/peter-flow.json` **on every change**
- **Never commit** `.env`, `.cursor/mcp.json`, SPA bundles, or live AWS/n8n resource IDs
- `ruff check .` must pass; tests run per service via `python scripts/run_all_tests.py`

## Scope

Production-minded ops code — observability, grounded/cited RAG, deterministic guardrail
floors, preview-first escalation. Models propose; unit-tested code and schemas decide.

Model/memory/storage: [ADR 0002](docs/adr/0002-model-memory-db.md). Service boundaries: [ADR 0003](docs/adr/0003-system-boundaries.md). MCP tools and CI commands: [docs/AGENT-TOOLING.md](docs/AGENT-TOOLING.md).
