# PETER PAN — Phase −1 audit & handoff

Canonical audit record for the `chore/repo-audit` cleanup pass.  
Branch baseline: `775179b` → audit commits on `chore/repo-audit`  
Tag: `pre-cleanup-20260716` → `cb66ebb` (rollback anchor before WIP cleanup)  
Date: 2026-07-16

---

## Baseline

### Metadata

| Item | Value |
|------|-------|
| Python | 3.14.5 (`.venv`) |
| Host OS | Windows 10 |
| Branch | `chore/repo-audit` @ `775179b` |
| `.env` | Present (required for compose) |

---

### Tests — `python scripts/run_all_tests.py`

**Exit code: 0 — All suites green.**

| Suite | Passed | Failed | Error | Skipped | Notes |
|-------|--------|--------|-------|---------|-------|
| dashboard-generator | 22 | 0 | 0 | 0 | cov 86.50% |
| fixture-llm | 27 | 0 | 0 | 0 | cov 93.15% |
| guardrails | 78 | 0 | 0 | 0 | cov 96.73% |
| image-analyzer | 2 | 0 | 0 | 0 | |
| ingestion | 22 | 0 | 0 | 0 | cov 95.45% |
| integration-stubs | 8 | 0 | 0 | 0 | cov 96.23% |
| langgraph-agent | 16 | 0 | 0 | 0 | cov 98.11% |
| predictor | 54 | 0 | 0 | 0 | cov 97.40% |
| rag | 50 | 0 | 0 | 0 | cov 94.18% |
| tools-api | 103 | 0 | 0 | 0 | cov 82.43% |
| peter_observability | 6 | 0 | 0 | 0 | cov 100% |
| ui | 48 | 0 | 0 | 0 | cov 88.49% |
| n8n | 184 | 0 | 0 | 0 | flow contract tests |
| evaluation | 22 | 0 | 0 | 0 | cov 90.11% |
| **TOTAL** | **642** | **0** | **0** | **0** | |

Warnings (non-failing): Starlette/httpx deprecation across FastAPI test clients; LangGraph asyncio deprecation; Chroma telemetry deprecation on one RAG test.

Repo-root `pytest --collect-only` is **not valid** for this repo (47 collection errors — duplicated basenames, per-service roots). Canonical runner is `scripts/run_all_tests.py`.

---

### Linter — `ruff check .`

**Exit code: 0 — All checks passed.**

Config: `ruff.toml` (F, E4, E7, E9; py312 target).

### Type checker

**Not configured.** No `pyproject.toml` mypy/pyright section. `.mypy_cache/` gitignored only.

---

### Docker Compose — cold start

```text
docker compose down
docker compose up -d
```

**Exit code: 0 — stack came up.** ~41s to healthy.

| Service | Container status | Host port |
|---------|------------------|-----------|
| ingestion | healthy | 8001 |
| predictor | healthy | 8002 |
| rag | healthy | 8003 |
| guardrails | healthy | 8004 |
| tools-api | healthy | 8005 |
| langgraph-agent | healthy | 8006 |
| image-analyzer | healthy | 8007 |
| dashboard-generator | healthy | 8008 |
| fixture-llm | healthy | 8010 |
| integration-stubs | healthy | 8020 |
| n8n | healthy | 5678 |
| grafana | healthy | 3000 |
| ui | **not started** | profile `ui` |
| n8n-bootstrap | **not started** | profile `bootstrap` |

Stale container `peter-pan-n8n-bootstrap-1` from prior run: Exited (1) 21h ago — not part of this cold up.

`docker compose config --quiet`: pass.

---

### Entrypoints — live HTTP probes (post cold-up)

| Entrypoint | URL | Result |
|------------|-----|--------|
| ingestion | `http://127.0.0.1:8001/healthz` | 200 `{"status":"ok","service":"ingestion"}` |
| predictor | `http://127.0.0.1:8002/healthz` | 200 |
| rag | `http://127.0.0.1:8003/healthz` | 200 |
| guardrails | `http://127.0.0.1:8004/healthz` | 200 |
| tools-api | `http://127.0.0.1:8005/healthz` | 200 |
| langgraph-agent | `http://127.0.0.1:8006/healthz` | 200 |
| image-analyzer | `http://127.0.0.1:8007/healthz` | 200 |
| dashboard-generator | `http://127.0.0.1:8008/healthz` | 200 |
| fixture-llm | `http://127.0.0.1:8010/healthz` | 200 |
| integration-stubs | `http://127.0.0.1:8020/healthz` | 200 |
| n8n | `http://127.0.0.1:5678/healthz` | 200 |
| grafana | `http://127.0.0.1:3000/api/health` | 200 database ok |
| ui (Streamlit) | `http://127.0.0.1:8501` | **not running** (profile not enabled) |

### Entrypoints — CLI / scripts

| Entrypoint | Command | Result |
|------------|---------|--------|
| E2E harness | `python evaluation/run_e2e.py --dry-run` | pass — 7 golden signals loaded |
| Test orchestrator | `python scripts/run_all_tests.py` | pass (see above) |

### Entrypoints — host import smoke

Services are **self-contained deployment units** (per `AGENTS.md`); repo-root import of service `app.py` files fails by design (relative imports / missing package on `PYTHONPATH`).

| Module | Host import from repo root |
|--------|---------------------------|
| `packages/peter_observability/observability` | **OK** (with `sys.path` insert) |
| `fixture_llm.app` | OK |
| `integration_stubs.app` | OK |
| ingestion, predictor, rag, guardrails, tools-api, langgraph-agent, image-analyzer, dashboard-generator | **FAIL** — require service rootdir or container |

All ten FastAPI services respond on `/healthz` inside running containers.

---

### Capability snapshot (baseline framing)

This repo is **production-shaped**, not scaffold:

- **642 tests**, all green, across 10 microservices + observability package + Streamlit UI lib + n8n flow contracts + evaluation harness.
- **Full compose stack** (minus optional profiles) cold-starts and reaches healthy on all Layer 3 services + n8n + Grafana.
- **Fixture-first path** verified: `run_e2e.py --dry-run` loads golden signals without live HTTP/LLM.

Stage 4 focus: **ORPHANED** — code that works and is tested but unreachable from any entrypoint. Baseline confirms the platform runs; reachability graph is Stage 4 work.

---

## Stage 2

Tool-driven inventory. No repo edits. Wiring captured per unit for Stage 4.

**Demo path definition (2-week filter):**

| Path | Entry | What runs |
|------|-------|-----------|
| **Canonical demo (n8n)** | `POST /webhook/peter-signal` via ingestion or UI | `peter-flow.json` → guardrails → predictor/RAG/langgraph/tools → output guardrails → team stubs |
| **Golden fixtures** | `evaluation/golden_signals.json` (7 cases) | Same expectations as n8n path; `run_e2e.py --entrypoint n8n` (default) |
| **Alternate (layer3)** | `run_e2e.py --entrypoint layer3` | guardrails → **langgraph-agent only** → guardrails (skips n8n, predictor-as-node, ingestion) |
| **Off-demo** | compose health / portfolio | image-analyzer, dashboard-generator HTTP, datagen CLIs, docs/llm_client spec |

---

### Evidence (tool output)

#### vulture — `vulture services packages evaluation scripts ui n8n --min-confidence 80`

Repo-root `vulture .` **crashes** on Python 3.14 (AST walk error in full tree). Scoped run exit 3, **21 hits**:

```text
packages/peter_observability/tests/test_observability.py:45: unused variable 'receive' (100%)
packages/peter_observability/tests/test_observability.py:45: unused variable 'scope' (100%)
packages/peter_observability/tests/test_observability.py:45: unused variable 'send' (100%)
services/tools-api/tests/test_notification_dispatch.py: (18× mock callback unused vars, 100%)
services/tools-api/tools_api/enrichment_tools.py:188: unused variable 'history_path' (100%)
```

#### ruff — `ruff check --select F401,F811,F841 .`

```text
All checks passed!
```

#### pytest coverage — repo root `pytest --cov=. --cov-report=term-missing`

**Not run** — invalid monorepo layout (same as baseline). Per-suite coverage from Stage 1 baseline (all ≥80% gates met).

#### deptry — `deptry services packages evaluation ui --requirements-files requirements-dev.txt`

Root has no `pyproject.toml`; monorepo uses **per-service `requirements.txt`**. Scan against dev-only root file:

```text
Found 167 dependency issues.
```

Dominant pattern: **DEP001** `fastapi`/`starlette`/`botocore`/`PIL` "missing" because service deps are not merged into root requirements-dev.txt. **DEP002** `pytest-cov`, `ruff` flagged unused at repo root (CI tools, not imported). **Tool verdict:** deptry at root is misleading; per-service deptry not run (would need 10 invocations).

#### pytest collect-only — repo root `pytest --collect-only -q services packages ui n8n evaluation`

```text
258 tests collected, 47 errors in 2.74s
ERROR ui/tools-api/tests/... (wrong rootdir — duplicated basenames)
```

Per-suite (canonical): **642 collected, 0 skipped, 0 xfailed** (matches Stage 1 run).

#### git ls-files -i -c --exclude-standard

```text
(empty — no tracked-but-ignored files)
```

#### git ls-files \| cache patterns

**0** tracked `__pycache__`, `.pyc`, or `.pytest_cache` files.

#### Fossilized (last touch — selected units)

| Path | Last touch |
|------|------------|
| `services/*` (core 6) | 5–20 hours ago |
| `services/image-analyzer` | 5 days ago |
| `predictive/datagen/` | 6 days ago |
| `infra/` | 3 days ago |
| `scripts/_ec2_layer2_*.sh` | **absent** (prior audit proposed delete; already removed) |

---

### Inventory — deployment units & major modules

Sorted by bucket. **Demo?** = on canonical n8n golden path. **Invoked by** = concrete callers only.

#### KEEP — on demo path or infrastructure spine

| Unit | Bucket | Demo? | Tests | Invoked by |
|------|--------|-------|-------|------------|
| `services/ingestion/` | KEEP | **YES** | 22 | compose `:8001`; n8n webhook target (`N8N_WEBHOOK_URL`); `run_e2e.py --entrypoint n8n`; `ui/app.py` Signal submit |
| `n8n/peter-flow.json` | KEEP | **YES** | 184 (contract) | compose `:5678`; bootstrap / `scripts/bootstrap_n8n_local.py`; ingestion forwards signals |
| `services/guardrails/` | KEEP | **YES** | 78 | n8n nodes `Guardrails Input/Output Check` → `/check/input`, `/check/output`; `run_e2e.py` (both entrypoints); compose `:8004`; guardrails → `PETER_TOOLS_URL` for owner verify |
| `services/predictor/` | KEEP | **YES** | 54 | n8n `Predictor Tool` → `/analyse`; compose `:8002`; **not** called by layer3 e2e shortcut |
| `services/rag/` | KEEP | **YES** | 50 | n8n `RAG Query Tool` → `/query`; langgraph-agent internal `_call_rag`; compose `:8003` |
| `services/langgraph-agent/` | KEEP | **YES** | 16 | n8n `LangGraph Agent Tool` → `/agent/run`; `run_e2e.py --entrypoint layer3`; calls RAG + tools-api internally; compose `:8006` |
| `services/tools-api/` (core) | KEEP | **YES** | 103 | n8n → `/tools/service_context`, `/escalations`; langgraph → `/tools/service_context`, `/tools/similar_incidents`; guardrails owner_check → `PETER_TOOLS_URL`; compose `:8005` |
| `services/fixture-llm/` | KEEP | **YES** | 27 | n8n OpenAI-compatible credential → `fixture-llm:8000/v1`; compose `:8010`; bootstrap sets `PETER_FIXTURE_LLM_URL` |
| `services/integration-stubs/` | KEEP | **YES** | 8 | n8n → `/github/deployments`, `/review-queue`, `/teams/{team}`, `/slack`; `run_e2e.py` polls `/deliveries`; compose `:8020` |
| `evaluation/` | KEEP | **YES** | 22 | CLI `run_e2e.py`; CI gate; loads `golden_signals.json` |
| `evaluation/golden_signals.json` | KEEP | **YES** | (fixture) | `run_e2e.py`, n8n contract tests |
| `docs/contracts/contracts.py` | KEEP | **YES** | via n8n+eval | Imported by all services' `contracts.py`; `run_e2e.py` validation |
| `docker-compose.yml` | KEEP | spine | config | Default stack 12 services; profiles `ui`, `bootstrap` |
| `scripts/run_all_tests.py` | KEEP | CI | — | CI / developer test orchestrator |
| `scripts/bootstrap_n8n_local.py` | KEEP | demo setup | via n8n tests | Bootstrap profile; n8n flow import |
| `grafana` (compose) | KEEP | demo observability | — | compose `:3000`; dashboard-generator depends_on |

#### KEEP — off demo path but intentional / portfolio

| Unit | Bucket | Demo? | Tests | Invoked by |
|------|--------|-------|-------|------------|
| `services/image-analyzer/` | KEEP | **NO** | 2 | compose `:8007` only; **ORPHANED from demo:** no caller in n8n, run_e2e, ui (evidence: grep + services/README "not on golden path"; course crosswalk — prior LAYER-2 audit said KEEP) |
| `services/dashboard-generator/` | KEEP | **NO** | 22 | compose `:8008`; `scripts/test_layer3_edge_matrix.py` POST `/dashboard`; **ORPHANED from demo:** no n8n node, no ui, no run_e2e (evidence: grep n8n/peter-flow.json, ui/, evaluation/) |
| `ui/` (Streamlit) | KEEP | **partial** | 48 | compose profile `ui` `:8501`; submits to n8n webhook (demo-adjacent Layer 1); not in default compose up |
| `predictive/datagen/` | KEEP | **NO** | — | CLI only (`generate_demo_data.py`, `generate_alert_stream.py`, `validate_data.py`); regenerates gitignored fixtures per PROJECT-PLAN; no runtime caller |
| `docs/llm_client/llm_client.py` | KEEP | **NO** | — | Canonical Layer 4 spec; **ORPHANED from runtime:** no `import` in any `services/**/*.py` (evidence: grep); Stage A uses fixture-llm HTTP instead |
| `packages/peter_observability/` | KEEP | **NO** | 6 | **ORPHANED from runtime:** only package copy exists; no service vendors it yet (evidence: glob `**/observability.py` → 1 file; grep services → 0 imports). ADR says copy into services — not done |
| `infra/` | KEEP | deploy | — | CloudFormation / EC2 docs path |
| `graphify-out/` | KEEP | tooling | — | graphify CLI output; large tracked JSON churn |
| `.claude/skills/` | KEEP | agent | — | canonical skills (post-WIP consolidation) |

#### DELETE-PROPOSED

| Path | Bucket | Demo? | Evidence |
|------|--------|-------|----------|
| `services/tools-api/tools_api/enrichment_tools.py` `history_path` param | DELETE-PROPOSED | NO | vulture 100% unused variable L188 |
| `scripts/_ec2_layer2_*.sh` (5 files) | *(already gone)* | — | Prior LAYER-2-PROPOSED-DELETIONS; glob 0 matches |
| `graphify-out/` dated snapshots `2026-07-16/` | DELETE-PROPOSED | NO | Duplicate of root graphify-out; 30k+ line JSON churn; regenerated by `graphify update` |

#### STALE-DOC

| Path | Bucket | Evidence |
|------|--------|----------|
| `docs/MASTER-CHECKLIST.md`, `IMPLEMENTATION-CHECKLIST.md`, `PRE-PUBLIC-CHECKLIST.md`, `COMPLIANCE-MATRIX.md`, `DOCS-RECONCILIATION.md` | STALE-DOC | Overlapping checklists; WIP added PRODUCT-STORY/ARCHITECTURE as new anchors — doc:doc contradiction risk |
| `docs/api.md` | STALE-DOC | Documents `POST /tools/similar-incidents` (hyphen); code is `/tools/similar_incidents` (underscore) — doc vs code |
| `docs/DOCS-RECONCILIATION.md` L224 | STALE-DOC | References `docs/llm_client.py`; actual path `docs/llm_client/llm_client.py` |
| Deleted `PLAN.md`, `LAYER-2-PROPOSED-DELETIONS.md` | STALE-DOC | Removed in WIP commit 775179b; content partially superseded by this audit |

#### DELETE-OBVIOUS

| Path | Bucket | Evidence |
|------|--------|----------|
| `.audit-venv/` (local) | DELETE-OBVIOUS | Throwaway Stage 2 tool venv; untracked; not in repo |
| Tracked cache artifacts | *(none)* | git ls-files cache patterns → 0 |

#### UNSURE

| Path | Bucket | Why |
|------|--------|-----|
| `services/tools-api/tools_api/incident_analysis.py` `analyze_incident()` | UNSURE | 103 suite tests cover module; **no HTTP route**; only test_direct + internal partial imports — portfolio demo script or dead weight? |
| `services/tools-api/tools_api/notification_dispatch.py` | UNSURE | 63% cov; heavily tested; demo path uses `preview=True` on `/escalations` (never dispatches); Stage C SNS/Slack path |
| `services/tools-api/` routes `/tools/recent_deployments`, `/tools/escalation_preview` | UNSURE | **ORPHANED from n8n:** n8n uses integration-stubs for deploys, not this route; langgraph calls `/tools/similar_incidents` + `/tools/service_context` only; routes exercised by tests + `evaluation/tool_evaluation_cases.json` |
| `docs/prompt-log/` (25% deliverable) | UNSURE | Course rubric artifact; not on runtime demo path |

---

### ORPHANED summary (tested-but-unreachable from demo entrypoints)

| Unit / surface | Works? | Tested? | No caller in | Verdict |
|----------------|--------|---------|--------------|---------|
| `image-analyzer` service | yes (healthz) | 2 tests | n8n, run_e2e, ui | **ORPHANED off-demo** — portfolio/crosswalk only |
| `dashboard-generator` service | yes | 22 tests | n8n, run_e2e, ui | **ORPHANED off-demo** — edge-matrix script only |
| `packages/peter_observability` | yes | 6 tests | all services (not vendored) | **ORPHANED** — spec without adoption |
| `docs/llm_client/llm_client.py` | n/a | no | services | **ORPHANED spec** — fixture-llm is actual Stage A seam |
| tools-api HTTP `/tools/recent_deployments` | yes | yes | n8n (uses stubs/github), langgraph | **ORPHANED route** — test/eval cases only |
| tools-api HTTP `/tools/escalation_preview` | yes | yes | n8n (uses `/escalations` with preview flag) | **ORPHANED route** — duplicate of escalation path |
| `notification_dispatch` module | yes | 18+ tests | demo `/escalations` preview=True | **ORPHANED on demo** — intentional preview-first; live dispatch is Stage C |

Off-demo orphans are **not bugs** for the 2-week demo filter — they are portfolio/course surface.

---

### Bucket counts

| Bucket | Count (units listed) |
|--------|---------------------|
| KEEP | 22 |
| DELETE-PROPOSED | 2 (+ 5 already deleted) |
| STALE-DOC | 4 groups |
| DELETE-OBVIOUS | 1 (local only) |
| UNSURE | 4 |

---

### Three biggest mess sources

1. **Documentation sprawl** — 5+ overlapping checklists + ARCHITECTURE + PRODUCT-STORY + master doc; WIP started consolidation but Stage 5 target (single README + single rules file) not reached.
2. **graphify-out tracked JSON** — tens of thousands of lines regenerated on doc edits; duplicates under `2026-07-16/`.
3. **Dual reachability models** — n8n demo path vs layer3 e2e shortcut vs tools-api HTTP routes that tests cover but orchestration bypasses (deploy correlation via integration-stubs, not tools-api).

---

### Alarms

- **No secrets in tracked files** (spot-check: `.env` gitignored; compose uses env interpolation).
- **642/642 green** — inventory is about reachability, not quality collapse.
- **vulture repo-root crash** — tool gap on Py3.14 / full tree; use scoped paths.
- **deptry root invalid** — per-service requirements not visible to monorepo root scan.
- **Prior ec2 one-shot scripts already deleted** — LAYER-2 proposed-deletions partially executed out-of-band.

---

### Stage 2 summary

The repo is a **complete Stage A platform**: ten services, n8n orchestration, 642 tests, compose spine. Stage 2 wiring shows the **canonical demo path is narrow** (ingestion → n8n → guardrails/predictor/rag/langgraph/tools/fixture-llm/stubs). Several **tested units are deliberately off-demo** (image-analyzer, dashboard-generator, observability package, llm_client spec) — orphans for portfolio, not failures. The actionable orphans for Stage 4 are **within** the demo spine: tools-api routes and modules that tests exercise but n8n/langgraph never HTTP-call, and the layer3 e2e shortcut that skips predictor-as-node.

**STOP** — awaiting bucket-by-bucket approval for Stage 3 deletions.

---

### Stage 3 follow-up — decisions recorded

#### UNSURE → all KEEP (no code changes)

| Item | Decision | Rationale |
|------|----------|-----------|
| `analyze_incident()` | **KEEP** | Test-only entry today; enrichment core of PETER — wire candidate, not cut |
| `notification_dispatch` | **KEEP** | `preview=True` is demo choice; flip flag → live dispatch |
| `/tools/recent_deployments`, `/tools/escalation_preview` | **KEEP** | Wiring debt (see below); not deletion candidates |
| `docs/prompt-log/` | **KEEP** in `docs/` | 25% course deliverable; not archived |

#### Wiring debt (record only — do not resolve pre-demo)

Three wiring models coexist:

1. **n8n demo path** — deploy context via `integration-stubs` `/github/deployments`, not tools-api `/tools/recent_deployments`.
2. **langgraph-agent** — calls `/tools/service_context` + `/tools/similar_incidents` only.
3. **tools-api HTTP routes** — `/tools/recent_deployments` and `/tools/escalation_preview` are tested (`test_app.py`, `evaluation/tool_evaluation_cases.json`) but **not called by n8n or langgraph**.

Escalation: n8n uses `POST /escalations` with `preview=True`; separate `/tools/escalation_preview` route is parallel surface.

#### STALE-DOC archive — commit `aad10e2`

`git mv` only (+ new `docs/archive/README.md`). **DOCS-RECONCILIATION pre-check:** all substantive fixes (guardrail schema, incident_class, LangGraph tools, image-analyzer seam, EC2 honest status) already reflected in `ARCHITECTURE.md`; remainder is historical decision log → straight to archive.

| Moved to `docs/archive/` |
|---|
| `MASTER-CHECKLIST.md`, `IMPLEMENTATION-CHECKLIST.md`, `PRE-PUBLIC-CHECKLIST.md` |
| `COMPLIANCE-MATRIX.md`, `DOCS-RECONCILIATION.md`, `PETER-PAN-PROJECT-MASTER-DOC-EN.md` |
| `LAYER-2-VALIDATION.md`, `audits/*` |

Archive links fixed in commit after `aad10e2` (all active docs → `docs/archive/`).

---

## Handoff

Phase −1 complete. Stages 4–6 **not run** unless reopened. Use this section as the operator brief going into demo week.

### Platform state

- **642/642 tests green** (`python scripts/run_all_tests.py`)
- **Compose cold-up verified** — 12 default-stack services healthy (UI/bootstrap are profiles)
- **Canonical demo path:** ingestion → n8n `peter-flow.json` → guardrails → predictor/RAG/langgraph/tools → fixture-llm → integration-stubs → team webhooks
- **Golden fixtures:** `evaluation/golden_signals.json` (7 cases); `run_e2e.py --entrypoint n8n` is default
- **Rollback tag:** `pre-cleanup-20260716` @ `cb66ebb`

### Audit commits (this branch)

| Commit | What |
|--------|------|
| `4bdefc4` | Untrack `graphify-out/`, ignore `.audit-venv/` |
| `3c571a5` | Remove unused `history_path` kwarg; delete dated graphify snapshot |
| `aad10e2` | Archive superseded docs → `docs/archive/` |
| *(links)* | Fix all active-doc references to `docs/archive/` paths |
| *(this file)* | Audit + handoff committed |

### Wiring debt (record — do not fix pre-demo unless demo requires it)

Three parallel models; tests pass but orchestration does not use every HTTP surface:

| Gap | Detail |
|-----|--------|
| Deploy correlation | n8n → `integration-stubs` `/github/deployments`; tools-api `/tools/recent_deployments` exists + tested but **not called** |
| Escalation preview | n8n → `POST /escalations` with `preview=True`; `/tools/escalation_preview` route is parallel unused surface |
| LangGraph tools | Calls `/tools/service_context` + `/tools/similar_incidents` only |
| layer3 e2e shortcut | `run_e2e.py --entrypoint layer3` skips n8n + predictor-as-node (guardrails → langgraph → guardrails) |

**Not bugs** — one wiring change each to bring routes onto the demo path post-demo.

### Deferred on purpose (KEEP — portfolio / post-demo)

| Unit | Why it stays |
|------|----------------|
| `services/image-analyzer/` | Course crosswalk / vision fallback; tested, not on golden n8n path |
| `services/dashboard-generator/` | Grafana POST seam; tested; only health scripts call it today |
| `packages/peter_observability/` | Spec package; not yet vendored into services (ADR intent) |
| tools-api `/tools/recent_deployments`, `/tools/escalation_preview` | Wiring debt above; deletion rejected |
| `notification_dispatch` | Live dispatch behind `preview=True`; flip for Stage C |
| `docs/llm_client/` | Layer 4 canonical spec; Stage A uses fixture-llm HTTP |
| `analyze_incident()` | Enrichment core; test-only entry today — wire candidate |

### Known ops gap — n8n Cloud header auth

Manual fix still required (from prior Layer 2 validation):

1. In **n8n Cloud UI**, edit **Header Auth account** so the HTTP header **name** is exactly `X-Peter-Webhook-Secret` (the credential's header-name field — not the account display name).
2. Prefer demo via **EC2 on-instance n8n** (`docker compose` + bootstrap profile), **not** Cloud webhook ingress, until (1) is done.

Local compose bootstrap: `scripts/bootstrap_n8n_local.py` / `docker compose --profile bootstrap up`.

### Active doc SoT (post-archive)

| Doc | Role |
|-----|------|
| `README.md` | How to run |
| `docs/ARCHITECTURE.md` | Four-layer architecture |
| `docs/BUILD_PLAN.md` | Build gates |
| `docs/PRODUCT-STORY.md` | Market / PITER→PETER PAN narrative |
| `docs/PROJECT-PLAN.md` | Rubric crosswalk |
| `docs/prompt-log/` | 25% course deliverable |
| `docs/archive/` | Frozen superseded checklists — **do not edit** |

### End state

Audit closed. No further cleanup stages unless explicitly reopened.
