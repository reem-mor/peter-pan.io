# Guardrail Check Logic

> 8 nodes · cohesion 0.36

## Key Concepts

- **check_output()** (8 connections) — `services/guardrails/guardrails_service/app.py`
- **check_input()** (7 connections) — `services/guardrails/guardrails_service/app.py`
- **_validation_reason()** (5 connections) — `services/guardrails/guardrails_service/app.py`
- **_bounded_reason()** (4 connections) — `services/guardrails/guardrails_service/app.py`
- **find_destructive_steps()** (3 connections) — `services/guardrails/guardrails_service/rules.py`
- **GuardrailResult** (2 connections)
- **Return the subset of ``steps`` that contain a disallowed destructive command.** (1 connections) — `services/guardrails/guardrails_service/rules.py`
- **ValidationError** (1 connections)

## Relationships

- [Guardrails Service](Guardrails_Service.md) (5 shared connections)
- [Guardrail Rules & Errors](Guardrail_Rules_%26_Errors.md) (3 shared connections)
- [Policy Engine Interface](Policy_Engine_Interface.md) (2 shared connections)
- [Owner Verification](Owner_Verification.md) (1 shared connections)

## Source Files

- `services/guardrails/guardrails_service/app.py`
- `services/guardrails/guardrails_service/rules.py`

## Audit Trail

- EXTRACTED: 31 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*