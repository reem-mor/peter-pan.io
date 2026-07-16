# Layer 2 — Orchestration (n8n · the PETER flow)

Architecture context: [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §4.

`peter-flow.json` is the versioned export of the Stage A workflow. **Re-export it on every
flow change** (BUILD_PLAN §3) — the n8n instance is not the source of record, this repo is.

- The tracked export contains no instance URL, workflow ID, or live credential binding.
- **Local compose** pins `n8nio/n8n:2.29.10`; upgrade only with flow/static/E2E revalidation.
  Tool nodes in `peter-flow.json` use `n8n-nodes-base.httpRequestTool` — not the deprecated
  `@n8n/n8n-nodes-langchain.httpRequestTool` type from early exports.
- Webhook ingress: `POST /webhook/peter-signal` (test: `/webhook-test/peter-signal`),
  body = a `Signal` (see `docs/contracts/contracts.py`).

## Local compose bootstrap

The one-shot `n8n-bootstrap` service is isolated behind the explicit `bootstrap`
profile. It uses authenticated n8n REST endpoints and does not mount the Docker socket:

```powershell
docker compose --profile bootstrap up --build
```

The bootstrap service:

1. Waits for n8n `/healthz`
2. Creates owner session (or uses `N8N_OWNER_*` from compose)
3. Creates **PETER Services Bearer** and **PETER Mock LLM** credentials
4. Imports `peter-flow.json` and activates `POST /webhook/peter-signal`

Alternatively, re-run the host-side script after a fresh n8n volume:

```powershell
python scripts/bootstrap_n8n_local.py
```

## Configuration (never inline in the flow)

Environment variables, set in the n8n instance:

| var | meaning (Stage A value) |
|---|---|
| `PETER_GUARDRAILS_URL` | Guardrails service base URL (`/check/input`, `/check/output`) |
| `PETER_PREDICTOR_URL` | Predictive Engine base URL (`/analyse`) |
| `PETER_RAG_URL` | RAG service base URL (`/query`) |
| `PETER_LANGGRAPH_URL` | LangGraph agent base URL (`/agent/run`) |
| `PETER_TOOLS_URL` | Tools API base URL (`/escalations`, preview-first) |
| `PETER_REVIEW_QUEUE_URL` | human-review receiver in `integration-stubs` |
| `PETER_DB_TEAM_WEBHOOK` / `PETER_INFRA_TEAM_WEBHOOK` / `PETER_APP_TEAM_WEBHOOK` / `PETER_TRIAGE_TEAM_WEBHOOK` | team webhooks (Stage A: webhook.site/stub URLs) |
| `PETER_SLACK_STUB_URL` | Slack incident-channel stub (Stage C: real Slack) |
| `PETER_GITHUB_API` / `PETER_GITHUB_REPO` | Deploy context stub (`integration-stubs` in local compose) |

Credentials, created in the n8n UI (the export carries **no** secrets). Local compose
creates them via `scripts/bootstrap_n8n_local.py` from `${PETER_SERVICES_TOKEN}`,
`${PETER_WEBHOOK_SECRET}`, and `${PETER_FIXTURE_LLM_URL}` — see
`n8n/bootstrap-credentials.example.json` for shape only.

- **PETER Services Bearer** (`httpBearerAuth`) — shared secret for all service HTTP calls.
- **PETER Mock LLM (OpenAI-compatible)** (`openAiApi`) — base URL pointing at the Stage A
  FixtureLLM service. Verify that every "(Mock Seam)" model node uses this fixture credential
  before running the flow. Stage C swaps this same credential to real providers
  (Gemini 2.5 Flash for extraction, Bedrock Claude Sonnet for agent/synthesis —
  [ADR 0002](../docs/adr/0002-model-memory-db.md)); the nodes never change.
- **PETER Webhook Header** (`httpHeaderAuth`) — header **name** must be exactly
  `X-Peter-Webhook-Secret` (the credential's header-name field, not the n8n account display
  name). Value = `${PETER_WEBHOOK_SECRET}`.

Signal `id` must match `^sig-[a-z0-9-]{8,}$` (at least 8 chars after `sig-`). Shorter ids
are rejected by input guardrails as `schema_invalid` before any LLM call.

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
