---
name: observability-incidents-domain
description: Use for any work touching alerts, incidents, logs, metrics, enrichment, classification, severity, or routing — the domain truth for PETER PAN.
---

# Observability & Incidents — Domain Truth

The single source of domain facts. If code, docs, or prompts contradict this
file, this file wins. If this file is missing a fact you need (e.g. the exact
6 class names), READ IT FROM `contracts.py` — never invent domain values.

## The core story (one line, use it in docs/demos)
> PITER connected Knowledge → RAG. PETER PAN connects Observability → Monitoring:
> alert in → enrich from logs/metrics → classify → guard → route → draw the problem.

## Incident model
- Classes: exactly 6, defined in `contracts.py` (`incident_class`). Read them
  from there. Never add a 7th, never collapse to fewer.
- Routing: 3-way category DERIVED from the 6 classes at n8n Node 8 (Router).
  The mapping table lives in the n8n flow — mirror it, don't fork it.
- Severity: P1–P4 only. Deterministic floors override LLM-stated severity
  ("LLM extracts; the service decides"). If retrieved context implies P1 but
  the LLM says P3, the floor wins and the discrepancy is flagged.

## Log & metric conventions (synthetic, demo-scale)
- All data is synthetic. Never real customer/production identifiers.
- Every synthetic log line carries: `timestamp` (ISO-8601 UTC), `service`,
  `level`, `message`, `correlation_id`. Enrichment joins on `correlation_id`.
- Metric names come only from `fixtures/dashboards/metrics_catalog.json`.
  Generating PromQL against uncatalogued metrics is a bug, not creativity.

## Enrichment pipeline (capability #1)
alert → RAG (similar past incidents + runbook snippets, top-3, cited) →
Predictor (`{incident_class, confidence}`) → merge into the incident brief.
- RAG output must cite which past incident it draws from. Uncited claims
  get stripped by the output guardrail.
- Predictor below confidence threshold → `uncertain` label → routed to the
  human-review branch, never silently forced into a class.

## What is OUT of scope (do not build, do not scaffold "for later")
- Redis / caching layers — not in the stack. Demo-scale doesn't need it.
- Feedback loop / retraining — ROADMAP slide only. No code, no queue tables.
- Live paging integrations (PagerDuty/Opsgenie), voice, bridge calls.
- Real Prometheus scraping of production targets — fixtures + demo Prometheus only.
