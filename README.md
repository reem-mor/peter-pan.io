<div align="center">

# PETER PAN

### Predictive, guarded, agentic incident response — n8n-orchestrated microservices

</div>

> **Status: architecture-first reset in progress.** This repo was reset from the legacy
> PITER AiOps project on 2026-07-08; see
> [ADR 0001 — PITER carryover](docs/adr/0001-piter-carryover.md) for what was kept,
> migrated, and deleted. `docs/BUILD_PLAN.md` (contracts, component inventory, staged
> build order) is pending — Phase 2.

## Canonical architecture

The two Mermaid diagrams are the source of truth — everything in this repo must align with them:

- [System architecture](docs/peter-pan-system.mmd) — demo environment (k3d + OTel + Grafana),
  PETER PAN core on EC2 (Ingestion, Predictive Engine, RAG, Guardrails, LangGraph agent,
  Tools API), n8n orchestration, task-routed AI models (Bedrock / llama.cpp / Ollama),
  knowledge & comms integrations.
- [n8n flow](docs/peter-pan-n8n-flow.mmd) — webhook → input guardrails → context enrichment →
  extraction → incident-commander agent → TriageReport → output guardrails → routing.

## Layout

| path | contents |
|---|---|
| `services/` | one dir per microservice (tools-api, guardrails, rag populated from PITER carryover; ingestion, predictor, langgraph-agent scaffolded) |
| `agents/` | LangGraph supervisor + specialists (Stage A) |
| `predictive/` | anomaly detection + training; `datagen/` fixtures |
| `n8n/` | exported flow JSONs, versioned on every change (Stage A) |
| `evaluation/` | golden-set seeds + eval harness |
| `docs/` | architecture diagrams, ADRs, BUILD_PLAN.md (pending) |
| `frontend/` | parked PITER React SPA — bonus dashboard, excluded from the build plan |

> Migrated code is not yet importable (old `app.*` paths) — re-packaging is Stage A work,
> and CI is intentionally lint-only until then.
