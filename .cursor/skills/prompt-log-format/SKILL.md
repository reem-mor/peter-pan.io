---
name: prompt-log-format
description: Use when writing or updating the Prompt Engineering Log — the 25% deliverable. Enforces the exact required format for all 5 surfaces.
---

# Prompt Engineering Log — Required Format (25% of grade)

Five surfaces. Five iterations each. Ten+ test cases per surface. No shortcuts —
this deliverable is worth as much as all EC2 services combined.

## The 5 surfaces (fixed list)
1. n8n Information Extractor (Node 4) — systemPromptTemplate
2. n8n AI Agent (Node 5) — system prompt + tool descriptions
3. RAG retrieval prompt (RAG service) — context injection + citation
4. Guardrails rail prompts (Guardrails service) — topic detection + output audit
5. Ollama system prompt (Streamlit assistant) — grounding + refusal
(Optional #6 for bonus: Dashboard Generator prompt — valid JSON, relevant panels)

## Entry format per surface (exact structure, no deviations)
```
## Surface N: <name>
### Test suite
10+ cases, each: input, expected behavior. Mix normal / edge / adversarial.

### V1 — Baseline
The prompt verbatim. Results table: case | pass/fail | actual output (short).

### V2 — <one-sentence failure being fixed>
What changed in the prompt (diff-style or bolded). Results. Regressions? y/n.

### V3 — <one-sentence failure being fixed>
Same structure.

### V4, V5 — Refinement
Same structure. By V5: 2-3 sentences on what you LEARNED about how this
model responds (phrasing patterns that work, what consistently fails).

### Final
The final prompt verbatim. One-line justification per design decision.
Pass rate: X/10.
```

## Honesty rules
- Real iterations only. If a version made things worse, that's a VALID entry —
  document the regression and the revert. Fabricated smooth progress reads as
  fake to any experienced grader.
- The failure sentence must be specific: "V2 fixed: extractor invented a
  region when none was stated" — not "improved accuracy".
- Test cases run against the SAME suite every version — no moving goalposts.
- Where git/chat history contains real past iterations, reconstruct from it
  and say so; where it doesn't, run the iterations now for real.

## Mechanics
- One markdown file per surface under `docs/prompt-log/`, plus an index page.
- Prompts under test live in versioned files (not inline in n8n/UI code) so
  each V is a real commit — the git history IS the evidence.
