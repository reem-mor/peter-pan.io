# Agent tooling — PETER PAN

## Cursor MCP

Copy [`.cursor/mcp.json.example`](../.cursor/mcp.json.example) to
`.cursor/mcp.json` (gitignored), then reload Cursor and confirm the server under
**Settings → MCP**. Use environment interpolation only; never commit local MCP
configuration or credentials.

| Server | Purpose |
|---|---|
| `playwright` | UI smoke tests |

Playwright is the only default project server. The AWS deployment plugin enabled in
`.cursor/settings.json` is managed by Cursor and is not part of project MCP JSON.

### Optional n8n MCP

n8n provides an instance-level MCP server. It is intentionally opt-in because it can
discover, edit, and execute workflows. Enable it only on a trusted development instance,
then merge [`.cursor/mcp.n8n.json.example`](../.cursor/mcp.n8n.json.example) into the
gitignored `.cursor/mcp.json` and set `N8N_MCP_URL` and `N8N_MCP_TOKEN` as user
environment variables.

Before using n8n MCP, invoke `n8n-flow-guardian`. Never use `test_workflow` on the
live PETER webhook flow, and re-export every approved change to `n8n/peter-flow.json`.

## Project skills

| Skill | Use when |
|---|---|
| `.cursor/skills/repo-tooling/` | CI and dev commands |
| `.cursor/skills/mcp-integration/` | Adding or troubleshooting Cursor MCP servers |
| `.cursor/skills/peter-evaluation/` | Running frozen evaluation and Stage A gates |
| `.cursor/skills/ec2-deploy/` | EC2 provisioning, stack deployment, n8n owner recovery, live validation |
| `.cursor/skills/agent-development/` | Creating focused project subagents |

Cursor skills under `.cursor/skills/` are authoritative for Cursor behavior.
`.claude/skills/` remains Claude-specific; do not assume the formats are interchangeable.

## Project subagents

| Subagent | Trigger |
|---|---|
| `contract-guard` | Contract, schema, request/response, or parser changes |
| `service-tester` | Changes under services, UI, n8n, evaluation, or scripts |
| `n8n-flow-guardian` | n8n MCP, export, bootstrap, or credential changes |
| `secrets-auditor` | Config, deployment, MCP, auth, or pre-commit review |

## Verification commands

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe scripts\run_all_tests.py
docker compose config --quiet
.\.venv\Scripts\python.exe evaluation\run_e2e.py --dry-run
```

`--dry-run` validates fixtures only. A full Stage A claim requires the compose-backed
n8n entrypoint documented by the evaluation harness.

## Security

- Never commit `.env`, `.cursor/mcp.json`, PEM keys, or live AWS/n8n resource IDs.
- n8n flow export carries credential **names** only, never values.
- Stop after a definitive auth or permission denial; do not weaken scopes or embed a token.
- Verify `git status` does not show `.cursor/mcp.json` before any commit.
