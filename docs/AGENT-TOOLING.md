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
| `.claude/skills/ec2-deploy/` | EC2 provisioning, deployment, recovery, and live validation |
| `.claude/skills/frontend-design/` | Building or refining the operator UI |
| `.claude/skills/guardrails-testing/` | Changing rails, deterministic floors, or frozen guardrail cases |
| `.claude/skills/incident-triage/` | Changing classification, severity, routing, or `TriageReport` generation |
| `.claude/skills/mcp-integration/` | Adding or troubleshooting project MCP servers |
| `.claude/skills/peter-evaluation/` | Running frozen evaluation and Stage A gates |
| `.claude/skills/prompt-engineering-log/` | Versioning and measuring the five graded prompt surfaces |
| `.claude/skills/rag-evaluation/` | Changing retrieval, grounding, citations, or RAG benchmarks |

`.claude/skills/` is the single project source of truth. Claude Code reads it
natively; Cursor reads it through third-party skill compatibility. Keep
**Include third-party Plugins, Skills, and other configs** enabled and verify the
inventory under **Customize → Skills**. Do not mirror skills into `.cursor/skills/`
or `.agents/skills/`: cross-root precedence is undocumented and duplicate copies drift.

References: [Cursor Agent Skills](https://cursor.com/docs/skills),
[Claude Code Agent Skills](https://code.claude.com/docs/en/skills).

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
- `.claude/settings.json` is the shared deny baseline; `.claude/settings.local.json`
  is user-local and gitignored.
- n8n flow export carries credential **names** only, never values.
- Stop after a definitive auth or permission denial; do not weaken scopes or embed a token.
- Verify `git status` does not show `.cursor/mcp.json` before any commit.
