# Layer 2 Validation Report — PETER PAN

**Date:** 2026-07-16  
**Scope:** n8n orchestration + connected Layer 3 services  
**Demo host:** EC2 on-instance compose (`n8n` + FastAPI services)  
**Authoring host:** n8n Cloud MCP (inactive draft — not the demo path)

---

## 1. Executive summary

Layer 2 (the PETER Observability Triage flow) is structurally correct and
demo-ready on the **EC2 on-instance n8n** path when signals use catalog
services and valid `sig-*` IDs. End-to-end runs produce grounded
`TriageReport` JSON with citations, deterministic 6→3 routing, and
guardrail rejection of destructive requests.

Cloud MCP is useful for authoring/inspection but is **not** the production
demo ingress (inactive webhook; header-auth credential name field still
misconfigured as the account display name).

**Final status:**

```text
READY WITH DOCUMENTED LIMITATIONS
```

---

## 2. Architecture discovered

```text
Input (Signal POST /webhook/peter-signal + X-Peter-Webhook-Secret)
  -> Normalize Signal
  -> Guardrails /check/input  {passed,flags,reason}
  -> IF passed?  (fail -> Reject / 503)
  -> Context enrichment (maintenance stub | GitHub deploys | complaints stub)
  -> Known-noise suppress (deterministic)
  -> Extract Incident Info (Fixture LLM seam)
  -> Assemble Incident
  -> Incident Commander tools:
       Predictor /analyse -> RAG /query | Service Context | LangGraph /agent/run
  -> Apply Predictor Policy (6->3 + P1-P4 floors in Code)
  -> Write TriageReport (+ structured parser) | Fixture fallback
  -> Finalize TriageReport (deterministic clamps)
  -> Guardrails /check/output
  -> Route by category -> team webhooks (+ P1 preview escalation + Slack stub)
  -> Respond TriageReport | flagged_for_review | suppressed
```

Optional / adjacent (not on the webhook critical path):

- Dashboard Generator `POST /dashboard` (fixture scenarios → Grafana)
- Image Analyzer (vision fallback; not required by Stage A spine)
- Ingestion service (alert fan-in)

Sources of truth: `docs/peter-pan-n8n-flow.mmd`, `n8n/peter-flow.json`,
`docs/contracts/contracts.py`.

---

## 3. Workflows reviewed

| Item | Result |
|------|--------|
| Name | `PETER PAN — Observability Triage` |
| Export | `n8n/peter-flow.json` |
| Cloud ID | inactive draft (authoring only; ID not tracked) |
| EC2 | Active webhook on `:5678` |
| Trigger | POST `peter-signal`, `responseMode=responseNode` |
| Guardrail order | Input before enrichment; output before route |
| IF contract | `$json.passed` boolean |
| Tool types | `n8n-nodes-base.httpRequestTool` |
| Static tests | **183 passed** (`n8n/tests`) |
| Duplicates | One archived duplicate on EC2 (already archived) |

---

## 4. Services reviewed

| Service | Port | Public health | On-box | Role in L2 |
|---------|------|---------------|--------|------------|
| ingestion | 8001 | OK | OK | Alert ingress (support) |
| predictor | 8002 | OK | OK | Node 5 tool |
| rag | 8003 | loopback only | OK | Node 5 tool |
| guardrails | 8004 | OK | OK | Nodes 2 + 7 |
| tools-api | 8005 | OK | OK | service_context + escalations |
| langgraph-agent | 8006 | OK | OK | Complex cross-domain tool |
| image-analyzer | 8007 | OK | OK | Optional vision fallback |
| dashboard-generator | 8008 | OK | OK | Grafana fixture POST |
| fixture-llm | 8010 | loopback | OK | Mock LLM seam |
| integration-stubs | 8020 | OK | OK | Team/review/slack stubs |
| grafana | 3000 | OK | OK | Dashboard target |
| n8n | 5678 | OK | OK | Layer 2 conductor |

---

## 5. System prompts

Versioned under `docs/prompt-log/prompts/`:

| Surface | File | Status |
|---------|------|--------|
| #1 Extractor | `surface-1-extractor.systemprompt.txt` | Aligned with Extract node |
| #2 Commander | `surface-2-agent.systemmessage.txt` | Aligned; tool-order rules explicit |
| #3 RAG | `surface-3-rag.systemprompt.txt` | Service-owned |
| #4 Output auditor | `surface-4-output-auditor.txt` | Guardrails floor + LLM assist |

Writer prompt lives in `Write TriageReport` messages; harden script now patches
that path (not only legacy `options.systemMessage`).

No prompt rewrite required for Stage A demo correctness. Soft prompt-injection
phrases without destructive keywords are intentionally **not** blocked (regex
floor is keyword-based; see limitations).

---

## 6. Layer 2 issues found

| Sev | Issue | Fix status |
|-----|-------|------------|
| Crit | Harden script hardcoded stale Cloud WF ID + host | **Fixed** — env `N8N_API_URL` / `N8N_WORKFLOW_ID` |
| Crit | Cloud webhook header auth displays as account name | **Documented** — fix credential header-name in Cloud UI to `X-Peter-Webhook-Secret` |
| High | Bootstrap `WORKFLOW_NAME` mismatch | **Fixed** |
| High | Writer harden path wrong | **Fixed** |
| Med | LangGraph tool missing retries | **Fixed** (export + Cloud) |
| Med | `api-gateway` not in tools catalog → `owner_unverified` | **Documented** — use catalog services |
| Med | Signal ID regex rejects short ids | **Documented** in `n8n/README.md` |
| Med | Grafana 412 without `overwrite:true` | **Documented** — use overwrite on re-POST |
| Low | Skill pointed at `flow-export.json` / wrong respond mode | **Fixed** |
| Low | `docker-compose.ec2.yml` published RAG publicly | **Fixed** — loopback only |

---

## 7. Layer 1 / Layer 3 changes

| Change | Why |
|--------|-----|
| `scripts/test_ec2_public_health.py` SSH-checks RAG | RAG is loopback-only; public refuse is not a failure |
| `docker-compose.ec2.yml` RAG → `127.0.0.1:8003` | Match secure runtime + local compose |
| No Streamlit/UI code changes | L2 path validated via webhook |

---

## 8. Files changed

- `scripts/harden_stage_a_n8n.py` — env-driven, writer messages path, LangGraph retries, scrub webhookId
- `scripts/bootstrap_n8n_local.py` — workflow name alignment
- `scripts/test_ec2_public_health.py` — loopback RAG/fixture-llm
- `n8n/peter-flow.json` — LangGraph retries + sticky credential note
- `docker-compose.ec2.yml` — RAG loopback
- `docs/n8n-workflow.md` — name
- `n8n/README.md` — webhook header + signal id
- `.cursor/skills/n8n-flow-conventions/SKILL.md` — export path + responseMode
- `docs/LAYER-2-VALIDATION.md` — this report
- Operator probes: `scripts/_ec2_layer2_*.sh` (temporary; safe to delete after use)

Cloud MCP updates (not in git): credential binds, LangGraph retries, sticky note.

---

## 9. Tests executed

| Suite | Result |
|-------|--------|
| `n8n/tests` | **183 passed** |
| `services/guardrails/tests` | passed (≈97% cov) |
| `services/langgraph-agent/tests` | passed (≈98% cov) |
| `services/predictor/tests --no-cov` | passed |
| `services/rag/tests` | passed (see run log) |
| `services/dashboard-generator/tests` | passed |
| `services/image-analyzer/tests` | passed |
| EC2 public health script | all green (incl. SSH RAG) |

---

## 10. API test results (sanitized)

| Case | Result |
|------|--------|
| Healthz all core services | 200 |
| `POST /tools/service_context` orders-api | owner `App Platform` |
| `POST /analyse` spike window | `error_rate_spike` sev 5 |
| `POST /query` weak query | `refused=true`, insufficient data |
| `POST /check/input` DROP TABLE | `passed=false`, `destructive_data_action` |
| Webhook no secret | 403 |
| Webhook empty `{}` | rejected `schema_invalid` |
| Webhook DROP TABLE | rejected `destructive_data_action` |
| Webhook orders-api valid | **200 TriageReport** application / P1 / App Platform / 3 cites |
| Webhook postgres-primary valid | **200 TriageReport** database / P1 / Database Reliability / 3 cites |
| `POST /dashboard` overwrite | uid `pp-orders-api-errors`, **3 panels** |

---

## 11. Playwright results

No Playwright UI suite exists for the Streamlit WebUI (`ui/app.py`). Stage A
validation used webhook + service probes instead. Adding Playwright is optional
polish; not blocking Layer 2 orchestration correctness.

---

## 12. EC2 service results

- Compose stack healthy; n8n on-instance with full `PETER_*` env set.
- RAG + fixture-llm bound to loopback (n8n uses compose DNS).
- Webhook auth enforced (`X-Peter-Webhook-Secret`).

---

## 13. Guardrail results

- Destructive keywords blocked at input and via webhook (verified).
- Soft “ignore previous instructions” without destructive keywords: **passes**
  (by design of regex floor — documented limitation).
- Output path flags invented owners (`owner_unverified`) when Tools catalog miss.

---

## 14. RAG evaluation results

- Live query returns cited runbook evidence (`citations` ≥ 1 on known topics).
- No-evidence query: `refused=true`, answer `insufficient data`.
- Frozen cases: `evaluation/rag_evaluation_cases.json` (custom eval, not RAGAS).

---

## 15. Predictor decision

**KEEP.** Six-class `incident_class` + EWMA floor + PyTorch classifier path.
Adds deterministic routing floor for Node 8. Verified live on EC2.

---

## 16. Image Analyzer decision

**KEEP AS OPTIONAL FALLBACK.** Not on Stage A webhook spine. Health OK.
Vision is the course crosswalk optional; do not wire into critical path unless
demo explicitly needs screenshots.

---

## 17. LangGraph / LangChain decision

**KEEP LangGraph service** (`plan → specialists → synthesise`) for complex
cross-domain incidents. n8n Commander owns Predictor + single-domain RAG/Tools;
LangGraph owns deep multi-step when invoked. Do not add a second LangChain
orchestration service.

---

## 18. PyTorch decision

```text
PYTORCH REQUIRED
```

Reason: `services/predictor/predictor_service/torch_classifier.py` and
`train.py` load/run a 1D-CNN checkpoint (`predictor.pth`) at inference/training.
RAG may pull torch via sentence-transformers/chroma on EC2 Chroma path; the
hard requirement is the Predictor classifier.

---

## 19–20. RAGAS / Langfuse decision

```text
USE CUSTOM EVALUATION ONLY
```

```text
NO ADDITIONAL EVALUATION PLATFORM REQUIRED
```

Reason: repo already has `evaluation/rag_evaluation_cases.json`,
`evaluation/run_e2e.py`, LangGraph benchmark queries, and n8n static/prompt
surface tests. RAGAS/Langfuse add deploy + credential overhead without Stage A
demo value.

---

## 21. Security findings

| Finding | Severity | Action |
|---------|----------|--------|
| Cloud Header Auth credential header-name wrong | High (Cloud only) | Operator: set header name to `X-Peter-Webhook-Secret` in Cloud UI |
| EC2 webhook auth OK | — | None |
| No secrets committed in export | — | Keep scrub on export |
| Harden script no longer embeds Cloud hostname | — | Fixed |
| Soft prompt-injection may pass | Med | Accept Stage A floor; harden keywords if course requires |

---

## 22. Remaining limitations

1. Writer often uses **fixture-fallback** provider (parser seam) — still contract-valid.
2. Cloud n8n is authoring-only until header credential + service URL env are fixed.
3. Services outside Tools catalog (e.g. `api-gateway`) route to review / unknown owner.
4. No Playwright UI automation yet.
5. No dedicated n8n `errorWorkflow` (failures rely on per-node `onError`).
6. Dashboard re-POST needs `overwrite:true` after first publish.

---

## 23. Exact demo procedure

```powershell
# 1) Health (from laptop)
.\.venv\Scripts\python.exe scripts\test_ec2_public_health.py <EC2_PUBLIC_IP>

# 2) On EC2 (SSH), run a golden signal — use a catalog service + long sig id:
#    orders-api | postgres-primary | shop-web | payments-api | redis-cache | k8s-ingress
curl -sS -X POST http://127.0.0.1:5678/webhook/peter-signal `
  -H "Content-Type: application/json" `
  -H "X-Peter-Webhook-Secret: $env:PETER_WEBHOOK_SECRET" `
  -d '@evaluation/golden_signals.json'  # or a single Signal object

# 3) Expect HTTP 200 TriageReport at root with category, p_level, owner_team, citations[]

# 4) Destructive demo
# body containing DROP TABLE -> status=rejected, flags=[destructive_data_action]

# 5) Dashboard
curl -sS -X POST http://127.0.0.1:8008/dashboard `
  -H "Authorization: Bearer $env:PETER_SERVICES_TOKEN" `
  -H "Content-Type: application/json" `
  -d '{"scenario":"orders-api-error-spike","incident_id":"inc-demo","overwrite":true}'
```

Local alternative:

```powershell
docker compose --profile bootstrap up --build
python scripts/bootstrap_n8n_local.py
python evaluation/run_e2e.py --entrypoint n8n --base-url http://localhost
```

---

## 24. Final status

```text
READY WITH DOCUMENTED LIMITATIONS
```

Primary demo path (EC2 on-instance n8n → services → TriageReport) validated for
valid production incidents, schema rejection, destructive blocking, RAG
no-evidence refusal, and Grafana dashboard overwrite publish.
