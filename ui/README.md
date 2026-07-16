# Layer 1 — Experience (Streamlit WebUI)

Operator-facing surface for PETER PAN.

## Responsibilities

1. **Submit Alert** — form → `POST` to n8n webhook → render `TriageReport` /
   guardrail rejection cards / optional Grafana link.
2. **Assistant** — chat against Fixture LLM or local Ollama (Stage C), grounded
   as an incident/SRE assistant (off-topic refusal).

## Stack

Streamlit · env-driven URLs · HTTP only (no Python imports from `services.*`).

## Key files

| File | Role |
|:---|:---|
| `app.py` | Layout, health probes, tabs |
| `lib.py` | HTTP clients, Signal subset, TriageReport extraction |
| `tests/` | Unit + Playwright smoke |

## Env (see root `.env.example`)

- `PETER_UI_N8N_WEBHOOK_URL` — Layer 2 ingress
- Service health base URLs for the sidebar
- Optional Ollama / fixture-llm chat endpoints
- `DEMO_MODE=1` — force fixture path for recording

## Conventions

Skill: `.claude/skills/frontend-design/` (PETER Streamlit section).  
Architecture: [`docs/ARCHITECTURE.md`](../docs/ARCHITECTURE.md) §3.
