# PETER PAN — Implementation Checklist (Course Spec Audit)

**Date:** 2026-07-14  
**Source of truth:** `docs/PROJECT-PLAN.md`, `docs/PETER-PAN-SPEC-CROSSWALK.md`, `docs/MASTER-CHECKLIST.md`  
**Domain:** AIOps incident triage (declared 1:1 crosswalk of the AI Property Triage final-project guideline)

Status: `[x]` verified · `[~]` partial · `[ ]` missing · `[!]` blocked

---

## Phase 1 — Repository Audit

| Item | Status | Evidence |
|------|--------|----------|
| Assignment spec read | `[x]` | `docs/PROJECT-PLAN.md`, `docs/PETER-PAN-SPEC-CROSSWALK.md` |
| Repo structure mapped | `[x]` | 11 services, Streamlit UI, n8n flow, compose, infra |
| Implementation checklist | `[x]` | This file |
| Duplicate/dead code audit | `[x]` | `frontend/` empty placeholder; `incoming/` session scratch only |
| Security baseline | `[~]` | `.env` gitignored; regex secret scan clean; NeMo/GGUF gaps documented |

---

## Phase 2 — Local Development

| Item | Status | Evidence |
|------|--------|----------|
| Python 3.12+ | `[x]` | `.venv` Python 3.14.5; target 3.12 in Dockerfiles |
| Docker Desktop | `[x]` | Docker 29.6.1, Compose v5.3.0 |
| Ollama installed | `[x]` | v0.31.2; models: `llama3.1:8b`, `llama3.2:3b` |
| Docker Compose stack | `[x]` | All 13 containers healthy (2026-07-14) |
| ChromaDB population | `[x]` | `scripts/populate_vector_store.py` — 24 incidents |
| Startup workflow documented | `[x]` | `docs/local-development.md`, `docs/setup.md` |
| n8n localhost URLs | `[x]` | Compose env vars wire internal hostnames |

---

## Phase 3 — Required Services (Course §4 crosswalk)

### RAG (`:8003`)

| Requirement | Status | Notes |
|-------------|--------|-------|
| `GET /healthz` | `[x]` | |
| `POST /query` | `[x]` | Returns `{answer, citations, refused}` |
| `POST /retrieve` | `[~]` | Retrieval via `/query`; no separate `/retrieve` |
| LangChain | `[~]` | Custom prompt path; LangChain not in requirements |
| ChromaDB persistent | `[x]` | Volume `rag-chroma`; `PETER_VECTOR_BACKEND=chroma` |
| GGUF llama.cpp | `[~]` | Code behind `GGUF_MODEL_PATH`; not loaded locally |
| ≥20 synthetic docs | `[x]` | 24 incidents, 6 classes × 4 |
| Citations + refusal | `[x]` | 35 RAG tests pass |

### Image Analyser → **Predictor** (`:8002`)

| Requirement | Status | Notes |
|-------------|--------|-------|
| PyTorch classifier | `[x]` | 1D-CNN transfer learning |
| `POST /analyse` | `[x]` | Crosswalk of `/analyse` (course: image) |
| >75% test accuracy | `[x]` | `metrics.json`: 88.1% |
| EWMA/z-score floor | `[x]` | Deterministic override |
| Image Analyzer (`:8007`) | `[~]` | ResNet scaffold; not in n8n flow |

### Guardrails (`:8004`)

| Requirement | Status | Notes |
|-------------|--------|-------|
| `POST /check/input` | `[x]` | |
| `POST /check/output` | `[x]` | |
| Schema `{passed, flags, reason}` | `[x]` | Frozen contract |
| NeMo Guardrails | `[~]` | Regex floor active; NeMo stubbed |
| <5% false positive | `[x]` | FP suite in tests |
| Prompt surfaces wired | `[~]` | Scaffolds exist; not wired to live engine |

### LangGraph Agent (`:8006`)

| Requirement | Status | Notes |
|-------------|--------|-------|
| `POST /agent/run` | `[x]` | Returns validated `TriageReport` |
| 3-node graph | `[x]` | plan → specialists → synthesise |
| RAG + Predictor tools | `[x]` | Predictor via n8n; LangGraph uses RAG + Tools |
| Partial failure handling | `[x]` | Graph tests 98% coverage |

---

## Phase 4 — n8n Workflow

| Item | Status | Evidence |
|------|--------|----------|
| Export `n8n/peter-flow.json` | `[x]` | 8-node spine + CTX branches |
| Guardrails in/out | `[x]` | Nodes 2 + 7 |
| RAG + Predictor + LangGraph | `[x]` | Node 5 tool calls |
| Gemini/GPT-4o (Stage C) | `[~]` | Stage A uses fixture-llm |
| Failure/retry handling | `[x]` | Node onError settings |
| Env-var URLs | `[x]` | Compose injects service URLs |
| Bootstrap script | `[x]` | `scripts/bootstrap_n8n_local.py` |
| Static flow tests | `[x]` | 183 n8n tests pass |

---

## Phase 5 — WebUI

| Item | Status | Evidence |
|------|--------|----------|
| Streamlit (not Gradio) | `[x]` | `ui/app.py` |
| Assistant tab (Ollama) | `[x]` | Fixture LLM + Ollama fallback |
| Incident submission → n8n | `[x]` | `submit_signal()` |
| Loading/error states | `[x]` | UI tests 44 pass |
| TriageReport display | `[x]` | Review queue tab |
| Playwright E2E | `[~]` | Run during validation session |

---

## Phase 6 — Docker & Infrastructure

| Item | Status |
|------|--------|
| Dockerfile per service | `[x]` 11/11 |
| `.dockerignore` | `[x]` per service |
| Health checks | `[x]` `/healthz` + compose healthcheck |
| Non-root containers | `[x]` useradd pattern |
| `docker-compose.yml` | `[x]` |
| `docker-compose.ec2.yml` | `[x]` |
| `.env.example` | `[x]` key-less |
| `infra/aws/` CloudFormation | `[x]` |
| `scripts/` helpers | `[x]` |
| `postman/` collection | `[x]` | `postman/peter-pan-core-apis.postman_collection.json` |

---

## Phase 7 — AWS EC2

| Item | Status | Evidence |
|------|--------|----------|
| t3.large instance | `[x]` | `18.234.123.139` per COMPLIANCE-MATRIX |
| Docker on EC2 | `[x]` | compose deployed |
| SG restricted /32 | `[x]` | No `0.0.0.0/0` |
| Chroma on EBS volume | `[x]` | count 24 verified |
| GGUF on EBS | `[ ]` | Session D — model not downloaded |
| n8n on-instance | `[x]` | Internal service URLs |
| Public health 10/10 | `[x]` | `scripts/test_ec2_public_health.py` |

---

## Phase 8 — Testing

| Suite | Status | Result |
|-------|--------|--------|
| `scripts/run_all_tests.py` | `[x]` | All suites green (2026-07-14) |
| E2E dry-run | `[x]` | 22 evaluation tests pass |
| E2E compose (n8n) | `[x]` | 7/7 golden signals pass (2026-07-14) |
| curl health endpoints | `[x]` | 8001–8004 → HTTP 200 |
| Playwright UI | `[x]` | Submission HTTP 200; screenshot saved |

---

## Phase 9 — Security

| Item | Status |
|------|--------|
| No secrets in git | `[x]` |
| `.env` gitignored | `[x]` |
| Upload validation (image) | `[x]` |
| EC2 SG not public | `[x]` |
| Non-root containers | `[x]` |

---

## Phase 10 — Documentation

| Doc | Status |
|-----|--------|
| `README.md` | `[x]` exists; updated this session |
| `docs/architecture.md` | `[x]` → `docs/ARCHITECTURE.md` |
| `docs/setup.md` | `[x]` created |
| `docs/local-development.md` | `[x]` created |
| `docs/aws-deployment.md` | `[x]` created |
| `docs/n8n-workflow.md` | `[x]` created |
| `docs/api.md` | `[x]` created |
| `docs/testing.md` | `[x]` created |
| `docs/security.md` | `[x]` created |
| `docs/demo-guide.md` | `[x]` → `docs/presentation/DEMO-SCRIPT.md` + `docs/demo-guide.md` |

---

## Remaining Gaps (honest)

1. **Prompt Engineering Log** — 5 surfaces; V1 only on surfaces 1–2; surfaces 3–5 need iterations (25% rubric).
2. **GGUF generation on EC2** — retrieval works; llama.cpp model not on disk.
3. **NeMo Guardrails** — deterministic regex floor meets demo path; full NeMo not installed.
4. **LangChain** — custom RAG path; not using LangChain package.
5. **Image Analyzer in n8n** — Predictor is the graded crosswalk; vision service is supporting seam only.
6. **Live Gemini/GPT-4o** — Stage A fixture-llm; Stage C optional.
