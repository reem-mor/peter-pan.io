# PETER PAN — 5–7 Minute Demo Script

## 0:00–0:45 · Problem

Production incidents arrive as noisy alerts, deploy events, and human reports. Operators
must validate the signal, gather context, find the correct runbook and owner, assign
priority, and route the incident without letting an LLM invent facts or execute unsafe
actions.

PETER PAN turns that manual triage path into a guarded, auditable workflow.

## 0:45–1:35 · Architecture

Show `docs/peter-pan-system.mmd` and explain the four layers:

1. Streamlit provides the operator interface.
2. n8n owns the workflow and routing.
3. Eight isolated FastAPI units provide ingestion, prediction, retrieval, guardrails,
   deterministic tools, deep reasoning, fixture inference, and local integration stubs.
4. Real providers remain behind the documented `LLMClient` seam for Stage C.

Emphasize that contracts are frozen Pydantic v2 models and services communicate only
over HTTP.

## 1:35–2:20 · Enterprise safety

Show the deterministic floors:

- Regex policy checks always run under the model layer.
- EWMA severity scoring cannot be suppressed by a classifier.
- Owners and escalation paths are verified against the Tools API.
- Citations are schema-required.
- Escalation is preview-first and audit logged.
- CI runs with an internal Docker network and generated ephemeral credentials.

## 2:20–4:30 · Live scenario

Use the `orders-api` golden incident:

- Title: `orders-api 5xx spike after deploy`
- Description: `Error rate above 5% for 10 minutes after deploy`
- Service: `orders-api`
- Environment: `production`
- Severity hint: `warning`

Narrate the path:

1. Ingestion validates `Signal`.
2. n8n input guardrails accept the synthetic incident.
3. Context branches attach deploy and complaint evidence.
4. The fixture model extracts incident fields.
5. The commander and deterministic services produce triage evidence.
6. The writer attempts structured generation; Stage A has a tested deterministic
   contract-valid fallback for parser incompatibility.
7. Output guardrails verify the owner and safe steps.
8. The router delivers an application/P3 report to App Platform and the Slack stub.

Show the resulting `TriageReport` fields: category, P-level, citation, verified owner,
safe recommendations, confidence, and model metadata.

## 4:30–5:25 · Reproducible evidence

Show the verification commands:

```powershell
.\.venv\Scripts\python.exe scripts\run_all_tests.py
.\.venv\Scripts\python.exe evaluation\run_e2e.py --dry-run
.\.venv\Scripts\python.exe evaluation\run_e2e.py --entrypoint n8n --base-url http://localhost --token $env:PETER_SERVICES_TOKEN
```

State the verified result: all three golden signals traversed Ingestion → n8n and reached
the expected team channel with the expected category and P-level.

## 5:25–6:15 · Honest limitations and roadmap

Stage A proves the fixture-backed orchestration and service contracts. It does not claim:

- trained PyTorch classifier accuracy,
- a 55+ document corpus,
- five prompt iterations per surface,
- real Bedrock/Gemini/Ollama execution,
- production AWS deployment.

Those remain ordered Stage B/C rubric work. The current design keeps them as provider or
data swaps without changing the deterministic safety floors.

## 6:15–6:40 · Close

PETER PAN demonstrates the enterprise pattern: models propose, typed contracts and
deterministic controls decide, every external action is previewed, and every claim is
backed by a repeatable test.
