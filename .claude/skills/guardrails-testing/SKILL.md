---
name: guardrails-testing
description: Use when working on PETER PAN's Guardrails service — the input rail (genuine ops event, injection block, HE/EN), the output rail (no invented owners/versions/paths, no destructive verbs), the deterministic regex floor, the frozen GuardrailResult response, or the frozen test sets. Trigger when editing services/guardrails/, Colang rails, the regex floor, the GuardrailResult contract, or the input/output guardrail nodes in n8n. Core principle: the deterministic floor has final say — no LLM output can override a hard safety rule.
---

# Guardrails Testing

Two endpoints, `POST /check/input` and `POST /check/output`, each returning a frozen
`GuardrailResult`. Architecture: **NeMo + Colang rails on top, deterministic regex floor
underneath.** The floor decides last. This ordering is the whole point — it kills the
"LLM always passes / always fails" risk.

## Frozen response contract (docs/contracts/contracts.py)
```python
class GuardrailResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    passed: bool                                    # `pass` is a Python keyword — field is `passed`
    flags: list[str] = Field(default_factory=list)  # violation codes; non-empty -> review queue
    reason: str = Field(default="", max_length=500) # human-readable, only when not passed
```
Notes:
- `flags` is a **list** — surface every violation at once, not one at a time.
- The output rail's `flags` map straight onto `TriageReport.guardrail_flags` (non-empty -> human review).
- This is a frozen contract: it's vendored into each service as `<pkg>/contracts.py` and the
  contract-identity test asserts the copies match. Changing it requires an ADR.
- The guideline's `safe_text` field is intentionally **not** carried — incidents are flagged for
  human review, not auto-sanitized. This is a declared, defensible domain decision.

## Why the floor exists
An LLM-based rail can be talked out of its own rules (prompt injection, jailbreak, or drift). So
the regex/deterministic floor runs *after* the LLM rail and has final authority on hard rules. If
the floor sets `passed=false`, it stays false regardless of what the LLM rail concluded. Never let
a change route around the floor or let the LLM's verdict override it.

## Input rail — what it must catch (`/check/input`)
| Check | Behavior |
|---|---|
| Genuine ops event | Reject off-topic / non-incident chatter |
| Prompt injection | Block "ignore previous instructions", role-play escapes, tool-hijack attempts |
| Language | Accept Hebrew + English (multilingual detection); don't reject valid HE input |
| Malformed input | Missing required fields -> structured reject, not a crash |

Rejects from machine sources return HTTP `200` with `passed=false` + `reason` (not a 4xx that
breaks the n8n branch).

## Output rail — what it must block (`/check/output`)
| Check | Behavior |
|---|---|
| Invented owners | `owner_team`/`escalation_path` not verifiable against Tools API -> block |
| Invented versions/paths | Fabricated version strings, file paths, hostnames -> block |
| Destructive verbs | `rm`, `drop`, `delete`, `truncate`, `kill -9`, `terminate`, force-push, etc. in `recommended_steps` -> block |
| Uncited claims | A report asserting a fact with no `citations` entry -> block |

Blocked output sets `passed=false` with the relevant `flags`, and n8n routes it to the **human
review queue** — never auto-published. Pass incident context into the output rail via a wrapper
request model so it can verify owner/service against the actual incident and the Tools API.

## Frozen test sets (do NOT mutate mid-iteration)
- **Input:** 10 valid + 10 invalid (invalid includes off-topic, injection, malformed, >=1 HE case).
- **Output:** 10 clean + 10 poisoned (poisoned includes invented owner, fabricated path/version,
  destructive verb, and uncited claim).

## Target metric
**False-positive rate < 5%** on valid inputs — the rails should rarely block legitimate traffic.
Track FP rate as the headline number; a rail that blocks everything is as broken as one that
blocks nothing.

## Adversarial cases to include
Injection variants, poisoned-corpus content surfacing in output, destructive-recommendation
attempts, owner-spoofing, mixed HE/EN evasion. These make the guardrails a *security* control,
not a spell-checker — and they're what impresses a reviewer.

## When editing here
- The regex floor is law. Never disable it "temporarily" or let the LLM rail's pass override it.
- Never weaken a rail to lower the FP rate — fix the rule precision instead, and report the real number.
- Any rail change -> re-run both frozen sets + the adversarial cases; FP rate must stay < 5% and no
  poisoned case may pass.
- Changing `GuardrailResult` -> STOP; it's a frozen contract (ADR required).
