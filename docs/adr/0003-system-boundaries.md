# ADR 0003 — System boundaries and service inventory

- **Status:** accepted (2026-07-10)
- **Context:** PETER PAN delivers the graded four-layer incident-ops architecture. The repository ships six FastAPI deployment units; two are supporting infrastructure, not additional graded capabilities.

## Decision

### Four graded primary services (Layer 3 core)

| Service | Graded role | Interface |
|---|---|---|
| RAG | Cited knowledge retrieval | `POST /query` |
| Predictor | Metric-window classification | `POST /analyse` |
| Guardrails | Input/output safety rails | `POST /check/input`, `/check/output` |
| LangGraph agent | Deep multi-domain reasoning | `POST /agent/run` |

### Supporting infrastructure (not a fifth/fourth graded deviation)

| Service | Role |
|---|---|
| Ingestion | Signal validation and n8n forwarding |
| Tools API | Owners, deploys, similar incidents, preview escalation, audit |

This is the **fourth declared deviation** from the guideline's literal four-service count: same capabilities, refined into ingress and governance seams.

### Orchestration rule

n8n is the sole workflow orchestrator. Canonical path: `Signal → Ingestion → n8n → tools`. Predictor is invoked once as a commander HTTP tool, not as a parallel ingress path.

### RAG invocation rule

When the LangGraph agent is active, RAG calls are owned by LangGraph. The n8n commander must not duplicate RAG retrieval in the same incident; use idempotent request keys or skip direct RAG when LangGraph is selected.

## Consequences

- Diagrams document Ingestion and Tools API as supporting nodes, not graded replacements.
- Public AWS demo exposes HTTPS ingress only; service ports 8001–8006 remain private.
- Frozen Tools API seed schemas define required fields and value types. Pydantic may
  provide empty-string defaults for optional fields; those defaults are implementation
  metadata and do not change the accepted wire shape.
