# Prompt Engineering Log — PETER PAN

The 25% deliverable. Five surfaces, versioned prompts, real iteration evidence.
Format contract: `.cursor/skills/prompt-log-format/SKILL.md`.

## Layout

- `prompts/` — the prompts under test, extracted byte-for-byte from their runtime
  homes (n8n nodes / services / UI). `n8n/tests/test_prompt_surfaces.py` asserts
  the n8n node content matches these files exactly. Editing a prompt means:
  edit the file → paste into the node → re-export `n8n/peter-flow.json`.
- `test-suites/` — frozen test suites (10+ cases per surface, normal / edge /
  adversarial). The same suite runs against every prompt version — no moving
  goalposts.
- `surface-N-*.md` — the iteration log per surface (V1…V5 + Final).

## Surfaces

| # | Surface | Prompt file(s) | Log | Status |
|---|---------|----------------|-----|--------|
| 1 | n8n Information Extractor (Node 4) | `prompts/surface-1-extractor.systemprompt.txt` | [surface-1-extractor.md](surface-1-extractor.md) | V1 baseline run (live Gemini) |
| 2 | n8n AI Agent / Incident Commander (Node 5) | `prompts/surface-2-agent.systemmessage.txt`, `prompts/surface-2-agent.tools.json` | [surface-2-agent.md](surface-2-agent.md) | suite defined; live baseline BLOCKED → Layer 4 |
| 3 | RAG retrieval prompt (RAG service) | — | — | Layer 3 session |
| 4 | Guardrails rail prompts (Guardrails service) | — | — | Layer 3 session |
| 5 | Ollama system prompt (Streamlit assistant) | — | — | Layer 1 session |

## Honesty rules (from the skill — binding)

Real iterations only; regressions are valid entries; failure sentences must be
specific; reconstruct from git/chat history only where it actually exists.
