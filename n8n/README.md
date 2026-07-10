# n8n — Layer 2 orchestration (the PETER flow)

`peter-flow.json` is the versioned export of the Stage A workflow. **Re-export it on every
flow change** (BUILD_PLAN §3) — the n8n instance is not the source of record, this repo is.

- Instance: `reemmor.app.n8n.cloud`, personal project, workflow **`lSa7mPQX0rbUi1K5`**
  ("PETER PAN — PETER Flow (Stage A)"), unpublished until Stage A services exist.
- Webhook ingress: `POST /webhook/peter-signal` (test: `/webhook-test/peter-signal`),
  body = a `Signal` (see `docs/contracts/contracts.py`).
- Two predecessor workflows named "PETER PAN Incident Submission Pipeline"
  (`QLOj0j7hiEuyP28t` — a mistitled property-listing template; `TALJtWbkoHtjzbKL` — the
  first PETER draft, superseded by this flow) are **archived** in n8n, restorable from the
  instance archive.

## Configuration (never inline in the flow)

Environment variables, set in the n8n instance:

| var | meaning (Stage A value) |
|---|---|
| `PETER_GUARDRAILS_URL` | Guardrails service base URL (`/check/input`, `/check/output`) |
| `PETER_PREDICTOR_URL` | Predictive Engine base URL (`/analyse`) |
| `PETER_RAG_URL` | RAG service base URL (`/query`) |
| `PETER_LANGGRAPH_URL` | LangGraph agent base URL (`/agent/run`) |
| `PETER_TOOLS_URL` | Tools API base URL (`/escalations`, preview-first) |
| `PETER_REVIEW_QUEUE_URL` | human-review queue stub endpoint |
| `PETER_DB_TEAM_WEBHOOK` / `PETER_INFRA_TEAM_WEBHOOK` / `PETER_APP_TEAM_WEBHOOK` / `PETER_TRIAGE_TEAM_WEBHOOK` | team webhooks (Stage A: webhook.site/stub URLs) |
| `PETER_SLACK_STUB_URL` | Slack incident-channel stub (Stage C: real Slack) |
| `PETER_GITHUB_API` / `PETER_GITHUB_REPO` | GitHub deployments context branch (real API, fake repo) |

Credentials, created in the n8n UI (the export carries **no** secrets):

- **PETER Services Bearer** (`httpBearerAuth`) — shared secret for all service HTTP calls.
- **PETER Mock LLM (OpenAI-compatible)** (`openAiApi`) — base URL pointing at the Stage A
  FixtureLLM service. ⚠️ On creation n8n auto-assigned the real "OpenAi n8n course"
  credential to the three "(Mock Seam)" model nodes — **swap it to the mock credential
  before running anything**. Stage C swaps this same credential to real providers
  (Gemini 2.5 Flash for extraction, Bedrock Claude Sonnet for agent/synthesis —
  [ADR 0002](../docs/adr/0002-model-memory-db.md)); the nodes never change.

## Flow ↔ diagram mapping

Diagram nodes 1–8 (`docs/peter-pan-n8n-flow.mmd`) → Signal Webhook + Normalize Signal (1),
Guardrails Input Check + IF (2–3), Maintenance/Deploys/Complaints → Merge Context →
Build IncidentContext + Known Noise? gate (CTX/IFS — suppression is deterministic code),
Extract Incident Info (4), Incident Commander with Predictor/RAG/LangGraph HTTP tools (5,
per the diagram's AGT→T1/T2/T3 edges — resolves BUILD_PLAN conflict 6), Write TriageReport
with the frozen contract JSON Schema (6), Guardrails Output Check + IF → review queue (7),
Route by Category (contract enum + `unroutable` fallback) + P1-only preview-first
escalation + Slack stub (8). `Finalize TriageReport` enforces the deterministic floors
(incident_id, generated_at, model_meta, clamps) in code after the parser.
