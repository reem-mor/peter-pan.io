# API Reference — PETER PAN

All services expose `GET /healthz`. Authenticated endpoints require:

```
Authorization: Bearer <PETER_SERVICES_TOKEN>
```

Frozen contracts: [`docs/contracts/contracts.py`](contracts/contracts.py)

## Port map (local compose)

| Service | Port | Package |
|---------|------|---------|
| Ingestion | 8001 | `ingestion_service` |
| Predictor | 8002 | `predictor_service` |
| RAG | 8003 | `rag_service` |
| Guardrails | 8004 | `guardrails_service` |
| Tools API | 8005 | `tools_api` |
| LangGraph | 8006 | `langgraph_agent` |
| Image Analyzer | 8007 | `image_analyzer_service` |
| Dashboard Generator | 8008 | `dashboard_generator` |
| Fixture LLM | 8010 | `fixture_llm` |
| Integration Stubs | 8020 | `integration_stubs` |

---

## Ingestion — `POST /signals`

Accepts a `Signal`, validates, forwards to n8n webhook.

```json
{
  "sig_id": "SIG-001",
  "description": "Orders API 5xx rate elevated",
  "service": "orders-api",
  "severity_hint": "high",
  "reporter": "grafana"
}
```

---

## Predictor — `POST /analyse`

Course crosswalk of Image Analyser.

**Request:**

```json
{
  "service": "orders-api",
  "metric_window": {"values": [1.2, 1.5, 2.1, 3.0, 4.2]},
  "context": {"alert_name": "HighErrorRate"}
}
```

**Response:**

```json
{
  "incident_class": "error_rate_spike",
  "severity": "P2",
  "confidence": 0.91,
  "classifier": {"engine": "torch", "method": "1d-cnn"}
}
```

---

## RAG — `POST /query`

**Request:** `{ "query": "...", "limit": 3 }`

**Response:**

```json
{
  "answer": "# Runbook excerpt…",
  "citations": [{"source_id": "orders_api_error_spike", "excerpt": "…"}],
  "refused": false
}
```

Off-topic or weak retrieval → `refused: true`.

---

## Guardrails

### `POST /check/input`

```json
{"text": "Orders API error rate > 5%"}
```

### `POST /check/output`

```json
{"text": "Probable cause: cache eviction per INC-101"}
```

**Response (both):**

```json
{"passed": true, "flags": [], "reason": ""}
```

Frozen schema — never `{valid, reason}` or `{pass, ...}`.

---

## LangGraph — `POST /agent/run`

**Request:**

```json
{
  "incident_id": "INC-101",
  "question": "What similar incidents and runbooks apply?"
}
```

**Response:** Validated `TriageReport` (category, p_level, summary, probable_cause, citations, owner_team, …).

---

## Image Analyzer — `POST /analyze`

Supporting seam (not in current n8n flow). Multipart image upload.

**Response:**

```json
{
  "room_type": "exterior",
  "condition_score": 3,
  "confidence": 0.72
}
```

---

## Tools API (selected)

| Endpoint | Purpose |
|----------|---------|
| `POST /tools/similar-incidents` | Historical incident lookup |
| `POST /tools/service-context` | Service ownership + SLO context |
| `POST /escalations` | P1 escalation preview |
| `GET /audit` | Audit log |

---

## Fixture LLM — `POST /v1/chat/completions`

OpenAI-compatible deterministic responses for Stage A n8n nodes.

---

## OpenAPI

Each FastAPI service serves interactive docs at `/docs` when running locally.
