# Incident Analysis & Environment Codes

> 28 nodes · cohesion 0.15

## Key Concepts

- **incident_analysis.py** (19 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **analyze_incident()** (12 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **Any** (11 connections)
- **Path** (9 connections)
- **normalize_environment()** (6 connections) — `services/tools-api/tools_api/environment_codes.py`
- **_correlate_deployments()** (6 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **_resolve_escalation()** (6 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **environment_codes.py** (5 connections) — `services/tools-api/tools_api/environment_codes.py`
- **_check_runbook_reference()** (5 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **_classify_priority()** (5 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **compose_triage_sections()** (5 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **_find_similar_incidents()** (5 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **_normalize_alert()** (5 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **_score_business_impact()** (5 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **compose_triage_narrative()** (4 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **validate_environment()** (3 connections) — `services/tools-api/tools_api/environment_codes.py`
- **_normalize_priority_label()** (3 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **_parse_iso()** (3 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **Canonical environment codes and optional aliases for demo datasets and tools.** (1 connections) — `services/tools-api/tools_api/environment_codes.py`
- **Return canonical environment code; pass through unknown values lowercased.** (1 connections) — `services/tools-api/tools_api/environment_codes.py`
- **Validate and normalize an environment code.      Returns ``(canonical, None)``** (1 connections) — `services/tools-api/tools_api/environment_codes.py`
- **Structured incident analysis over the canonical Tools API datasets.  Runbook *** (1 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **Resolve the notify list and any compliance overrides for a priority.      Over** (1 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **Existence-only check against ``data/runbooks_manifest.json``.      Runbook *co** (1 connections) — `services/tools-api/tools_api/incident_analysis.py`
- **Run the full structured analysis pipeline for an alert.** (1 connections) — `services/tools-api/tools_api/incident_analysis.py`
- *... and 3 more nodes in this community*

## Relationships

- [Tools API Service](Tools_API_Service.md) (5 shared connections)
- [Tools API Data Access](Tools_API_Data_Access.md) (2 shared connections)
- [UI Library & Shared Contracts](UI_Library_%26_Shared_Contracts.md) (2 shared connections)
- [Escalation Service](Escalation_Service.md) (2 shared connections)
- [Text Parsing Utilities](Text_Parsing_Utilities.md) (2 shared connections)

## Source Files

- `services/tools-api/tools_api/environment_codes.py`
- `services/tools-api/tools_api/incident_analysis.py`

## Audit Trail

- EXTRACTED: 120 (94%)
- INFERRED: 7 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*