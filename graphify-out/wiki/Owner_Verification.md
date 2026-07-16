# Owner Verification

> 6 nodes · cohesion 0.40

## Key Concepts

- **verify_owner_team()** (6 connections) — `services/guardrails/guardrails_service/owner_check.py`
- **owner_check.py** (4 connections) — `services/guardrails/guardrails_service/owner_check.py`
- **_auth_headers()** (2 connections) — `services/guardrails/guardrails_service/owner_check.py`
- **AsyncClient** (1 connections)
- **Owner-team verification against the Tools API — fail-closed by design.** (1 connections) — `services/guardrails/guardrails_service/owner_check.py`
- **Return True when owner_team is confirmed via Tools API.      When ``service``** (1 connections) — `services/guardrails/guardrails_service/owner_check.py`

## Relationships

- [Guardrails Service](Guardrails_Service.md) (2 shared connections)
- [Guardrail Check Logic](Guardrail_Check_Logic.md) (1 shared connections)

## Source Files

- `services/guardrails/guardrails_service/owner_check.py`

## Audit Trail

- EXTRACTED: 15 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*