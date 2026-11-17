> **Historical implementation - superseded by [PETER PAN](https://github.com/reem-mor/peter-pan).** This repository documents an earlier architecture and learning iteration. The maintained flagship and recruiter-facing technical evidence are in `reem-mor/peter-pan`. This repository is retained for engineering history and is not the recommended starting point for new contributions.

---

# PETER PAN — Agentic incident-response platform

Predictive, guarded, agentic incident response — n8n-orchestrated microservices with
deterministic safety floors over LLM judgement.

[![CI](https://github.com/reem-mor/peter-pan.io/actions/workflows/ci.yml/badge.svg)](https://github.com/reem-mor/peter-pan.io/actions/workflows/ci.yml)

## Architecture

Source of truth: [system diagram](docs/peter-pan-system.mmd) · [n8n flow](docs/peter-pan-n8n-flow.mmd) · [build plan](docs/BUILD_PLAN.md)

Architecture reference (runtime flow, service status, health commands): **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**

| Layer | Component | Status |
|---|---|---|
| 1 UI | Streamlit WebUI (`ui/`) | Stage B skeleton |
| 2 Orchestration | n8n PETER flow (`n8n/peter-flow.json`) | Full local golden-set E2E verified |
| 3 Core | Six core FastAPI services + three supporting seams | Stage A fixture-backed implementation |
| 4 Models | Task-routed `LLMClient` (`docs/llm_client/`) | Fixture adapters + Stage C stubs |

**Graded four primary services:** RAG, Predictor, Guardrails, LangGraph agent. Ingestion and Tools API are supporting infrastructure ([ADR 0003](docs/adr/0003-system-boundaries.md)).

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
# Set the required empty secret values in .env; never commit that file.
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe scripts/run_all_tests.py
docker compose config --quiet        # syntax check only
.\.venv\Scripts\python.exe evaluation/run_e2e.py --dry-run
docker compose --profile bootstrap up --build -d
# Full compose-backed E2E:
.\.venv\Scripts\python.exe evaluation/run_e2e.py --entrypoint n8n --base-url http://localhost --token $env:PETER_SERVICES_TOKEN
```

The `bootstrap` profile keeps the one-shot authenticated workflow import explicit.
Stage A attempts the structured LLM writer first and uses a tested deterministic,
contract-valid fixture fallback when the local OpenAI-compatible parser path fails.

## Layout

| Path | Purpose |
|---|---|
| `services/` | 9 self-contained deployment units (6 core + image-analyzer + fixture-llm + integration-stubs) |
| `ui/` | Streamlit WebUI (Stage B) |
| `n8n/` | Versioned workflow export |
| `evaluation/` | Golden sets + E2E harness |
| `infra/aws/` | CloudFormation demo stack |
| `docs/` | Contracts, ADRs, audits, architecture reference |

## Documentation

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Runtime flow, service status, health commands |
| [setup.md](docs/setup.md) | Prerequisites and `.env` configuration |
| [local-development.md](docs/local-development.md) | Docker Compose startup workflow |
| [aws-deployment.md](docs/aws-deployment.md) | EC2 demo deployment |
| [n8n-workflow.md](docs/n8n-workflow.md) | 8-node orchestration spine |
| [api.md](docs/api.md) | Endpoint reference |
| [testing.md](docs/testing.md) | Test commands and rubric metrics |
| [security.md](docs/security.md) | Secrets, network, container policy |
| [demo-guide.md](docs/demo-guide.md) | 5–8 minute demonstration script |
| [IMPLEMENTATION-CHECKLIST.md](docs/IMPLEMENTATION-CHECKLIST.md) | Course spec audit status |

Postman: [postman/peter-pan-core-apis.postman_collection.json](postman/peter-pan-core-apis.postman_collection.json)

## Development tooling

MCP servers, CI commands, and available skills: [docs/AGENT-TOOLING.md](docs/AGENT-TOOLING.md)

## License

MIT
