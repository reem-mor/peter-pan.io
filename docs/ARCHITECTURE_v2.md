# PETER PAN — Architecture Reference

Human entry point for the repo. Diagrams are the source of truth; this document
orients you to what exists today and links you to the detail.

---

## System diagrams

| Diagram | What it shows |
|---|---|
| [`docs/peter-pan-system.mmd`](peter-pan-system.mmd) | Four-layer topology, service nodes, data flows |
| [`docs/peter-pan-n8n-flow.mmd`](peter-pan-n8n-flow.mmd) | 8-node n8n spine, CTX branches, guardrail gates |

Architecture decisions: [ADR 0002 — model/memory/storage](adr/0002-model-memory-db.md) ·
[ADR 0003 — service boundaries](adr/0003-system-boundaries.md).

Frozen contracts: [`docs/contracts/contracts.py`](contracts/contracts.py) (pydantic v2,
`extra="forbid"`; JSON Schema exported to [`docs/contracts/export_json_schema.py`](contracts/export_json_schema.py)).

---

## Runtime flow

```
Inbound signal (Grafana alert / WebUI form / deploy event)
    │
    ▼
[Ingestion API]  POST /signals → validates Signal, forwards to n8n webhook
    │
    ▼
[n8n — node 1]  Webhook /webhook/peter-signal
    │
[n8n — node 2]  HTTP → Guardrails POST /check/input
[n8n — node 3]  IF guardrail fails → reject (logged)
    │
    ├─ [CTX branch] maintenance-window stub / GitHub deploys / Slack complaints → IncidentContext
    │
[n8n — node 4]  LM node (Stage A: FixtureLLM) → extract Incident fields
[n8n — node 5]  AI Agent (Stage A: FixtureLLM) → tool calls:
    │               ├─ Predictor  POST /analyse
    │               ├─ RAG        POST /query
    │               └─ LangGraph  POST /agent/run
[n8n — node 6]  LLM Chain → TriageReport (Structured Output Parser, frozen schema)
[n8n — node 7]  HTTP → Guardrails POST /check/output; fail → review queue
[n8n — node 8]  Router: category → infra/database/application team webhook + P1 escalation
    │
    ▼
TriageReport (returned to caller / rendered in UI)
```

---

## Folder ownership

| Path | Owner | Notes |
|---|---|---|
| `services/` | Layer 3 — nine self-contained FastAPI units | No cross-imports; HTTP-only comms |
| `ui/` | Layer 1 — Streamlit WebUI | Stage B |
| `n8n/` | Layer 2 — n8n flow export | Re-export on every flow change |
| `docs/contracts/` | Shared contracts | Frozen; ADR required to change |
| `evaluation/` | Eval harness + frozen golden sets | Never mutate test sets mid-run |
| `infra/aws/` | CloudFormation demo stack | Stage C / deployment |
| `docs/` | Diagrams, ADRs, audits, plans | This file is the entry point |
| `scripts/` | Bootstrap and utility scripts | `run_all_tests.py`, `bootstrap_n8n_local.py` |
| `predictive/` | Predictor datagen + training | Stage C |
| `packages/` | Shared observability helpers | `peter_observability` |

---

## Service deployment units

| Service dir | Package | Primary endpoint | Status |
|---|---|---|---|
| `services/ingestion/` | `ingestion_service` | `POST /signals` | Implemented |
| `services/predictor/` | `predictor_service` | `POST /analyse` | EWMA floor implemented; PyTorch classifier **stubbed** |
| `services/rag/` | `rag_service` | `POST /query` | TF-IDF retrieval implemented; llama.cpp generation **stubbed** |
| `services/guardrails/` | `guardrails_service` | `POST /check/input`, `POST /check/output` | Regex floor implemented; NeMo **stubbed** |
| `services/image-analyzer/` | `image_analyzer_service` | `POST /analyze` | Stage A supporting seam — ResNet scaffold; not invoked by the current n8n flow |
| `services/tools-api/` | `tools_api` | `POST /escalations`, `GET /audit`, tool routes | Implemented (preview-first, SQLite audit) |
| `services/langgraph-agent/` | `langgraph_agent` | `POST /agent/run` | Deterministic graph topology implemented; no provider call in Stage A |
| `services/fixture-llm/` | `fixture_llm` | OpenAI-compatible `/v1/chat/completions` | Stage A seam — deterministic canned responses |
| `services/integration-stubs/` | `integration_stubs` | Team webhooks, review-queue receiver | Stage A seam — stub endpoints |

All nine service units expose `GET /healthz`.

---

## Canonical contracts (never break silently)

| Contract model | Used by | Enforced by |
|---|---|---|
| `Signal` | Ingestion → n8n webhook | pydantic schema + contract copy-identity test |
| `Incident` | n8n node 4 output → agent input | Structured Output Parser JSON Schema |
| `IncidentContext` | CTX branch merge output | pydantic |
| `TriageReport` | n8n node 6 → guardrail output check | pydantic + output guardrail owner-verification |

Changing any contract requires an ADR. Copies live in `<service>/<pkg>/contracts.py`;
a contract-identity test asserts all copies match `docs/contracts/contracts.py`.

---

## Evaluation ownership

| Asset | Purpose | Mutability |
|---|---|---|
| `evaluation/golden_signals.json` | E2E input fixtures | Frozen |
| `evaluation/tool_evaluation_cases.json` | LangGraph tool benchmark (10 queries) | Frozen mid-run |
| `evaluation/results/` | Generated evidence | `e2e_latest.json` is replaced per run; preserve tagged/final evidence separately |
| `evaluation/run_e2e.py` | Stage A exit-gate harness | Extend only; `--dry-run` loads fixtures without HTTP |

---

## Health checks

```powershell
# Syntax check compose
docker compose config --quiet

# Run all service test suites
python scripts/run_all_tests.py

# Dry-run E2E (no HTTP, no n8n required)
python evaluation/run_e2e.py --dry-run

# Lint
ruff check .
```

The compose-backed full E2E (fixtures → Ingestion → n8n → TriageReport) was verified
against seven scenarios on 2026-07-11: application, database, infra/LangGraph,
rejection, suppression, review queue, and P1 preview escalation. The stack and explicit
n8n bootstrap profile must be running first.

---

## Implemented · Stubbed · Planned

| Capability | State |
|---|---|
| Signal validation + normalisation (Ingestion) | **Implemented** |
| Regex/rule guardrail floor | **Implemented** |
| EWMA/z-score anomaly floor (Predictor) | **Implemented** |
| LangGraph graph topology + parallel RAG/Tools specialists | **Implemented** |
| Tools API (owners, deploys, similar incidents, escalation preview, audit log) | **Implemented** |
| n8n 8-node spine + CTX branches | **Implemented** |
| FixtureLLM seam (OpenAI-compatible, deterministic) | **Implemented** |
| Structured writer parser failure path | **Implemented** — tool-grounded, contract-valid Stage A fallback |
| Integration stubs (team webhooks, review queue) | **Implemented** |
| TF-IDF retrieval in RAG | **Implemented** |
| Contract-identity test | **Implemented** |
| PyTorch classifier (1D-CNN/GRU dual head) | **Stubbed** — fixed-weight fixture; training is Stage C |
| NeMo Guardrails layer | **Stubbed** — regex floor is the active rail |
| llama.cpp GGUF generation in RAG | **Stubbed** — FixtureLLM is the active seam |
| Streamlit WebUI (`ui/`) | **Implemented skeleton** (Stage B wiring pending) |
| ≥55-doc corpus + `scripts/seed_kb.py` | **Planned** follow-on rubric work |
| Prompt Engineering Log (5 surfaces × 5 iterations) | **Planned** (Stage A → C) |
| Real LLM providers (Gemini, Bedrock, Ollama) | **Optional/planned** (Stage C; not required for Layers 2–3) |
| pgvector / Supabase ingestion | **Planned** (Stage C) |
| AWS EC2 deployment | **Implemented (demo)** — `scripts/provision_ec2.sh` · `scripts/deploy_ec2.sh` · `docker-compose.ec2.yml`; dev-IP-only SG, instance-generated secrets; full n8n-path E2E passed 7/7 on EC2 2026-07-11 |
| PyTorch training + dataset (≥200 samples) | **Planned** (Stage C stretch) |
