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
discover, edit, publish, execute, and test workflows. Enable it on a trusted
development or n8n Cloud instance, then merge **one** entry from
[`.cursor/mcp.n8n.json.example`](../.cursor/mcp.n8n.json.example) into the
gitignored `.cursor/mcp.json` and set `N8N_MCP_URL` / `N8N_MCP_TOKEN` as user
environment variables.

Prefer the `n8n-mcp` **stdio** entry (`npx mcp-remote` → `…/mcp-server/http`). Cursor’s
direct Streamable HTTP transport can fail with `Failed to open SSE stream` against
n8n Cloud even when a manual `initialize` POST returns HTTP 200. Use the
`n8n-mcp-http` block only if HTTP is stable in your Cursor build; `n8n-supergateway`
is a second stdio fallback. Do not point Cursor at an MCP Server Trigger URL
(`/mcp/...`); instance-level MCP is `/mcp-server/http` only.

Before using n8n MCP, invoke `n8n-flow-guardian`. Prefer `execute_workflow` for full
runs and `test_workflow` for pin-data isolation. On an *active* webhook/Telegram flow,
unpublish before `test_workflow` (or use `execute_workflow`) so the production webhook
is not deregistered. Re-export every approved PETER change to `n8n/peter-flow.json`.

If the server shows discovery errors after a config change, fully restart Cursor so it
picks up User env vars, then retry `search_workflows`.

## Project skills

| Skill | Use when |
|---|---|
| `.claude/skills/ec2-deploy/` | EC2 provisioning, deployment, recovery, and live validation |
| `.claude/skills/frontend-design/` | Building or refining the operator UI |
| `.claude/skills/graphify/` | Building or querying the project knowledge graph (`/graphify`) |
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

## Graphify

Knowledge graph for agent navigation ([Graphify](https://github.com/Graphify-Labs/graphify)).
Output lives in `graphify-out/` (commit the map; local noise is gitignored).

**Install (developer machine — not the repo `.venv`):**

```powershell
uv tool install graphifyy
graphify install --project --platform cursor
graphify install --project --platform claude
```

PyPI package is `graphifyy`; CLI command is `graphify`. Do not add Graphify to
`requirements-dev.txt` or service venvs. Do not use `--platform agents` in this repo
(skills stay under `.claude/skills/` only).

**Build / refresh (AST-only, no API cost):**

```powershell
graphify update .
```

**Query:**

```powershell
graphify query "Where is GuardrailResult defined?"
graphify path "GuardrailResult" "TriageReport"
graphify explain "GuardrailResult"
```

Wiring: [`.cursor/rules/graphify.mdc`](../.cursor/rules/graphify.mdc) (`alwaysApply`),
[`.claude/skills/graphify/`](../.claude/skills/graphify/), `.graphifyignore`,
`.claudeignore` (`graphify-out/` so Claude prompt cache is not busted on rebuilds).
Skip `graphify hook install` here — it mutates git config for a merge driver; refresh
manually with `graphify update .` after code changes.

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
