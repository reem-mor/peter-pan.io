# n8n Bootstrap & Demo Assets

> 25 nodes · cohesion 0.13

## Key Concepts

- **PETER Flow (n8n)** (12 connections) — `n8n/peter-flow.json`
- **Bootstrap n8n Local Script** (9 connections) — `scripts/bootstrap_n8n_local.py`
- **Client** (8 connections)
- **main()** (7 connections) — `scripts/bootstrap_n8n_local.py`
- **_patch_and_activate()** (5 connections) — `scripts/bootstrap_n8n_local.py`
- **n8n — Layer 2 orchestration (the PETER flow)** (4 connections) — `n8n/README.md`
- **_archive_conflicting_peter_workflows()** (4 connections) — `scripts/bootstrap_n8n_local.py`
- **_credential_id()** (4 connections) — `scripts/bootstrap_n8n_local.py`
- **_find_workflow()** (4 connections) — `scripts/bootstrap_n8n_local.py`
- **n8n Layer 2 Orchestration README** (3 connections) — `n8n/README.md`
- **_ensure_owner()** (3 connections) — `scripts/bootstrap_n8n_local.py`
- **_publish_workflow()** (3 connections) — `scripts/bootstrap_n8n_local.py`
- **_wait_for_n8n()** (3 connections) — `scripts/bootstrap_n8n_local.py`
- **Prompt Engineering Log README** (2 connections) — `docs/prompt-log/README.md`
- **Surface 1: n8n Information Extractor Log** (2 connections) — `docs/prompt-log/surface-1-extractor.md`
- **Surface 2: n8n AI Agent Log** (2 connections) — `docs/prompt-log/surface-2-agent.md`
- **Extractor System Prompt** (2 connections) — `docs/prompt-log/prompts/surface-1-extractor.systemprompt.txt`
- **Agent System Message** (2 connections) — `docs/prompt-log/prompts/surface-2-agent.systemmessage.txt`
- **Any** (2 connections)
- **PETER PAN Demo Script** (1 connections) — `docs/presentation/DEMO-SCRIPT.md`
- **Configuration (never inline in the flow)** (1 connections) — `n8n/README.md`
- **Flow ↔ diagram mapping** (1 connections) — `n8n/README.md`
- **Local compose bootstrap** (1 connections) — `n8n/README.md`
- **Deactivate + archive non-canonical PETER flows that steal peter-signal.      L** (1 connections) — `scripts/bootstrap_n8n_local.py`
- **Streamlit WebUI** (1 connections) — `ui/app.py`

## Relationships

- [Guardrails Service](Guardrails_Service.md) (1 shared connections)
- [Ingestion Service](Ingestion_Service.md) (1 shared connections)
- [LangGraph Agent Service](LangGraph_Agent_Service.md) (1 shared connections)
- [Predictor Service API](Predictor_Service_API.md) (1 shared connections)
- [RAG Query API](RAG_Query_API.md) (1 shared connections)
- [Tools API Service](Tools_API_Service.md) (1 shared connections)
- [UI Library & Shared Contracts](UI_Library_%26_Shared_Contracts.md) (1 shared connections)

## Source Files

- `docs/presentation/DEMO-SCRIPT.md`
- `docs/prompt-log/README.md`
- `docs/prompt-log/prompts/surface-1-extractor.systemprompt.txt`
- `docs/prompt-log/prompts/surface-2-agent.systemmessage.txt`
- `docs/prompt-log/surface-1-extractor.md`
- `docs/prompt-log/surface-2-agent.md`
- `n8n/README.md`
- `n8n/peter-flow.json`
- `scripts/bootstrap_n8n_local.py`
- `ui/app.py`

## Audit Trail

- EXTRACTED: 85 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*