---
name: streamlit-demo-ui
description: Use for any Streamlit UI work — layout, UX polish, demo readiness, the assistant tab, or the alert submission tab.
---

# Streamlit UI — Professional Demo Standards

The UI is what employers and the lecturer actually SEE. It gets judged in the
first 10 seconds. Professional here means calm, legible, and never broken —
not flashy.

## Structure (per course requirement — two tabs)
1. **Assistant** — chat vs local Ollama. Streamed responses (`st.write_stream`),
   chat history in `st.session_state`, system prompt loaded from a file
   (it's prompt surface #5 — must be versionable, not inline string).
2. **Submit Alert** — form → POST to n8n webhook → render the returned
   incident brief + dashboard link.

## Non-negotiable UX rules
- **Nothing hangs silently.** Every network call wrapped in `st.status()` or
  a spinner with a stage label ("Enriching from logs…", "Classifying…",
  "Generating dashboard…"). Timeout on every request (10s), and a human
  error message on failure — never a raw traceback on screen.
- **The demo path never depends on a live LLM.** If the fixture path is
  active, show a small subtle badge ("demo data") — honest, not hidden.
- **Result rendering:** incident brief as structured blocks
  (`st.metric` for severity/class/confidence, expander for RAG citations,
  a prominent `st.link_button` to the generated Grafana dashboard). Not one
  giant JSON dump — but DO include a collapsed "raw response" expander for
  the technical audience.
- **Rejection paths are first-class.** Input-guardrail fail and
  output-guardrail fail each render a clear explanation card showing
  `{passed, flags, reason}` — these are two of the four required video
  segments, they must look intentional.

## Visual discipline
- One accent color, consistent with Grafana's dark theme (the dashboard opens
  next to the app in the demo — they should look like one product).
- `st.set_page_config(page_title="PETER PAN", layout="wide")`, real page icon.
- No emoji noise in UI copy. Short labels. English UI (employer-facing).
- No custom CSS hacks beyond `st.markdown` minimal touches — fragile in demos.

## Demo-safety
- All URLs/ports from env (`N8N_WEBHOOK_URL`, `GRAFANA_URL`) — switching
  laptop → EC2 must be a .env change, zero code edits.
- A `DEMO_MODE=1` env that forces fixtures — the recording insurance switch.
