---
name: agent-development
description: Creates focused Cursor project subagents under .cursor/agents. Use when defining a reusable reviewer, tester, workflow guardian, or other isolated project-specific agent.
disable-model-invocation: true
---

# Cursor Subagent Development

## Location and format

Create project agents as `.cursor/agents/<name>.md`:

```markdown
---
name: focused-agent
description: Specific capability and trigger. Use proactively when ...
---

You are ...
```

Use lowercase hyphenated names. Cursor project agents require `name` and
`description`; do not copy Claude plugin fields such as `color`, plugin namespaces,
or unsupported tool lists.

## Workflow

1. Define one narrow responsibility and concrete trigger scenarios.
2. Prefer project scope for PETER PAN-specific contract, n8n, test, or security behavior.
3. Write a specific proactive description so delegation is discoverable.
4. In the prompt body, define workflow, hard constraints, and exact output evidence.
5. Keep frozen contracts, synthetic-only data, secrets rules, and approval gates explicit.
6. Document the new agent in `docs/AGENT-TOOLING.md`.
7. Reload Cursor and invoke the subagent against a read-only sample task.

Avoid generic agents that duplicate built-in reviewers or grant unnecessary mutation
authority. Never embed credentials, local paths outside the repository, or live resource IDs.
