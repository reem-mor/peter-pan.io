# Setup — PETER PAN

Prerequisites and first-time environment configuration.

## Prerequisites

| Tool | Minimum | Verify |
|------|---------|--------|
| Python | 3.12 | `python --version` |
| Docker Desktop | Latest stable | `docker --version` |
| Git | 2.x | `git --version` |
| Ollama (optional, UI assistant) | 0.3+ | `ollama --version` |

Windows users: use PowerShell from the repo root (`c:\dev\peter-pan.io`).

## Clone and virtualenv

```powershell
git clone https://github.com/reem-mor/peter-pan.io.git
cd peter-pan.io
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
```

## Environment file

```powershell
Copy-Item .env.example .env
```

Edit `.env` and set **non-empty** values for:

- `PETER_SERVICES_TOKEN` — shared bearer token for service-to-service auth
- `PETER_WEBHOOK_SECRET` — webhook header secret for n8n ingestion
- `N8N_ENCRYPTION_KEY` — 32+ character random string
- `N8N_JWT_SECRET` — 32+ character random string
- `N8N_OWNER_PASSWORD` — local n8n admin password

Never commit `.env`. Only `.env.example` (key-less placeholders) is tracked.

## Ollama (Layer 1 assistant)

```powershell
ollama pull llama3.1:8b
# or: ollama pull llama3
```

Set in `.env` when running UI outside compose:

```
PETER_OLLAMA_URL=http://host.docker.internal:11434
PETER_OLLAMA_MODEL=llama3.1:8b
```

## Verify before first run

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe scripts\run_all_tests.py
docker compose config --quiet
.\.venv\Scripts\python.exe evaluation\run_e2e.py --dry-run
```

## Next steps

- Local stack: [local-development.md](local-development.md)
- AWS demo: [aws-deployment.md](aws-deployment.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
