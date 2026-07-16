# Policy Engine Interface

> 14 nodes · cohesion 0.26

## Key Concepts

- **PolicyEngine** (10 connections) — `services/guardrails/guardrails_service/policy_engine.py`
- **Signal** (9 connections) — `services/guardrails/guardrails_service/contracts.py`
- **TriageReport** (9 connections) — `services/guardrails/guardrails_service/contracts.py`
- **NoopPolicyEngine** (9 connections) — `services/guardrails/guardrails_service/policy_engine.py`
- **CheckInputRequest** (8 connections) — `services/guardrails/guardrails_service/app.py`
- **CheckOutputRequest** (8 connections) — `services/guardrails/guardrails_service/app.py`
- **policy_engine.py** (7 connections) — `services/guardrails/guardrails_service/policy_engine.py`
- **BaseModel** (2 connections)
- **Anything that enters the system: Grafana alert, WebUI form, deploy event, compla** (1 connections) — `services/guardrails/guardrails_service/contracts.py`
- **The one artifact PETER PAN produces. Output-guardrail-checked before routing.** (1 connections) — `services/guardrails/guardrails_service/contracts.py`
- **Protocol** (1 connections)
- **Pluggable policy-engine seam (BUILD_PLAN §3, GRD row: "NeMo stubbed behind same** (1 connections) — `services/guardrails/guardrails_service/policy_engine.py`
- **Additional policy checks layered on top of the deterministic regex floor.** (1 connections) — `services/guardrails/guardrails_service/policy_engine.py`
- **Stage A default — contributes no additional flags beyond the regex floor.** (1 connections) — `services/guardrails/guardrails_service/policy_engine.py`

## Relationships

- [Guardrails Service](Guardrails_Service.md) (7 shared connections)
- [Guardrails Contracts](Guardrails_Contracts.md) (7 shared connections)
- [Guardrail Check Logic](Guardrail_Check_Logic.md) (2 shared connections)
- [Policy Input Checks](Policy_Input_Checks.md) (2 shared connections)
- [Policy Output Checks](Policy_Output_Checks.md) (2 shared connections)

## Source Files

- `services/guardrails/guardrails_service/app.py`
- `services/guardrails/guardrails_service/contracts.py`
- `services/guardrails/guardrails_service/policy_engine.py`

## Audit Trail

- EXTRACTED: 42 (62%)
- INFERRED: 26 (38%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*