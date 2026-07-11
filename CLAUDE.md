# CLAUDE.md — PETER PAN

Working memory for Claude Code on this repo. Read before acting.

## What this is
PETER PAN — a self-hostable, predictive, agentic incident-response platform (AIOps triage).
Built as a 1:1 crosswalk of the AI Property Triage final-project guideline into the incident-ops domain: same graded capabilities, same rubric lines, AIOps instead of real estate.

PETER = Priority · Enrichment · Triage · Escalation · Resolution
PAN = Predictive · Agentic · Navigator

## Golden rules (apply to every task)
1. **Audit before action.** Read the relevant code/config and state a plan before editing. No edits on assumption.
2. **Phased execution with approval gates.** Break work into phases; pause for explicit approval before any destructive or consequential step (deletes, migrations, deploys, force-push, `docker compose down -v`, dropping data).
3. **Deterministic floors override the LLM.** The regex guardrail floor and the EWMA/z-score predictor floor have final say. Never let a change route around them.
4. **Synthetic data only.** No real PII, secrets, customer incidents. Ever. Not in code, fixtures, commits, or logs.
5. **Secrets via `.env` + Secrets Manager.** Never hardcode keys. Never commit `.env`. `.env.example` stays key-less.
6. **Be brief.** Short, direct answers. Concrete diffs over prose. Decide autonomously where context allows rather than asking.

## Repo layout
```
/n8n                    → exported flow JSON (import target for the 8-node spine)
/services
  /ingestion            → FastAPI · POST /signals · validate + normalise Signal
  /predictor            → FastAPI · POST /analyse · EWMA floor (impl); PyTorch stubbed
  /rag                  → FastAPI · POST /query · TF-IDF retrieval (impl); llama.cpp stubbed
  /guardrails           → FastAPI · POST /check/input + /check/output · regex floor (impl); NeMo stubbed
  /tools-api            → FastAPI · tools + escalation preview + audit log
  /langgraph-agent      → FastAPI · POST /agent/run · planner→tools→synthesiser
  /fixture-llm          → Stage A seam: OpenAI-compatible deterministic fixture server
  /integration-stubs    → Stage A seam: team webhook stubs + review-queue receiver
/ui                     → Streamlit WebUI — Stage B (skeleton exists)
/scripts                → run_all_tests.py, bootstrap_n8n_local.py, seed_kb.py (planned)
/docs                   → ARCHITECTURE.md (entry point), diagrams, ADRs, contracts, audits
/evaluation             → frozen golden sets + run_e2e.py harness (do not mutate mid-run)
/predictive             → datagen + training pipeline (Stage C)
```

## Service contracts (do not break silently)
| Service | Endpoint | In → Out |
|---|---|---|
| Ingestion | `POST /signals` | `Signal` → forwarded n8n response |
| RAG | `POST /query` | `{query, limit}` → `{answer, citations, refused}` |
| Predictor | `POST /analyse` | `{incident?, metric_window_ref?, window?}` → `{category, severity, confidence, method, scores}` |
| Guardrails | `POST /check/input`, `/check/output` | `{signal}` / `{report, service?, environment?}` → `{pass, flags, reason}` |
| Tools API | `/tools/*`, `POST /escalations`, `GET /audit` | deterministic facts, preview-first escalation, audit records |
| LangGraph | `POST /agent/run` | `{incident, question?}` → `TriageReport` |

Predictor categories: `cpu_saturation`, `memory_leak`, `db_lock_contention`, `replication_lag`, `error_rate_spike`, `normal`. Severity 1–5 → P4–P1.

Every core service exposes `/healthz`. Before any demo run:
```powershell
python scripts/run_all_tests.py   # all service pytest suites
docker compose config --quiet     # compose syntax check
python evaluation/run_e2e.py --dry-run  # fixture load, no HTTP
```
The full compose-backed E2E (Ingestion → n8n → TriageReport) was verified for all
three golden signals on 2026-07-11. It requires the compose stack and explicit n8n
bootstrap profile. The Stage A writer has a deterministic contract-valid fallback for
local parser incompatibility; do not describe that fallback as a real-provider result.

## Build order (guideline-aligned)
Stage A: Layer 2 (n8n spine) + Layer 3 (services) first — this is the graded core.
Stage B: Layer 1 (WebUI) once services are stable.
Prompt Engineering Log grows from Phase 2 onward — 5 surfaces × 5 iterations, ≥10 frozen test cases each.

## n8n MCP safety (hard rules — violating these breaks production)
- **Never** call `test_workflow` on a live webhook/Telegram-triggered flow — it deregisters the production webhook.
- Use `update_workflow` with an `operations` array as the safe modification path.
- Credential bindings do **not** inherit — set explicitly via `setNodeCredential`.
- `create_workflow_from_code` cooks escape sequences in template literals — use `String.fromCharCode()` / `\uXXXX` for any Hebrew in Code nodes.
- Structured Output Parser nodes imported via JSON store `jsonSchemaExample` as a parsed object, not a string — fix with `setNodeParameter`.
- Perplexity node v2 needs an explicit `operation` discriminator alongside `resource: "search"`.
- Project-scope credential mismatch is the most common `publish_workflow` failure — check scope first.
- `get_execution` needs both `executionId` and `workflowId`; use `includeData: true` with filtered `nodeNames` to avoid response-size limits.

## Deployment scope (portfolio / demo)
Single EC2 t3.large, six core services plus local support containers via docker-compose. Inbound restricted to n8n egress + dev IP — **never 0.0.0.0/0**. Containers non-root. GGUF on EBS. Design for ≤5 concurrent users, ≤1 signal/sec, ≤10k KB docs. No formal SLA — graceful degradation + recoverable restart is the failure model. The production path is planned for `docs/deployment.md`; it is not implemented in Stage A.

## Declared deviations (state upfront, never hide)
1. AIOps domain instead of real estate.
2. Time-series metric windows instead of images for the classifier (vision fallback available).
3. Bedrock Claude alongside Gemini/GPT-4o; pgvector alongside ChromaDB — one-node swaps.

## Definition of done (per change)
- Typed request/response schemas, error handling, fail-safe path.
- `/healthz` still green; `python scripts/run_all_tests.py` passes in the touched service.
- No secrets in diff; `.env.example` still key-less.
- If it touches a prompt surface, the frozen test set still passes and the log is updated.

## Planned vs implemented (Stage A in progress)
- **Implemented:** signal validation, regex guardrail floor, EWMA floor, LangGraph topology, Tools API, n8n spine + CTX branches, FixtureLLM seam, integration stubs, TF-IDF retrieval.
- **Stubbed (fixture-backed):** PyTorch classifier, NeMo rails layer, llama.cpp GGUF generation.
- **Planned:** ≥55-doc corpus + seed_kb.py, Prompt Engineering Log, real LLM providers (Gemini/Bedrock/Ollama), pgvector ingestion, PyTorch training, AWS EC2 deployment.

## Language
Author switches Hebrew/English naturally; mirror whichever is used, keeping English technical terms inline in Hebrew. Prefer human-sounding, warm phrasing over formal/AI-sounding output.
