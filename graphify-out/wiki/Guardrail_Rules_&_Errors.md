# Guardrail Rules & Errors

> 15 nodes · cohesion 0.19

## Key Concepts

- **rules.py** (9 connections) — `services/guardrails/guardrails_service/rules.py`
- **GuardrailViolation** (7 connections) — `services/guardrails/guardrails_service/errors.py`
- **scan_text()** (5 connections) — `services/guardrails/guardrails_service/rules.py`
- **check_operator_guardrails()** (4 connections) — `services/guardrails/guardrails_service/rules.py`
- **RuleMatch** (4 connections) — `services/guardrails/guardrails_service/rules.py`
- **scan_off_topic()** (4 connections) — `services/guardrails/guardrails_service/rules.py`
- **errors.py** (3 connections) — `services/guardrails/guardrails_service/errors.py`
- **.__init__()** (1 connections) — `services/guardrails/guardrails_service/errors.py`
- **Exception** (1 connections)
- **Guardrail-specific exceptions.  This service is self-contained and never impor** (1 connections) — `services/guardrails/guardrails_service/errors.py`
- **Raised when a deterministic regex/policy check rejects a request or response.** (1 connections) — `services/guardrails/guardrails_service/errors.py`
- **Deterministic regex guardrail floor, isolated from the retired legacy applicatio** (1 connections) — `services/guardrails/guardrails_service/rules.py`
- **Return every disallowed-operational-action match found in ``text``.** (1 connections) — `services/guardrails/guardrails_service/rules.py`
- **Flag junk/off-topic text that lacks any operational markers.** (1 connections) — `services/guardrails/guardrails_service/rules.py`
- **Raise GuardrailViolation on the first disallowed-operational-action match.** (1 connections) — `services/guardrails/guardrails_service/rules.py`

## Relationships

- [Guardrail Check Logic](Guardrail_Check_Logic.md) (3 shared connections)
- [Guardrails Service](Guardrails_Service.md) (1 shared connections)

## Source Files

- `services/guardrails/guardrails_service/errors.py`
- `services/guardrails/guardrails_service/rules.py`

## Audit Trail

- EXTRACTED: 42 (95%)
- INFERRED: 2 (5%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*