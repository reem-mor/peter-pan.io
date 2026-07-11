---
name: repo-tooling
description: Maps PETER PAN development commands, environment setup, CI gates, and Cursor tooling. Use when working with setup, .env, Docker Compose, tests, evaluation, MCP, or repository configuration.
---

# PETER PAN Repository Tooling

## Start here

1. Read [`docs/AGENT-TOOLING.md`](../../docs/AGENT-TOOLING.md) first.
2. Treat [`AGENTS.md`](../../AGENTS.md), accepted ADRs, and frozen contracts as constraints.
3. Use `.cursor/mcp.json` for local Cursor MCP configuration. It is gitignored; copy from `.cursor/mcp.json.example`.
4. Never read, print, or commit `.env` or `.cursor/mcp.json`.

## Commands

Run from the repository root with the Python 3.12 virtual environment:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe scripts\run_all_tests.py
docker compose config --quiet
.\.venv\Scripts\python.exe evaluation\run_e2e.py --dry-run
```

Run a service suite from its own import root:

```powershell
Set-Location services\guardrails
..\..\.venv\Scripts\python.exe -m pytest -q
```

For the local n8n import path, set all required variables in the gitignored `.env`,
then use the explicit bootstrap profile:

```powershell
docker compose --profile bootstrap up --build
```

Do not claim full E2E from `--dry-run`; it validates fixtures only.

## Do not

- Change `docs/contracts/`, tool schemas, diagrams, or frozen evaluation cases without the required ADR/approval.
- Commit `.env`, `.cursor/mcp.json`, credentials, live resource IDs, or generated runtime databases.
- Run live n8n workflows, AWS deployments, or destructive Compose commands unless explicitly requested.
- Add commands or paths that do not exist in this repository.
