---
name: incident-triage
description: Use when working on PETER PAN's incident classification, severity mapping, team routing, or TriageReport generation — anything touching how a signal becomes a categorized, severity-scored, routed report. Covers the 6-class predictor incident_class, its deterministic map to the 3-way routing category, the severity 1–5 → P1–P4 mapping, and the frozen TriageReport contract. Trigger when editing the Predictor, the router node, the LLM-chain that builds TriageReport, or any test asserting on class/severity/owner/routing.
---

# Incident Triage

How PETER PAN turns a raw signal into a categorized, severity-scored, routed `TriageReport`.
The rules here are **domain law** — the LLM proposes, deterministic policy decides.

## Two different taxonomies — do not conflate
This is the #1 source of confusion. There are TWO classification fields:

| Field | Where | Values | Purpose |
|---|---|---|---|
| `incident_class` | Predictor `/analyse` output | **6 classes** (below) | Fine-grained incident *type* from the metric window |
| `category` | `TriageReport` (frozen contract) | **3 classes**: `infra` · `database` · `application` | Coarse *routing* bucket for n8n node 8 |

`incident_class` (6) maps **deterministically** to `category` (3). The predictor emits the fine
class; deterministic code derives the routing category. Never let an LLM pick the routing category
directly.

## The 6 predictor classes (fixed set — never invent new ones)
| `incident_class` | Signature | -> routing `category` |
|---|---|---|
| `cpu_saturation` | Sustained high CPU, run-queue growth | `infra` |
| `memory_leak` | Monotonic memory climb, no GC recovery | `infra` |
| `db_lock_contention` | Lock waits, blocked sessions, query queueing | `database` |
| `replication_lag` | Replica delay growing vs primary | `database` |
| `error_rate_spike` | 5xx / exception rate above baseline | `application` |
| `normal` | Within EWMA/z-score band — no incident | (suppressed — no route) |

If a model output names any class outside this set, that is a **contract violation** — the
deterministic layer rejects it and falls back to `normal` + low confidence.

## Severity -> P-level (deterministic, not LLM-decided)
Severity is 1–5 from the Predictor's second head, mapped to `p_level`
(`Literal["P1","P2","P3","P4"]` — **there is no P5**):

| Severity (1–5) | `p_level` | Meaning |
|---|---|---|
| 5 | P1 | Customer-facing outage / data risk |
| 4 | P2 | Major degradation, no full outage |
| 3 | P3 | Contained, elevated risk |
| 2 | P4 | Minor / single-component |
| 1 | P4 | Informational |

**Hard rule:** the extractor prompt must *never infer severity* — severity comes from the
Predictor + deterministic policy only. An LLM-stated severity is advisory context, never the
value written to the report.

## Routing (deterministic map, node 8)
`category` + `p_level` -> owning team, with escalation fallback:
- `infra` -> **Infra team**
- `database` -> **DB team**
- `application` -> **App team**
- `p_level == P1` -> **preview-first escalation dispatch** (in addition to the team route)
- Unresolved / low-confidence / conflicting -> **escalation fallback** (never silently drop)

Routing is a lookup, not a generation. Never let the agent free-text a team name.

## TriageReport contract (FROZEN — matches docs/contracts/contracts.py)
Key fields (see the canonical model for the full shape):
- `category: Literal["infra","database","application"]` — the routing bucket, verified.
- `p_level: Literal["P1","P2","P3","P4"]` — deterministic from severity.
- `owner_team`, `escalation_path` — **copied only from Tools API responses**, never invented
  (output guardrail verifies against Tools API ground truth).
- `citations: list[Citation]` — **min_length=1**; an uncited report fails the output guardrail.
- `recommended_steps` — read-only/safe steps only; no destructive verbs (output rail enforces).
- `guardrail_flags` — non-empty -> human review queue.

The shape is frozen in `docs/contracts/contracts.py`. Changing it requires an ADR and breaks the
n8n Structured Output Parser + the E2E golden tests.

## Where the agent's tools live (node 5, per the flow diagram)
n8n node 5 (the incident commander) calls **four** tools: RAG (`/query`), Predictor (`/analyse`),
LangGraph (`/agent/run`), and Tools API (`/tools/service_context`). The **LangGraph** service
itself calls **RAG + Tools API** as its specialists (NOT the Predictor — n8n owns the Predictor
call). When LangGraph is active for an incident, it owns the RAG call; the n8n commander must not
duplicate RAG retrieval in the same incident (use idempotent keys or skip direct RAG).

## Idempotency
Duplicate signals (same signature within a window) must not dispatch twice. Dedup on signal key
before routing. P1 escalation must be idempotent — re-processing one P1 produces one dispatch.

## Domain truth (migrated from observability-incidents-domain)

- Synthetic data only. Log lines carry `timestamp`, `service`, `level`, `message`,
  `correlation_id`. Metric names come only from `fixtures/dashboards/metrics_catalog.json`.
- Enrichment: alert → RAG (cited) → Predictor `{incident_class, confidence}` → brief.
  Below-threshold confidence → `uncertain` → human-review branch, never forced class.
- Out of scope (do not scaffold): Redis/caching, feedback-loop retrain code, PagerDuty/
  Opsgenie, voice/bridge, real production Prometheus scrape targets.

## Predictor ML rules (migrated from pytorch-predictor)

- 6 output classes from `contracts.py` only; transfer-learning backbone + fine-tuned head.
- Softmax max below named threshold → `uncertain`, never a forced class.
- Training: seeded script, stratified split, `metrics.json` with real test accuracy
  (target >75%), per-class precision/recall. Report honest accuracy; note if synthetic
  data makes the task trivially easy.
- Serve: load once at startup, `eval` + `torch.no_grad()`, CPU-fine on t3.large.

## When editing here
- Changing class/severity/routing logic -> edit the deterministic policy module, not a prompt.
- Touching `TriageReport` shape -> STOP; it's frozen. Confirm with the human first.
- Any change -> incident-triage unit tests (6->3 class map, severity->P-level, routing table,
  dedup, P1 idempotency) must stay green.
