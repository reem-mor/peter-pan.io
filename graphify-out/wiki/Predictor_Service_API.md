# Predictor Service API

> 40 nodes · cohesion 0.07

## Key Concepts

- **app.py** (22 connections) — `services/predictor/predictor_service/app.py`
- **_run_classifier()** (7 connections) — `services/predictor/predictor_service/app.py`
- **analyse()** (6 connections) — `services/predictor/predictor_service/app.py`
- **request_validation_error()** (5 connections) — `services/predictor/predictor_service/app.py`
- **match_context()** (5 connections) — `services/predictor/predictor_service/classifier.py`
- **predict()** (5 connections) — `services/predictor/predictor_service/classifier.py`
- **classification_context()** (4 connections) — `services/predictor/predictor_service/category.py`
- **classifier.py** (4 connections) — `services/predictor/predictor_service/classifier.py`
- **ewma.py** (4 connections) — `services/predictor/predictor_service/ewma.py`
- **score()** (4 connections) — `services/predictor/predictor_service/ewma.py`
- **fixture_window()** (4 connections) — `services/predictor/predictor_service/fixtures.py`
- **AnalyseRequest** (3 connections) — `services/predictor/predictor_service/app.py`
- **AnalyseResponse** (3 connections) — `services/predictor/predictor_service/app.py`
- **auth.py** (3 connections) — `services/predictor/predictor_service/auth.py`
- **require_bearer_token()** (3 connections) — `services/predictor/predictor_service/auth.py`
- **category.py** (3 connections) — `services/predictor/predictor_service/category.py`
- **severity_band()** (3 connections) — `services/predictor/predictor_service/ewma.py`
- **fixtures.py** (3 connections) — `services/predictor/predictor_service/fixtures.py`
- **ADR 0004 — Guardrail result and predictor taxonomy contracts** (2 connections) — `docs/adr/0004-guardrail-and-predictor-contracts.md`
- **BaseModel** (2 connections)
- **JSONResponse** (1 connections)
- **RequestValidationError** (1 connections)
- **healthz()** (1 connections) — `services/predictor/predictor_service/app.py`
- **Any** (1 connections)
- **Request** (1 connections)
- *... and 15 more nodes in this community*

## Relationships

- [PyTorch Classifier Training](PyTorch_Classifier_Training.md) (3 shared connections)
- [Guardrails Service](Guardrails_Service.md) (1 shared connections)
- [n8n Bootstrap & Demo Assets](n8n_Bootstrap_%26_Demo_Assets.md) (1 shared connections)

## Source Files

- `docs/adr/0004-guardrail-and-predictor-contracts.md`
- `services/predictor/predictor_service/app.py`
- `services/predictor/predictor_service/auth.py`
- `services/predictor/predictor_service/category.py`
- `services/predictor/predictor_service/classifier.py`
- `services/predictor/predictor_service/ewma.py`
- `services/predictor/predictor_service/fixtures.py`

## Audit Trail

- EXTRACTED: 115 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*