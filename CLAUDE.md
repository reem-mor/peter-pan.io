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
4. **Contracts are frozen.** Canonical schemas live in `docs/contracts/`; changing one requires an ADR. Never break a service contract silently.
5. **Synthetic data only.** No real PII, secrets, customer incidents. Ever. Not in code, fixtures, commits, or logs.
6. **Secrets via `.env` + Secrets Manager.** Never hardcode keys. Never commit `.env`. `.env.example` stays key-less.
7. **Be brief.** Short, direct answers. Concrete diffs over prose. Decide autonomously where context allows rather than asking.

## Karpathy-inspired coding behavior

These guidelines bias toward caution over speed. PETER PAN's safety floors, frozen
contracts, security rules, and required resilience paths always take precedence.

### 1. Think before coding
- Surface assumptions and trade-offs that materially affect the result.
- If uncertainty would change behavior or architecture, stop and ask. Proceed autonomously on reversible, well-specified work.
- If a simpler approach exists, say so and push back when warranted.

### 2. Simplicity first
- Write the minimum code that solves the requested problem; add nothing speculative.
- Avoid single-use abstractions and unrequested flexibility or configurability.
- Preserve required error handling, graceful degradation, health checks, and audit paths.

### 3. Surgical changes
- Every changed line must trace directly to the request.
- Match existing style; do not refactor, reformat, or remove unrelated code.
- Remove only imports, variables, or functions made obsolete by the current change.

### 4. Goal-driven execution
- Define verifiable success criteria before implementation and verify them before claiming completion.
- For fixes, reproduce the failure first; for refactors, verify behavior before and after.
- Never weaken tests, contracts, deterministic floors, or evaluation thresholds to make a change pass.

## Canonical project references
- Architecture, ownership, endpoints, and implementation status: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Build sequence and milestone gates: [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md)
- Frozen schemas: [docs/contracts/](docs/contracts/)
- Rubric and prompt-engineering requirements: [docs/PROJECT-PLAN.md](docs/PROJECT-PLAN.md)
- Agent tooling, MCP setup, and CI commands: [docs/AGENT-TOOLING.md](docs/AGENT-TOOLING.md)

## Verification and evidence

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

## n8n MCP safety (hard rules — violating these breaks production)
- **Never** call `test_workflow` on a live webhook/Telegram-triggered flow — it deregisters the production webhook.
- Use `update_workflow` with an `operations` array as the safe modification path.
- Credential bindings do **not** inherit — set explicitly via `setNodeCredential`.
- `create_workflow_from_code` cooks escape sequences in template literals — use `String.fromCharCode()` / `\uXXXX` for any Hebrew in Code nodes.
- Structured Output Parser nodes imported via JSON store `jsonSchemaExample` as a parsed object, not a string — fix with `setNodeParameter`.
- Perplexity node v2 needs an explicit `operation` discriminator alongside `resource: "search"`.
- Project-scope credential mismatch is the most common `publish_workflow` failure — check scope first.
- `get_execution` needs both `executionId` and `workflowId`; use `includeData: true` with filtered `nodeNames` to avoid response-size limits.

## Deployment safety (portfolio / demo)
- Canonical deployment constraints and procedures: [infra/aws/README.md](infra/aws/README.md).
- Restrict inbound access to n8n egress and the developer IP — **never `0.0.0.0/0`**.
- Containers run non-root. Secrets come from environment interpolation or Secrets Manager.
- There is no formal SLA; graceful degradation and recoverable restart are the failure model.
- The production deployment path remains planned, not implemented in Stage A.

## Declared deviations (state upfront, never hide)
1. AIOps domain instead of real estate.
2. Time-series metric windows instead of images for the classifier (vision fallback available).
3. Bedrock Claude alongside Gemini/GPT-4o; pgvector alongside ChromaDB — one-node swaps.

## Definition of done (per change)
- Typed request/response schemas, error handling, fail-safe path.
- `/healthz` still green; `python scripts/run_all_tests.py` passes in the touched service.
- No secrets in diff; `.env.example` still key-less.
- If it touches a prompt surface, the frozen test set still passes and the log is updated.

## Language
Author switches Hebrew/English naturally; mirror whichever is used, keeping English technical terms inline in Hebrew. Prefer human-sounding, warm phrasing over formal/AI-sounding output.
