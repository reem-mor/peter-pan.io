# UI Library & Shared Contracts

> 53 nodes · cohesion 0.05

## Key Concepts

- **datetime** (16 connections)
- **lib.py** (15 connections) — `ui/lib.py`
- **contracts.py** (9 connections) — `services/predictor/predictor_service/contracts.py`
- **BaseModel** (7 connections)
- **app.py** (7 connections) — `ui/app.py`
- **_handle_submission()** (7 connections) — `ui/app.py`
- **SubmissionResult** (5 connections) — `ui/lib.py`
- **submit_signal()** (5 connections) — `ui/lib.py`
- **_render_triage_report()** (4 connections) — `ui/app.py`
- **chat_sync()** (4 connections) — `ui/lib.py`
- **classify_webhook_body()** (4 connections) — `ui/lib.py`
- **extract_triage_report()** (4 connections) — `ui/lib.py`
- **Signal** (4 connections) — `ui/lib.py`
- **GuardrailResult** (3 connections) — `services/predictor/predictor_service/contracts.py`
- **Incident** (3 connections) — `services/predictor/predictor_service/contracts.py`
- **IncidentContext** (3 connections) — `services/predictor/predictor_service/contracts.py`
- **Signal** (3 connections) — `services/predictor/predictor_service/contracts.py`
- **TriageReport** (3 connections) — `services/predictor/predictor_service/contracts.py`
- **_render_guardrail_card()** (3 connections) — `ui/app.py`
- **call_fixture_llm()** (3 connections) — `ui/lib.py`
- **call_ollama()** (3 connections) — `ui/lib.py`
- **Citation** (2 connections) — `services/predictor/predictor_service/contracts.py`
- **DeployRef** (2 connections) — `services/predictor/predictor_service/contracts.py`
- **Any** (2 connections)
- **check_health()** (2 connections) — `ui/lib.py`
- *... and 28 more nodes in this community*

## Relationships

- [Incident Analysis & Environment Codes](Incident_Analysis_%26_Environment_Codes.md) (2 shared connections)
- [Canonical Contracts](Canonical_Contracts.md) (1 shared connections)
- [Alert Stream Generator](Alert_Stream_Generator.md) (1 shared connections)
- [Demo Data Generator](Demo_Data_Generator.md) (1 shared connections)
- [Guardrails Contracts](Guardrails_Contracts.md) (1 shared connections)
- [Ingestion Service](Ingestion_Service.md) (1 shared connections)
- [Integration Stubs Service](Integration_Stubs_Service.md) (1 shared connections)
- [LangGraph Agent Service](LangGraph_Agent_Service.md) (1 shared connections)
- [Agent Graph Logic](Agent_Graph_Logic.md) (1 shared connections)
- [RAG Service Contracts](RAG_Service_Contracts.md) (1 shared connections)
- [Tools API Contracts](Tools_API_Contracts.md) (1 shared connections)
- [Escalation Service](Escalation_Service.md) (1 shared connections)

## Source Files

- `services/predictor/predictor_service/contracts.py`
- `ui/app.py`
- `ui/lib.py`

## Audit Trail

- EXTRACTED: 154 (99%)
- INFERRED: 2 (1%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*