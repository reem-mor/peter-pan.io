---
name: mcp-integration
description: Configures PETER PAN project MCP servers with environment-only authentication and least privilege. Use when adding, changing, reviewing, or troubleshooting .cursor/mcp.json, Playwright MCP, n8n MCP, or external tool connections.
---

# PETER PAN MCP Integration

## Source of truth

- Project template: `.cursor/mcp.json.example`
- Local configuration: `.cursor/mcp.json` (gitignored)
- Setup and inventory: `docs/AGENT-TOOLING.md`
- Security rules: `.cursor/rules/secrets-and-mcp-security.mdc`

The skill is shared through `.claude/skills/`, but the repository configuration it
governs is Cursor's `.cursor/mcp.json`. Do not create a Claude plugin `.mcp.json`,
use `${CLAUDE_PLUGIN_ROOT}`, or document Claude-only `/mcp` commands here.

## Workflow

1. Confirm the server has a concrete repository use case.
2. Prefer an official hosted server or maintained launcher.
3. Read the server's current documentation before choosing transport or arguments.
4. Add only the required server and permissions to the example.
5. Reference every token, URL, profile, and credential through `${ENV_VAR}`.
6. Keep actual values in user environment variables or the gitignored `.env`.
7. Document setup, scope, and a read-only verification call.
8. Reload Cursor and verify the server under Settings → MCP.
9. Confirm `git status` does not include `.cursor/mcp.json` or a secret-bearing file.

## Configuration pattern

```json
{
  "mcpServers": {
    "example": {
      "command": "npx",
      "args": ["-y", "@vendor/server@latest"],
      "env": {
        "EXAMPLE_TOKEN": "${EXAMPLE_TOKEN}"
      },
      "timeout": 120000
    }
  }
}
```

Use HTTPS for remote transports. Do not place bearer values directly in `args`,
`headers`, JSON examples, documentation, or screenshots.

## Repository defaults

Playwright is the only default project server because it supports the Stage B UI
smoke test without external credentials.

n8n MCP is optional. Use the separate `.cursor/mcp.n8n.json.example` only with a
trusted development or cloud instance. n8n's built-in instance-level MCP must be
enabled by an owner, workflow access must be explicitly scoped, and connection
details come from `N8N_MCP_URL` / `N8N_MCP_TOKEN` (or Cursor `mcp_auth` for the
hosted HTTP MCP endpoint).

Before any n8n MCP call:

- Load the `n8n-flow-guardian` subagent guidance.
- If server status is `error`, call `mcp_auth` then retry a read-only tool.
- Prefer read-only discovery first, then mutate/publish/execute as the user requests.
- Prefer `execute_workflow` for full runs; use `test_workflow` for pin-data isolation.
- On active webhook/Telegram flows, avoid bare `test_workflow` (can deregister the
  webhook) — unpublish first or use `execute_workflow` instead.
- Use operation-based updates and explicit credential bindings.
- Re-export approved PETER flow changes to `n8n/peter-flow.json`.

## n8n flow conventions (migrated from n8n-flow-conventions)

8 nodes fixed (do not add/remove without approval): Webhook → Guardrails Input → IF →
Information Extractor → AI Agent → LLM Chain (+ Structured Output Parser) → Guardrails
Output → Router (Switch). Router owns the 6→3 `incident_class` → category map — only there.

Expression gotchas: `$('Node Name').item.json.field` after merges; HTTP body type JSON
explicitly (422 from FastAPI often means form-encoded); timeouts 30s/60s; IF compares
booleans not strings. Parallel branches reconverge via Merge (Combine by position) before
the Chain. Never hardcode EC2 IP in nodes. Re-export to `n8n/peter-flow.json` after every
approved structural change; strip/verify no tokens or live IPs in the JSON.

## Verification

1. Copy `.cursor/mcp.json.example` to `.cursor/mcp.json`.
2. Reload Cursor.
3. Confirm the server is connected under Settings → MCP.
4. Invoke one read-only tool call.
5. Verify failure behavior with the required environment variable unset.
6. Check that no token or local MCP file appears in the tracked diff.

Stop on authentication, authorization, or entitlement denial. Report the failure;
do not weaken permissions or hardcode a credential to work around it.
