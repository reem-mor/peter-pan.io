# Ingestion Service

> 33 nodes · cohesion 0.08

## Key Concepts

- **app.py** (12 connections) — `services/ingestion/ingestion_service/app.py`
- **contracts.py** (10 connections) — `services/ingestion/ingestion_service/contracts.py`
- **BaseModel** (7 connections)
- **_forward_to_n8n()** (6 connections) — `services/ingestion/ingestion_service/app.py`
- **_build_client()** (4 connections) — `services/ingestion/ingestion_service/app.py`
- **create_signal()** (4 connections) — `services/ingestion/ingestion_service/app.py`
- **Signal** (4 connections) — `services/ingestion/ingestion_service/contracts.py`
- **_normalize_service_slug()** (3 connections) — `services/ingestion/ingestion_service/app.py`
- **auth.py** (3 connections) — `services/ingestion/ingestion_service/auth.py`
- **require_bearer_token()** (3 connections) — `services/ingestion/ingestion_service/auth.py`
- **GuardrailResult** (3 connections) — `services/ingestion/ingestion_service/contracts.py`
- **Incident** (3 connections) — `services/ingestion/ingestion_service/contracts.py`
- **IncidentContext** (3 connections) — `services/ingestion/ingestion_service/contracts.py`
- **TriageReport** (3 connections) — `services/ingestion/ingestion_service/contracts.py`
- **Signal** (2 connections)
- **Citation** (2 connections) — `services/ingestion/ingestion_service/contracts.py`
- **DeployRef** (2 connections) — `services/ingestion/ingestion_service/contracts.py`
- **healthz()** (1 connections) — `services/ingestion/ingestion_service/app.py`
- **Any** (1 connections)
- **AsyncClient** (1 connections)
- **Ingestion Service — accepts, validates, normalizes and forwards Signals.  BUIL** (1 connections) — `services/ingestion/ingestion_service/app.py`
- **Lowercase, spaces -> dashes. Deterministic, no other transformation.** (1 connections) — `services/ingestion/ingestion_service/app.py`
- **Factory so tests can monkeypatch in an ``httpx.MockTransport`` client     witho** (1 connections) — `services/ingestion/ingestion_service/app.py`
- **POST the validated Signal JSON to the n8n webhook. One retry on     transport-l** (1 connections) — `services/ingestion/ingestion_service/app.py`
- **readyz()** (1 connections) — `services/ingestion/ingestion_service/app.py`
- *... and 8 more nodes in this community*

## Relationships

- [n8n Bootstrap & Demo Assets](n8n_Bootstrap_%26_Demo_Assets.md) (1 shared connections)
- [UI Library & Shared Contracts](UI_Library_%26_Shared_Contracts.md) (1 shared connections)

## Source Files

- `services/ingestion/ingestion_service/app.py`
- `services/ingestion/ingestion_service/auth.py`
- `services/ingestion/ingestion_service/contracts.py`

## Audit Trail

- EXTRACTED: 90 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*