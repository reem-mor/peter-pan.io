# Security — PETER PAN

## Secrets policy

- **Never** commit `.env`, `.cursor/mcp.json`, PEM keys, or live API tokens
- `.env.example` contains only empty `${VAR}` placeholders
- Use `AWS_PROFILE` / SSO over static access keys
- MCP JSON uses `"env": { "KEY": "${KEY}" }` interpolation only

Verify before commit:

```powershell
git status  # must not show .env or mcp.json with secrets
```

## Gitignore coverage

`.env`, `.env.*` (except `!.env.example`), `*.pem`, `.cursor/mcp.json`

## Service authentication

- Inter-service: `Authorization: Bearer $PETER_SERVICES_TOKEN`
- n8n webhook: `X-Peter-Webhook-Secret: $PETER_WEBHOOK_SECRET`

## Input validation

- All FastAPI endpoints use Pydantic v2 models (`extra="forbid"` on contracts)
- Image Analyzer: file type and size limits on upload
- Guardrails: regex floor blocks injection, destructive commands, off-topic input

## Network exposure (EC2)

- Security group: **/32 only** — developer IP, no `0.0.0.0/0` on app ports
- n8n runs on-instance; services communicate on Docker network
- fixture-llm bound to loopback in EC2 compose override

## Containers

- Non-root `appuser` in service Dockerfiles
- No unnecessary `--privileged`
- Health checks on all services

## Logging

- Do not log bearer tokens, webhook secrets, or API keys
- Audit trail via Tools API SQLite (`TOOLS_AUDIT_DB`)

## External calls

- Timeouts on httpx clients in services
- Fixture-first demo path requires **zero** external API calls
- Live LLM paths (Bedrock/Gemini/Ollama) are optional Stage C add-ons

## Dependency review

```powershell
pip audit  # when available
```

Dependabot enabled: `.github/dependabot.yml`

## n8n MCP safety

- Never `test_workflow` on production webhook flows
- Use `update_workflow` with `operations` array for modifications
- Credential bindings do not inherit — set explicitly

## Pre-public checklist

See [`docs/PRE-PUBLIC-CHECKLIST.md`](PRE-PUBLIC-CHECKLIST.md)

## Cursor rules

[`.cursor/rules/secrets-and-mcp-security.mdc`](../.cursor/rules/secrets-and-mcp-security.mdc)
