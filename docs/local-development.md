# Local Development — PETER PAN

Single documented startup workflow for the full compose stack.

## Quick start (one command sequence)

```powershell
# From repo root, with .env configured (see setup.md)
docker compose --profile bootstrap --profile ui up --build -d
```

This starts:

| Service | Port | URL |
|---------|------|-----|
| Ingestion | 8001 | http://localhost:8001/healthz |
| Predictor | 8002 | http://localhost:8002/healthz |
| RAG | 8003 | http://localhost:8003/healthz |
| Guardrails | 8004 | http://localhost:8004/healthz |
| Tools API | 8005 | http://localhost:8005/healthz |
| LangGraph | 8006 | http://localhost:8006/healthz |
| Image Analyzer | 8007 | http://localhost:8007/healthz |
| Dashboard Generator | 8008 | http://localhost:8008/healthz |
| Grafana | 3000 | http://localhost:3000 |
| Fixture LLM | 8010 | http://localhost:8010/healthz |
| Integration Stubs | 8020 | http://localhost:8020/healthz |
| n8n | 5678 | http://localhost:5678 |
| Streamlit UI | 8501 | http://localhost:8501 |

The `bootstrap` profile runs `scripts/bootstrap_n8n_local.py` once to import and activate `n8n/peter-flow.json`.

## Populate ChromaDB (optional, chroma backend)

```powershell
$env:PETER_VECTOR_BACKEND = "chroma"
docker compose up -d rag
.\.venv\Scripts\python.exe scripts\populate_vector_store.py
```

Default compose uses TF-IDF (`PETER_VECTOR_BACKEND=tfidf`). Set `PETER_VECTOR_BACKEND=chroma` in `.env` for sentence-transformer + Chroma retrieval.

## Health validation

```powershell
.\.venv\Scripts\python.exe scripts\test_layer3_health.py --include-support
```

## End-to-end harness

```powershell
# Requires running stack + bootstrap
$token = (Get-Content .env | Where-Object { $_ -match '^PETER_SERVICES_TOKEN=' }) -replace 'PETER_SERVICES_TOKEN=',''
.\.venv\Scripts\python.exe evaluation\run_e2e.py --entrypoint n8n --base-url http://localhost --token $token
```

Direct Layer 3 path (no n8n):

```powershell
.\.venv\Scripts\python.exe evaluation\run_e2e.py --entrypoint layer3 --base-url http://localhost --token $token
```

## curl examples

```powershell
curl http://localhost:8001/healthz
curl http://localhost:8002/healthz
curl http://localhost:8003/healthz
curl http://localhost:8004/healthz

# RAG query (replace TOKEN)
curl -X POST http://localhost:8003/query `
  -H "Authorization: Bearer TOKEN" `
  -H "Content-Type: application/json" `
  -d '{"query":"orders API 5xx spike","limit":3}'
```

## WebUI workflow

1. Open http://localhost:8501
2. **Assistant tab** — chat with fixture LLM or Ollama (if `PETER_OLLAMA_URL` set)
3. **Incident Submission tab** — submit a Signal; n8n orchestrates guardrails → extract → agent → TriageReport

## Tear down

```powershell
docker compose --profile bootstrap --profile ui down
# Add -v only if you intend to wipe Chroma/n8n volumes (destructive)
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| n8n webhook 404 | Re-run bootstrap: `docker compose --profile bootstrap up n8n-bootstrap` |
| Service unhealthy | `docker compose logs <service>` |
| E2E token rejected | Match `PETER_SERVICES_TOKEN` in `.env` and `--token` flag |
