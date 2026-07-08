# ADR 0001 — PITER carryover into PETER PAN

- **Status:** accepted (2026-07-08)
- **Branch:** `cleanup/peter-pan-reset`, cut from `portfolio-archive-wip` @ `94193cb` (== `peter-pan/main`)
- **Canonical architecture:** [peter-pan-system.mmd](../peter-pan-system.mmd) · [peter-pan-n8n-flow.mmd](../peter-pan-n8n-flow.mmd)

## Context

This repository evolved from `piter-aiops` (Flask + Bedrock Agent + React SPA). PETER PAN is a
different system — n8n orchestration over FastAPI microservices (Ingestion, Predictor, RAG,
Guardrails, Tools API, LangGraph agent) with task-routed models (Bedrock, llama.cpp, Ollama)
and a Streamlit WebUI. Every tracked file was audited into KEEP / MIGRATE / DELETE / UNSURE
and the approved table applied on this branch. Everything deleted is recoverable from git
history (`git show 94193cb:<path>`) and from the `origin` remote (piter-aiops.git).

## Kept

- Repo tooling: `.gitignore`, `.dockerignore`, `LICENSE`, `ruff.toml`, `pytest.ini`,
  `requirements-dev.txt` (trimmed to standalone dev tools), `.claude/`, `.cursor/`, `.github/`.
- `frontend/` — the PITER React SPA, **parked as a bonus dashboard by explicit user decision**.
  Excluded from the build plan and CI; the diagrams specify a Streamlit WebUI instead.
- `evaluation/{demo_questions,rag_evaluation_cases,tool_evaluation_cases}.json` — golden-set seeds.
- To be rewritten before/during Stage A: `README.md` (stub now), `AGENTS.md`, `CLAUDE.md`,
  `.env.example`, `.github/copilot-instructions.md`, `.github/workflows/ci.yml` (lint-only interim).

## Migrated

| from | to | why |
|---|---|---|
| `app/enrichment_tools.py` + `incident_analysis.py`, `data_access.py`, `environment_codes.py`, `text_utils.py` | `services/tools-api/` | the four tools + full import closure |
| `app/services/escalation_{service,message}.py`, `notification_dispatch.py`, `action_groups/piter-escalation/lambda_function.py` | `services/tools-api/` (`escalation_lambda.py`) | preview-first escalation bridge → approval gate |
| `mcp/schemas/*.json` (4) | `services/tools-api/schemas/` | the real tool contracts; seed for the pydantic v2 contracts |
| `data/source/**` | `services/tools-api/data/` | canonical datasets the tools read |
| `app/guardrails.py` | `services/guardrails/` | deterministic regex floor under NeMo |
| `app/services/{local_rag,kb_corpus,kb_manifest}.py`, `app/validators.py` | `services/rag/` | offline TF-IDF RAG = deterministic Stage-A stub (user decision) |
| `knowledge_base/{incidents,runbooks,services}/**` | `services/rag/corpus/` | generic seed corpus |
| `scripts/{generate_alert_stream,generate_demo_data,validate_data}.py` | `predictive/datagen/` | Predictor/Ingestion demo + training fixtures |
| 16 test modules | `services/*/tests/` | reusable deterministic tests |

## Deleted (single commit `chore: remove legacy PITER files`)

Bedrock Agent action-group wiring, the Flask API (`app/`, `app.py`, `wsgi.py`) and its tests,
the MCP demo layer (logic already lived in `enrichment_tools.py`), PITER docs/infra/deploy
scripts, archived legacy frontends and datasets, PITER-branded KB content, and PITER submission
evidence (screenshots, presentation, evaluation reports — user decision). Root `Dockerfile`,
`docker-compose.yml`, `requirements.txt` go too; Stage A builds per-service equivalents.

## UNSURE — deliberately untouched, decide later

`app/services/structured_analysis.py` + its test (closest ancestor of the `TriageReport`
contract), `config/mcp.json.example`, `scripts/labs/**` (course material; belongs in the
course repo).

## Honest limitations after this cleanup

1. **Migrated Python is not importable** — modules still `import app.*` and carry PITER
   naming/docstrings. Stage A re-packages, renames, and re-greens the tests. `pytest` at repo
   root is expected RED until then; CI is lint-only on purpose.
2. `escalation_service.py` still loads the lambda by its old `action_groups/` path — rewired in Stage A.
3. `guardrails.py` imports `BedrockError` from the deleted `app/errors.py` — rewired in Stage A.

## Conflicts recorded (not silently resolved)

1. The task assumed the diagrams lived in `/docs`; they were untracked at repo root → adopted into `docs/`.
2. The task said PITER had **pydantic schemas**; the codebase has none. The actual contracts are
   the four JSON Schemas now in `services/tools-api/schemas/`. Phase 2 defines pydantic v2
   `Signal` / `Incident` / `TriageReport` fresh, seeded by them.
3. Tool-name mapping: `get_recent_deployments`→`correlate_deployments`,
   `get_service_owner`→`lookup_owner_and_escalation`, `find_similar_incidents`→same,
   `get_escalation_path`→escalation bridge. Renames land in Stage A.
4. Keeping `frontend/` contradicts the diagrams (Streamlit UI) — deliberate, parked, out of scope.
5. Local `main` = this branch's base + one revert commit (`7ec5a78`); base chosen to match `peter-pan/main`.
