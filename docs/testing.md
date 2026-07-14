# Testing — PETER PAN

## Unit and integration tests

```powershell
.\.venv\Scripts\python.exe scripts\run_all_tests.py
```

Runs pytest in: all `services/*/tests`, `ui/tests`, `n8n/tests`, `evaluation/tests`, `packages/peter_observability/tests`.

## Lint

```powershell
.\.venv\Scripts\python.exe -m ruff check .
```

## E2E harness

```powershell
# Fixture load only — no HTTP
.\.venv\Scripts\python.exe evaluation\run_e2e.py --dry-run

# Direct Layer 3 (guardrails → agent → guardrails)
.\.venv\Scripts\python.exe evaluation\run_e2e.py --entrypoint layer3 --base-url http://localhost --token <TOKEN>

# Full n8n orchestration (requires compose + bootstrap)
.\.venv\Scripts\python.exe evaluation\run_e2e.py --entrypoint n8n --base-url http://localhost --token <TOKEN>
```

Golden fixtures: `evaluation/golden_signals.json` (frozen — do not mutate mid-run).

## Health checks

```powershell
.\.venv\Scripts\python.exe scripts\test_layer3_health.py --include-support
.\.venv\Scripts\python.exe scripts\test_ec2_public_health.py --host <EC2_IP>
```

## Per-service pytest

```powershell
.\.venv\Scripts\python.exe -m pytest services/rag/tests -q
.\.venv\Scripts\python.exe -m pytest services/guardrails/tests -q
.\.venv\Scripts\python.exe -m pytest services/predictor/tests -q
.\.venv\Scripts\python.exe -m pytest services/langgraph-agent/tests -q
.\.venv\Scripts\python.exe -m pytest ui/tests -q
.\.venv\Scripts\python.exe -m pytest n8n/tests -q
```

## Compose syntax

```powershell
docker compose config --quiet
```

## curl smoke

```powershell
curl http://localhost:8001/healthz
curl http://localhost:8002/healthz
curl http://localhost:8003/healthz
curl http://localhost:8004/healthz
```

## Postman

Import [`postman/peter-pan-core-apis.postman_collection.json`](../postman/peter-pan-core-apis.postman_collection.json).

Set collection variables: `base_url`, `bearer_token`.

## Playwright (WebUI)

With stack running:

```powershell
# Via MCP browser tools or manual:
# 1. Navigate to http://localhost:8501
# 2. Submit incident form
# 3. Verify TriageReport in review queue
```

Screenshots for submission: `docs/presentation/evidence/`

## CI

GitHub Actions: `.github/workflows/ci.yml` — ruff, schema drift, per-service pytest, compose E2E gate.

## Coverage bars

Per-service minimum 80% (enforced in `pyproject.toml` / service configs). Predictor, guardrails, langgraph typically >95%.

## Rubric-specific metrics

| Metric | Target | Where |
|--------|--------|-------|
| Predictor accuracy | >75% | `services/predictor/predictor_service/artifacts/metrics.json` |
| Guardrails FP rate | <5% | `services/guardrails/tests/` FP suite |
| RAG retrieval | top-3 + refusal | `services/rag/tests/test_vector_rag.py` |
