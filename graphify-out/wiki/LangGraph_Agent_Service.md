# LangGraph Agent Service

> 28 nodes · cohesion 0.10

## Key Concepts

- **app.py** (14 connections) — `services/langgraph-agent/langgraph_agent/app.py`
- **contracts.py** (10 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **BaseModel** (7 connections)
- **TriageReport** (5 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **AgentRunRequest** (4 connections) — `services/langgraph-agent/langgraph_agent/app.py`
- **_build_client()** (4 connections) — `services/langgraph-agent/langgraph_agent/app.py`
- **agent_run()** (3 connections) — `services/langgraph-agent/langgraph_agent/app.py`
- **auth.py** (3 connections) — `services/langgraph-agent/langgraph_agent/auth.py`
- **require_bearer_token()** (3 connections) — `services/langgraph-agent/langgraph_agent/auth.py`
- **GuardrailResult** (3 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **Incident** (3 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **IncidentContext** (3 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **Signal** (3 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **Citation** (2 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **DeployRef** (2 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **healthz()** (1 connections) — `services/langgraph-agent/langgraph_agent/app.py`
- **AsyncClient** (1 connections)
- **BaseModel** (1 connections)
- **LangGraph Agent Service — ``POST /agent/run`` (BUILD_PLAN §3, LangGraph agent r** (1 connections) — `services/langgraph-agent/langgraph_agent/app.py`
- **Factory so tests can monkeypatch in an ``httpx.MockTransport`` client     witho** (1 connections) — `services/langgraph-agent/langgraph_agent/app.py`
- **HTTPAuthorizationCredentials** (1 connections)
- **Shared bearer-auth dependency for non-health routes.  Vendored per-service (AG** (1 connections) — `services/langgraph-agent/langgraph_agent/auth.py`
- **PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1** (1 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **Anything that enters the system: Grafana alert, WebUI form, deploy event, compla** (1 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- **Output of the n8n context-enrichment branches (nodes MW/DEP/CMP → merge).** (1 connections) — `services/langgraph-agent/langgraph_agent/contracts.py`
- *... and 3 more nodes in this community*

## Relationships

- [Agent Graph Logic](Agent_Graph_Logic.md) (2 shared connections)
- [n8n Bootstrap & Demo Assets](n8n_Bootstrap_%26_Demo_Assets.md) (1 shared connections)
- [RAG Query API](RAG_Query_API.md) (1 shared connections)
- [Tools API Service](Tools_API_Service.md) (1 shared connections)
- [UI Library & Shared Contracts](UI_Library_%26_Shared_Contracts.md) (1 shared connections)

## Source Files

- `services/langgraph-agent/langgraph_agent/app.py`
- `services/langgraph-agent/langgraph_agent/auth.py`
- `services/langgraph-agent/langgraph_agent/contracts.py`

## Audit Trail

- EXTRACTED: 80 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*