# Layer 3 — Platform services

Each subdirectory is a **self-contained FastAPI deployment unit**
(own package, Dockerfile, tests, requirements). **No** `from services.*` imports.

Contracts are vendored from [`docs/contracts/contracts.py`](../docs/contracts/contracts.py)
and kept byte-identical via `tests/test_contracts_identity.py` where applicable.

## Graded core (course-mapped)

| Directory | Port (compose) | Role |
|:---|:---|:---|
| `rag/` | 8003 | Cited retrieval + insight; Chroma / TF-IDF; optional Llama.cpp |
| `predictor/` | 8002 | PyTorch + EWMA floor → 6 `incident_class` |
| `guardrails/` | 8004 | Input/output rails → `{passed, flags, reason}` |
| `langgraph-agent/` | 8005 | Planner → RAG/Tools specialists → synthesis |

## Supporting seams (ADR 0003)

| Directory | Role |
|:---|:---|
| `ingestion/` | Accept/normalize `Signal`, forward to n8n |
| `tools-api/` | Owners, deploys, enrichment, escalation preview, audit |
| `dashboard-generator/` | Fixture-first Grafana dashboard POST |
| `image-analyzer/` | Vision fallback (ResNet) — not on golden path |
| `fixture-llm/` | OpenAI-compatible mock for Stage A LM nodes |
| `integration-stubs/` | Downstream route stubs for E2E |

## Rules

- Typed Pydantic request/response; structured errors; `/healthz` on every unit.
- Fixture-first tests; register suites in `scripts/run_all_tests.py`.
- Performance budget: demo endpoints under ~2s on t3.large with fixtures.
- FastAPI conventions: [`docs/AGENT-TOOLING.md`](../docs/AGENT-TOOLING.md).

Architecture: [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §5 · API: [`docs/api.md`](../docs/api.md).
