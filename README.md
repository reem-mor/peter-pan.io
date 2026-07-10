<div align="center">

# PETER PAN

### Predictive, guarded, agentic incident response — n8n-orchestrated microservices

[![CI](https://github.com/reem-mor/peter-pan.io/actions/workflows/ci.yml/badge.svg)](https://github.com/reem-mor/peter-pan.io/actions/workflows/ci.yml)

</div>

PETER PAN ingests production signals (Grafana alerts, manual reports, deploy events, user
complaints), enriches and de-noises them deterministically, extracts a structured incident,
lets an **incident-commander agent** investigate through governed tools (anomaly predictor,
citation-only RAG, LangGraph deep-reasoning specialists), and emits a **schema-enforced,
citation-backed TriageReport** that passes output guardrails before anyone gets paged.
Design rule throughout: **deterministic safety floors over LLM judgement** — models propose,
unit-tested code and schemas decide.

> **Not PITER.** This repo evolved from the legacy
> [PITER AiOps](https://github.com/reem-mor/piter-aiops) project (Flask + Bedrock Agent +
> React) but is a **different system with its own architecture**. What was kept, migrated,
> and deleted is recorded in [ADR 0001](docs/adr/0001-piter-carryover.md).

## Architecture — four layers

The two Mermaid diagrams are the **source of truth**; anything not in them is out of scope:
[system architecture](docs/peter-pan-system.mmd) · [n8n flow](docs/peter-pan-n8n-flow.mmd).

| layer | what | status |
|---|---|---|
| **1 · Humans** | Streamlit WebUI (incident form, TriageReport viewer, local assistant) | Stage B |
| **2 · Orchestration** | the n8n **PETER flow** — webhook → guardrails → enrichment → noise gate → extractor → commander agent → TriageReport → guardrails → router/escalation | **built** → [`n8n/peter-flow.json`](n8n/peter-flow.json) · [docs](n8n/README.md) |
| **3 · Core services** | six FastAPI microservices: Ingestion, Predictive Engine (EWMA floor + classifier), RAG (cited answers only), Guardrails (regex floor + NeMo seam), Tools API + approval gate, LangGraph agent | **packaged, suites green** — fixture LLM + E2E harness pending |
| **4 · AI models** | task-routed ([why](docs/model-memory-db-rationale.md) · [ADR 0002](docs/adr/0002-model-memory-db.md)): Gemini 2.5 Flash (extraction), Bedrock Claude Sonnet (agent/synthesis), llama.cpp Mistral 7B (RAG generation), Ollama Llama 3 (assistant) — all behind one `LLMClient` seam | Stage C; Stage A runs deterministic fixtures |

## Contracts first

[`docs/contracts/contracts.py`](docs/contracts/contracts.py) defines the only models the
layers exchange — `Signal`, `Incident` (+ `IncidentContext`, `DeployRef`), `Citation`,
`TriageReport` — **frozen at Stage A start**; changing one requires an ADR. JSON Schemas are
exported for n8n's Structured Output Parser. Floors baked into the contracts: citations are
schema-required (uncited answers fail), `owner_team`/`escalation_path` may only be copied
from Tools API responses, P-level mapping is deterministic code, escalation is preview-first.

## Repo layout

| path | contents |
|---|---|
| `services/` | one self-contained dir per microservice (tools-api, guardrails, rag carry migrated code; ingestion, predictor, langgraph-agent scaffolded) |
| `n8n/` | versioned PETER-flow export + setup docs (re-exported on every flow change) |
| `docs/` | diagrams (source of truth), [BUILD_PLAN.md](docs/BUILD_PLAN.md), ADRs, frozen contracts |
| `predictive/` | demo/training data generators (`datagen/`) |
| `evaluation/` | golden-set seeds; Stage A adds the E2E eval harness |

## Build stages

Full plan with exit gates: [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md).

- **Stage A — Layers 2+3, mock-first** *(in progress)*: contracts frozen ✅ · PETER flow
  built + exported ✅ · six services packaged with green suites ✅ · coherent PITER-free
  dataset/corpus universe + reconciled eval golden set ✅ · FixtureLLM mock, real LangGraph
  graph and the `run_e2e` harness ⏳. Exit gate: `docker compose up` + one command posts
  golden `Signal` fixtures and receives valid `TriageReport`s **with zero external API calls**.
- **Stage B — Streamlit UI** against the mock-backed stack.
- **Stage C — real providers last**: swap the fixture client for Bedrock/llama.cpp/Ollama by
  config; same E2E suite must stay green; eval scores recorded in `evaluation/results/`.

## Development

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements-dev.txt   # Windows paths
ruff check .                        # must pass
python scripts/run_all_tests.py     # per-service pytest suites (each service is its own rootdir)
docker compose build                # six self-contained service images
```

Secrets live in `.env` (gitignored, never committed); n8n credentials are referenced by
name only — the flow export carries none. Service URLs and webhook targets are documented
in [`n8n/README.md`](n8n/README.md).

## License

[MIT](LICENSE)
