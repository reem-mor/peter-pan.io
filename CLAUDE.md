# CLAUDE.md — PETER PAN

Working memory for Claude Code on this repo. Read before acting.

## What this is
PETER PAN — a self-hostable, guarded, agentic incident-response platform (AIOps triage).
Built as a 1:1 crosswalk of the AI Property Triage final-project guideline into the incident-ops domain: same graded capabilities, same rubric lines, AIOps instead of real estate.

PETER = Priority · Enrichment · Triage · Escalation · Resolution
PAN = the Panoramic view of your incidents (PITER connected Knowledge → RAG; PETER PAN connects Observability → Monitoring)

## Golden rules (apply to every task)
1. **Audit before action.** Read the relevant code/config and state a plan before editing. No edits on assumption.
2. **Phased execution with approval gates.** Break work into phases; pause for explicit approval before any destructive or consequential step (deletes, migrations, deploys, force-push, `docker compose down -v`, dropping data).
3. **Deterministic floors override the LLM.** The regex guardrail floor and the EWMA/z-score predictor floor have final say. Never let a change route around them.
4. **Contracts are frozen.** Canonical schemas live in `docs/contracts/`; changing one requires an ADR. Never break a service contract silently.
5. **Synthetic data only.** No real PII, secrets, customer incidents. Ever. Not in code, fixtures, commits, or logs.
6. **Secrets via `.env` + Secrets Manager.** Never hardcode keys. Never commit `.env`. `.env.example` stays key-less.
7. **Branch flow only.** Feature branch → PR → merge on green CI. Never merge locally to main.
8. **Be brief.** Short, direct answers. Concrete diffs over prose. Decide autonomously where context allows rather than asking.

## Locked decisions & scope
- Guardrail schema: `{passed, flags, reason}` (documented deviation from the course's `{pass, reason, safe_text}`).
- Predictor: 6 classes, field `incident_class`; the 6→3 routing mapping lives only in the n8n Router. Severity P1–P4 only — no P5.
- Fixture-first: the demo path never depends on a live LLM or external API.
- Python 3.12 is the target (venv + CI).
- **Out of scope — do not scaffold, even "for later":** Redis/caching, feedback-loop code (roadmap slide only), voice/bridge/live-call integration, PagerDuty/Opsgenie, Kubernetes, Terraform.

## Skills (canonical root: `.claude/skills/` — see `docs/AGENT-TOOLING.md`)
| Area | Skill |
|---|---|
| Classification, severity, routing, TriageReport, Predictor ML | `.claude/skills/incident-triage/` |
| Guardrails rails, regex floor, GuardrailResult | `.claude/skills/guardrails-testing/` |
| RAG grounding, citations, embeddings, Chroma/GGUF | `.claude/skills/rag-evaluation/` |
| Prompt Engineering Log (25% deliverable) | `.claude/skills/prompt-engineering-log/` |
| Frozen eval / Stage A gates / demo freeze | `.claude/skills/peter-evaluation/` |
| Streamlit UI + Grafana dashboard JSON | `.claude/skills/frontend-design/` |
| MCP servers + n8n flow conventions | `.claude/skills/mcp-integration/` |
| EC2 / CloudFormation / deploy | `.claude/skills/ec2-deploy/` |
| Knowledge graph navigation | `.claude/skills/graphify/` |
| FastAPI layout / caveman communication ladder | `docs/AGENT-TOOLING.md` (no separate skill) |

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
- Product story (PITER → PETER PAN, market): [docs/PRODUCT-STORY.md](docs/PRODUCT-STORY.md)
- Architecture (four layers): [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Build sequence and milestone gates: [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md)
- Frozen schemas: [docs/contracts/](docs/contracts/)
- Rubric and prompt-engineering requirements: [docs/PROJECT-PLAN.md](docs/PROJECT-PLAN.md)
- Course-spec crosswalk and deviations register: [docs/PETER-PAN-SPEC-CROSSWALK.md](docs/PETER-PAN-SPEC-CROSSWALK.md)
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

## n8n MCP (cloud account — full control when connected)
Create, update, publish, unpublish, execute, and pin-data test are all allowed on the
connected n8n Cloud account when the user has enabled the n8n MCP server.

- Prefer `execute_workflow` with `executionMode: "manual"` to exercise draft/node logic.
- Prefer `execute_workflow` with `executionMode: "production"` after `publish_workflow`.
- Prefer `test_workflow` + `prepare_test_pin_data` for isolated node/path tests that should
  not hit live credentials/HTTP.
- **Webhook caveat:** `test_workflow` on an *active* webhook/Telegram-triggered flow can
  deregister the production webhook. For those flows: unpublish → test → republish, or use
  `execute_workflow` (`manual`/`production`) instead. Do not refuse a user-requested test —
  use the safer path first and state which path you took.
- Use `update_workflow` with an `operations` array as the safe modification path.
- Credential bindings do **not** inherit — set explicitly via `setNodeCredential`.
- `create_workflow_from_code` cooks escape sequences in template literals — use `String.fromCharCode()` / `\uXXXX` for any Hebrew in Code nodes.
- Structured Output Parser nodes imported via JSON store `jsonSchemaExample` as a parsed object, not a string — fix with `setNodeParameter`.
- Perplexity node v2 needs an explicit `operation` discriminator alongside `resource: "search"`.
- Project-scope credential mismatch is the most common `publish_workflow` failure — check scope first.
- `get_execution` needs both `executionId` and `workflowId`; use `includeData: true` with filtered `nodeNames` to avoid response-size limits.
- If the n8n MCP server status is `error` / tools unavailable, call `mcp_auth` then retry.

## Deployment safety (portfolio / demo)
- Canonical deployment constraints and procedures: [infra/aws/README.md](infra/aws/README.md).
- Restrict inbound access to n8n egress and the developer IP — **never `0.0.0.0/0`**.
- Containers run non-root. Secrets come from environment interpolation or Secrets Manager.
- There is no formal SLA; graceful degradation and recoverable restart are the failure model.
- The production deployment path remains planned, not implemented in Stage A.

## Declared deviations (state upfront, never hide)
1. AIOps domain instead of real estate.
2. Time-series metric windows instead of images for the classifier (vision fallback implemented: `services/image-analyzer`).
3. Guardrail schema `{passed, flags, reason}` instead of `{pass, reason, safe_text}`.
4. Bedrock Claude alongside Gemini/GPT-4o; pgvector alongside ChromaDB — one-node swaps.
Full register: docs/PETER-PAN-SPEC-CROSSWALK.md.

## Definition of done (per change)
- Typed request/response schemas, error handling, fail-safe path.
- `/healthz` still green; `python scripts/run_all_tests.py` passes in the touched service.
- No secrets in diff; `.env.example` still key-less.
- If it touches a prompt surface, the frozen test set still passes and the log is updated.

## Language
Author switches Hebrew/English naturally; mirror whichever is used, keeping English technical terms inline in Hebrew. Prefer human-sounding, warm phrasing over formal/AI-sounding output.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
