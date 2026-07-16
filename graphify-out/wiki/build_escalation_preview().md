# build_escalation_preview()

> God node · 11 connections · `services/tools-api/tools_api/escalation_service.py`

**Community:** [Escalation Service](Escalation_Service.md)

## Connections by Relation

### calls
- format_escalation_messages() `INFERRED`
- create_escalation() `EXTRACTED`
- enrich_escalation_context() `INFERRED`
- _find_owner_by_team_or_service() `EXTRACTED`
- _resolve_escalation() `INFERRED`
- EscalationServiceError `EXTRACTED`

### contains
- escalation_service.py `EXTRACTED`

### rationale_for
- Build a read-only escalation preview for a TriageReport. Never dispatches. `EXTRACTED`

### references
- Path `EXTRACTED`
- Any `EXTRACTED`
- [TriageReport](TriageReport.md) `EXTRACTED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*