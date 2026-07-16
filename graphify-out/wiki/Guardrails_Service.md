# Guardrails Service

> 11 nodes · cohesion 0.22

## Key Concepts

- **app.py** (24 connections) — `services/guardrails/guardrails_service/app.py`
- **get_http_client()** (4 connections) — `services/guardrails/guardrails_service/app.py`
- **_build_http_client()** (3 connections) — `services/guardrails/guardrails_service/app.py`
- **AsyncClient** (3 connections)
- **require_auth()** (2 connections) — `services/guardrails/guardrails_service/app.py`
- **__init__.py** (2 connections) — `services/guardrails/guardrails_service/__init__.py`
- **healthz()** (1 connections) — `services/guardrails/guardrails_service/app.py`
- **FastAPI app for the Guardrails microservice (BUILD_PLAN §3, GRD row).  Two end** (1 connections) — `services/guardrails/guardrails_service/app.py`
- **Bearer-token auth gate — only enforced when PETER_SERVICES_TOKEN is set.** (1 connections) — `services/guardrails/guardrails_service/app.py`
- **Yield the shared outbound httpx client — overridden in tests with a     MockTra** (1 connections) — `services/guardrails/guardrails_service/app.py`
- **Guardrails microservice — deterministic input/output floor (BUILD_PLAN §3, GRD r** (1 connections) — `services/guardrails/guardrails_service/__init__.py`

## Relationships

- [Policy Engine Interface](Policy_Engine_Interface.md) (7 shared connections)
- [Guardrail Check Logic](Guardrail_Check_Logic.md) (5 shared connections)
- [Guardrails Contracts](Guardrails_Contracts.md) (2 shared connections)
- [Owner Verification](Owner_Verification.md) (2 shared connections)
- [Predictor Service API](Predictor_Service_API.md) (1 shared connections)
- [n8n Bootstrap & Demo Assets](n8n_Bootstrap_%26_Demo_Assets.md) (1 shared connections)
- [Guardrail Rules & Errors](Guardrail_Rules_%26_Errors.md) (1 shared connections)

## Source Files

- `services/guardrails/guardrails_service/__init__.py`
- `services/guardrails/guardrails_service/app.py`

## Audit Trail

- EXTRACTED: 43 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*