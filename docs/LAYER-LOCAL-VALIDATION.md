# Local Layer 1→3→2→4 Validation Report

**Date:** 2026-07-16  
**Scope:** Local Docker Compose (`--profile bootstrap --profile ui`)  
**Status:** `READY WITH DOCUMENTED LIMITATIONS`

Verification order (locked): **L1 → L3 → L2 → L4**. Demo path remains fixture-first.

---

## Executive summary

Local stack is healthy end-to-end. Streamlit renders TriageReports and reject cards; Playwright smokes pass for UI + n8n login; Layer 3 health/edge matrix pass; webhook golden/reject/destructive paths pass; Mock LLM seam uses compose-internal `fixture-llm`.

---

## Pass / fail matrix

| Layer | Check | Result |
|-------|--------|--------|
| L0 | `docker compose --profile bootstrap --profile ui` healthy | **PASS** |
| L0 | `scripts/test_layer3_health.py --include-support` | **PASS** (10/10) |
| L1 | UI unit (`ui/tests`) | **PASS** (48) |
| L1 | Playwright (`ui/tests/playwright`) | **PASS** (6/6) |
| L1 | Submit → TriageReport UI (orders-api) | **PASS** |
| L1 | Destructive → reject card | **PASS** |
| L3 | HTTP edge matrix (`scripts/test_layer3_edge_matrix.py`) | **PASS** |
| L3 | Per-service pytest (guardrails, rag, tools, langgraph, ingestion, predictor `--no-cov`, fixture-llm, dashboard) | **PASS** when run **per service dir** |
| L2 | `pytest n8n/tests` | **PASS** (184) |
| L2 | Webhook no-auth → 403 | **PASS** |
| L2 | Valid catalog `orders-api` → TriageReport (`application` / P1 / App Platform / 3 citations) | **PASS** |
| L2 | Missing `severity_hint` → TriageReport | **PASS** |
| L2 | Destructive → `destructive_data_action` | **PASS** |
| L2 | Short `sig-*` → `schema_invalid` | **PASS** |
| L2 | Unknown slug `api-gateway` → `flagged_for_review` (202) | **PASS** (documented) |
| L4 | n8n Mock Seam → fixture-llm (`peter-stage-a-fixture`) | **PASS** |
| L4 | UI Assistant fixture chat (Bearer token) | **PASS** |
| L4 | Optional Ollama Assistant smoke | **PASS** (local; not required for DoD) |
| L4 | Cloud Bedrock/Gemini | **SKIP** (not required for local DoD) |

---

## Fixes applied during this pass

1. **Bootstrap archives conflicting PETER\* workflows** (old Stage A stole `peter-signal` → empty 200 bodies).
2. **Mock LLM credential URL** uses `PETER_FIXTURE_LLM_INTERNAL_URL` default `http://fixture-llm:8000/v1` — host `.env` `PETER_FIXTURE_LLM_URL=http://localhost:8010/v1` must **not** be written into the n8n OpenAI credential.
3. **Normalize Signal** already maps missing `severity_hint` / optional fields to `null` (not `""`).
4. **fixture-llm** exposes `GET /v1/models` for OpenAI client probes.
5. **UI** `call_fixture_llm` sends `Authorization: Bearer ${PETER_SERVICES_TOKEN}` when set.
6. **Streamlit** success/reject/flagged render paths (prior phase) + Playwright suite under `ui/tests/playwright/`.

No spine / CTX node stripping. Flow export changed only for Normalize null mapping earlier; credential/bootstrap fixes do not require a new export.

---

## Documented limitations

| Limitation | Notes |
|------------|--------|
| Pytest multi-package collection | Running several `services/*/tests` in one pytest invocation can mis-collect sibling modules. Run **one service root at a time**. |
| Host `.env` in shell | Loading full `.env` into the process can break unit tests that expect unset `PETER_SERVICES_TOKEN` / `PETER_TOOLS_URL`. Prefer isolated pytest (fixtures now clear the common offenders). |
| Unknown catalog services | `api-gateway` (and similar) → output guardrails / review path (`202 flagged_for_review`), not a hard reject. Prefer catalog slugs (`orders-api`, `postgres-primary`, …). |
| Stage A workflow on volume | Survives n8n restarts until archived; bootstrap now archives non-canonical `PETER*` flows. |
| Cloud LLM / EC2 | Out of scope for this local DoD; see `docs/archive/LAYER-2-VALIDATION.md` for EC2 Layer 2. |
| n8n MCP Cloud | Authoring account is separate from local `:5678`; do not confuse Cloud WF IDs with local. |

---

## How to re-verify

```powershell
docker compose --profile bootstrap --profile ui up --build -d
.\.venv\Scripts\python.exe scripts\test_layer3_health.py --include-support
.\.venv\Scripts\python.exe scripts\test_layer3_edge_matrix.py
.\.venv\Scripts\python.exe -m pytest ui/tests -q
.\.venv\Scripts\python.exe -m pytest ui/tests/playwright -q
.\.venv\Scripts\python.exe -m pytest n8n/tests -q
# If webhook empty/403 conflict:
.\.venv\Scripts\python.exe scripts\bootstrap_n8n_local.py
```

Secrets stay in `.env` / process env only — never commit `.env`, live WF IDs, or tokens.
