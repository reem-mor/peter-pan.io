---
name: peter-evaluation
description: Runs PETER PAN frozen evaluations and Stage A quality gates without external model calls. Use when changing prompts, tools, ingestion, guardrails, retrieval, n8n orchestration, or when making test, coverage, or E2E claims.
---

# PETER PAN Evaluation

## Invariants

- Never mutate frozen evaluation cases during a run.
- Stage A uses synthetic fixtures and local services only.
- `--dry-run` validates inputs; it is not end-to-end evidence.
- Record exact commands and outputs before updating an audit or rubric claim.
- Models may propose; deterministic contracts, thresholds, and guardrails decide.

## Fast gate

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe scripts\run_all_tests.py
.\.venv\Scripts\python.exe evaluation\run_e2e.py --dry-run
docker compose config --quiet
```

## Full Stage A gate

1. Set required local-only values in the gitignored `.env`.
2. Start the fixture stack with the explicit bootstrap profile.
3. Wait for every service health check and n8n workflow activation.
4. Run the E2E harness with `--entrypoint n8n`.
5. Validate every response against `TriageReport`.
6. Inspect integration-stub deliveries for the expected category or review route.
7. Stop the stack without deleting volumes unless the user explicitly approves it.

## Evidence rules

- Report passed, failed, skipped, and warning counts.
- Do not claim 80% coverage without a fresh coverage report and enforced threshold.
- Do not claim zero external egress unless the isolated CI/local compose configuration was used.
- Do not claim prompt improvement without running the same frozen cases for every compared version.
- Store generated result artifacts under `evaluation/results/`; never overwrite frozen inputs.

If the stack is unavailable, run the fast gate and report full E2E as unverified.

## Demo freeze (migrated from demo-script-guard)

Four required video segments (5–8 min): (1) E2E success with live dashboard, (2) input
guardrail reject card, (3) output guardrail review path, (4) Ollama on-topic + off-topic
refusal. From freeze day: every change states which segment it can break; fixtures green
before and after; no new deps/schema/renames; `DEMO_MODE=1` for recording. Rehearse cold
start + all four segments under 8 minutes.
