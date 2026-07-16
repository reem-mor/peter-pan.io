# Tools API Service

> 44 nodes · cohesion 0.10

## Key Concepts

- **app.py** (22 connections) — `services/tools-api/tools_api/app.py`
- **TriageReport** (10 connections) — `docs/contracts/contracts.py`
- **enrichment_tools.py** (10 connections) — `services/tools-api/tools_api/enrichment_tools.py`
- **lookup_owner_and_escalation()** (9 connections) — `services/tools-api/tools_api/enrichment_tools.py`
- **score_business_impact()** (9 connections) — `services/tools-api/tools_api/enrichment_tools.py`
- **_find_service_owner()** (9 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **correlate_deployments()** (8 connections) — `services/tools-api/tools_api/enrichment_tools.py`
- **enrich_triage_demo()** (8 connections) — `services/tools-api/tools_api/enrichment_tools.py`
- **_resolve_source_dir()** (8 connections) — `services/tools-api/tools_api/enrichment_tools.py`
- **find_similar_incidents()** (7 connections) — `services/tools-api/tools_api/enrichment_tools.py`
- **lookup_owner()** (7 connections) — `services/tools-api/tools_api/enrichment_tools.py`
- **Path** (7 connections)
- **_ok_or_404()** (6 connections) — `services/tools-api/tools_api/app.py`
- **Any** (6 connections)
- **BaseModel** (6 connections)
- **service_context()** (6 connections) — `services/tools-api/tools_api/app.py`
- **Any** (6 connections)
- **enrich_escalation_context()** (6 connections) — `services/tools-api/tools_api/escalation_message.py`
- **escalation_preview()** (5 connections) — `services/tools-api/tools_api/app.py`
- **recent_deployments()** (5 connections) — `services/tools-api/tools_api/app.py`
- **similar_incidents()** (5 connections) — `services/tools-api/tools_api/app.py`
- **EscalationPreviewRequest** (4 connections) — `services/tools-api/tools_api/app.py`
- **EscalationRequest** (4 connections) — `services/tools-api/tools_api/app.py`
- **EscalationResponse** (4 connections) — `services/tools-api/tools_api/app.py`
- **RecentDeploymentsRequest** (4 connections) — `services/tools-api/tools_api/app.py`
- *... and 19 more nodes in this community*

## Relationships

- [Escalation Service](Escalation_Service.md) (5 shared connections)
- [Incident Analysis & Environment Codes](Incident_Analysis_%26_Environment_Codes.md) (5 shared connections)
- [Canonical Contracts](Canonical_Contracts.md) (2 shared connections)
- [Tools API Data Access](Tools_API_Data_Access.md) (2 shared connections)
- [LangGraph Agent Service](LangGraph_Agent_Service.md) (1 shared connections)
- [n8n Bootstrap & Demo Assets](n8n_Bootstrap_%26_Demo_Assets.md) (1 shared connections)
- [Tools API Contracts](Tools_API_Contracts.md) (1 shared connections)

## Source Files

- `docs/contracts/contracts.py`
- `services/tools-api/tools_api/app.py`
- `services/tools-api/tools_api/enrichment_tools.py`
- `services/tools-api/tools_api/escalation_message.py`
- `services/tools-api/tools_api/incident_analysis.py`

## Audit Trail

- EXTRACTED: 174 (82%)
- INFERRED: 37 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*