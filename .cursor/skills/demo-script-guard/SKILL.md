---
name: demo-script-guard
description: Use during demo preparation and recording days — protects the four required video segments and freezes risk.
---

# Demo Script Guard (days 9–12)

Once demo prep starts, the priority inverts: protecting what works beats
adding anything.

## The four required video segments (5–8 min total)
1. Successful end-to-end: alert → enrich → classify → route → brief →
   **dashboard generated live** (the headline moment — rehearse the timing).
2. Input-guardrail rejection: junk/off-topic alert → clean rejection card
   showing `{passed:false, flags, reason}`.
3. Output-guardrail rejection: a brief that trips the output rail → flagged
   for review, NOT returned as-is.
4. Ollama assistant exchange: one on-topic answer + one off-topic refusal.

## Freeze rules (active from day 9)
- Any code change must state which of the 4 segments it could break, and the
  fixture suite runs before AND after. No green fixtures → revert, no debate.
- No new dependencies, no schema changes, no renames after the freeze.
- `DEMO_MODE=1` (forced fixtures) is the recording default. The live-LLM path
  may be shown as a second take only if the fixture take is already safely
  recorded.

## Rehearsal checklist (run twice before recording)
- [ ] Cold start: `docker compose up -d` from stopped state → all healthchecks
      green in < 2 min. Time it.
- [ ] All 4 segments back-to-back with a stopwatch — total under 8 min
      including narration pauses.
- [ ] Grafana open in an adjacent tab, dark theme, dashboard folder clean of
      test junk (`peter-pan` folder only).
- [ ] Browser: no bookmarks bar with personal items, no notifications,
      no other tabs. Fresh profile is safest.
- [ ] The generated-dashboard moment: verify the link opens in < 5s and the
      panels actually render data (empty panels look worse than no demo).

## Narration
- Open with the one-line story: "PITER connected Knowledge to RAG; PETER PAN
  connects Observability to Monitoring."
- Each segment gets one sentence of setup BEFORE clicking — never narrate
  while waiting for a spinner.
- Close with the panoramic line + the roadmap slide (feedback loop lives
  there, and only there).
