# PETER PAN — Session A Layer 3 Audit (2026-07-13)

Read-only audit of every `services/*` deployment unit against
[docs/ARCHITECTURE.md](../ARCHITECTURE.md), taken before any Session A change.
Baseline: `python scripts/run_all_tests.py` exit 0 (all suites green) on the
repo venv (Python 3.14.5; CI target remains 3.12).

## Service inventory

| Service | Endpoints | Contract | Tests | Fixture / real |
|---|---|---|---|---|
| `services/ingestion/` | `POST /signals`, `GET /healthz`, `GET /readyz` | `Signal` (vendored, identity-tested) | 3 files (~11 tests): schema accept/reject, n8n forward (mocked), auth, golden signal | **Real** validation + normalisation + forward; graceful degradation when webhook missing |
| `services/predictor/` | `POST /analyse`, `GET /healthz` | `incident_class` Literal of 6 classes; `AnalyseResponse` local model | 6 files (~26 tests): six-class, EWMA bands, unknown-class fallback, severity conflict, NaN/Inf, auth | EWMA/z-score floor **real**; classifier **fixed-weight stub** — no `train.py`, no `predictor.pth`, no `metrics.json` |
| `services/rag/` | `POST /query`, `GET /healthz` | `Citation` (vendored); `QueryResponse` with `refused: bool` | 8 files (~31 tests): retrieval, grounding, refusal, `MIN_SCORE`, corpus structure | TF-IDF retrieval **real** (in-memory, 28-file static corpus); no vector store, no populate script, llama.cpp generation **absent** |
| `services/guardrails/` | `POST /check/input`, `POST /check/output`, `GET /healthz` | `GuardrailResult` `{passed, flags, reason}` exact, `extra="forbid"` | 11 files (~52 tests): accept/reject tables, floor, owner verification (mocked), auth | Regex floor **real**; policy engine **Noop stub** (NeMo seam). No explicit floor-overrides-engine test; no FP-rate test on golden valid alerts |
| `services/tools-api/` | 4 tool routes, `POST /escalations`, `GET /teams`, `GET /audit`, `GET /healthz` | `TriageReport` input for escalations (vendored) | 16 files (~96 tests) | **Real** (CSV/JSON fixture data, SQLite audit, preview-first; live dispatch off) |
| `services/langgraph-agent/` | `POST /agent/run`, `GET /healthz` | Output validates as `TriageReport` | 2 files (~16 tests): graph paths, P1/P3, contract | Graph topology **real** (HTTP to RAG/Tools); no provider LLM call (Stage A by design) |
| `services/image-analyzer/` | `POST /analyze`, `GET /healthz` | Local `AnalyzeImageResponse` | 1 file (2 tests) | **Mock fixture** (deterministic from image dims); not invoked by n8n flow — matches ARCHITECTURE status |
| `services/fixture-llm/` | `POST /v1/chat/completions`, `/v1/responses`, `GET /healthz`, `/readyz` | OpenAI-compatible envelope | 1 file (18 tests) | **Deterministic fixture seam** by design |
| `services/integration-stubs/` | team webhooks, `/review-queue`, `/deliveries`, `GET /healthz` | n/a (stub envelope) | 1 file (8 tests) | **Stub by design** |

## Gaps vs Session A targets

| Target | Current state |
|---|---|
| Guardrails: floor-overrides-LLM test; FP <5% on golden valid alerts | Missing both tests; schema + floor already correct |
| Predictor: seeded `train.py` → `predictor.pth` + `metrics.json`, served with threshold fallback | Nothing trained anywhere in repo; ARCHITECTURE lists training as "Planned (Stage C stretch)" |
| RAG: idempotent populate script, ≥20 incidents, 6 classes ≥3 each, vector store | No `scripts/populate_vector_store.py`; `scripts/seed_kb.py` listed Planned, absent; corpus is static files |
| Dashboard Generator `POST /dashboard` | **Does not exist**: no service dir, no `fixtures/dashboards/`, no `metrics_catalog.json`, no Grafana in any compose file |
| EC2 current state | ARCHITECTURE says demo instance running with 7/7 E2E on 2026-07-11 (dev-IP-only SG; n8n Cloud egress not yet allowed) |

## Doc discrepancies noted (not fixed here)

- `docs/PETER-PAN-SPEC-CROSSWALK.md` §4.2 says Predictor `POST /predict`; ADR 0004,
  ARCHITECTURE, and the code use `POST /analyse`. Code + ADR win.
- Crosswalk §3.1 node 8 says the router reads `incident_class`; contracts freeze
  `TriageReport.category` as the routing field, with the 6→3 map applied in n8n
  before report generation. ADR 0004 wins.
- `fastapi-service-conventions` skill says shared models live at repo-root
  `contracts.py`; the enforced convention is a vendored copy per service checked
  against `docs/contracts/contracts.py`. Vendored convention wins.
