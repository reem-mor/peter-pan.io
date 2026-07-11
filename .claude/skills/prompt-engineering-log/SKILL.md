---
name: prompt-engineering-log
description: Use when working on PETER PAN's Prompt Engineering Log — the graded artifact worth 25% of the project. Trigger when versioning, testing, or documenting any of the five prompt surfaces (extractor, agent/commander, RAG, guardrails, Ollama assistant), or when running their frozen test sets. Enforces the required V1→V5 iteration format, the ≥10-case-per-surface rule, and pass-rate reporting. This is the single highest-ROI documentation task in the project.
---

# Prompt Engineering Log

This is **25% of the grade** — the largest single rubric line. It must show *methodology*, not just final prompts: for each surface, a baseline that fails, targeted fixes, refinement, and a measured pass rate against a frozen test set. Treat every prompt change as an experiment with a recorded result.

## The five surfaces (all required)
| # | Surface | Grounds on | Frozen test set (≥10 each) |
|---|---|---|---|
| 1 | **Info Extractor** | Incident field extraction; *never infers severity* | 10 alerts: missing fields, mixed HE/EN, ≥1 injection |
| 2 | **AI Agent / Commander** | Tool selection + tool descriptions | 10 incidents needing different tool combos |
| 3 | **RAG retrieval** | Citation-enforced grounding | 10 queries, 3 with no KB match ("not in KB") |
| 4 | **Guardrails rails** | Topic rail + output auditor | 10+10 valid/invalid in, 10+10 clean/poisoned out |
| 5 | **Ollama assistant** | SRE grounding / refusal | 10 chats: off-topic, SLA-bait, injection |

## Required format per surface (this exact shape is graded)
```
### Surface N — <name>
Objective: <what this prompt must do>
Frozen test set: <N cases, link to /evaluation/...>

V1 (baseline):   <prompt> → pass rate X/10 — failure modes observed
V2 (targeted):   <what changed and why> → pass rate Y/10
V3 (targeted):   <what changed and why> → pass rate Z/10
V4 (refinement): <what changed and why> → pass rate ...
V5 (final):      <final prompt> → final pass rate

Analysis: which fixes moved the needle, which didn't, remaining known gaps.
```
The **narrative between versions** is what earns the 25% — "V1 hallucinated severity, so V2 added an explicit "extract only, never infer severity" instruction, which fixed 3/4 failures" is worth more than the final prompt alone.

## Rules
- **Freeze the test set before V1.** The cases must not change across iterations, or pass rates aren't comparable. Sets live in `/evaluation/` — treat as immutable per surface.
- **≥10 cases per surface**, including the adversarial/edge cases listed above (injection, mixed-language, no-match, poisoned output).
- **Show real regressions.** If V3 scored lower than V2, keep it in the log and explain — reviewers trust an honest curve over a suspiciously monotonic one.
- **n8n-embedded prompts count.** Surfaces 1, 2, 4 live inside the n8n flow. Hash the prompts embedded in `n8n/peter-flow.json` so you can detect drift between the log and what the flow actually runs.

## Anti-patterns (will cost marks)
- Only showing final prompts (no iteration story) → looks like you didn't do the engineering.
- Changing test cases to make a prompt "pass" → invalidates the whole measurement.
- Fabricated pass rates → run the sets, persist the outputs, cite the run.

## Output
Deliverable is a PDF/DOCX (`docs/prompt-log/`) that grows from Phase 2 onward. Each surface's frozen set and per-version results are reproducible from `/evaluation/`.

## When editing here
- Every prompt change to a surface → re-run its frozen set, record the new pass rate, add a version entry. Never edit a prompt without logging the result.
- Keep the log and the running prompts in sync (hash check for n8n-embedded ones).
