# Presentation Evidence — 2026-07-11

## Verified

- Streamlit loaded at `http://localhost:8501`.
- Health panel reported Ingestion, RAG, Guardrails, Tools API, and Fixture LLM healthy.
- Incident Submission tab and Signal contract were visible through Playwright.
- Unified pytest gate passed with an enforced 80% coverage floor for every Python
  deployment unit, UI, and evaluation harness.
- Full local golden-set E2E passed:
  - orders-api → application / P3 / application team
  - postgres-primary → database / P1 / database team
  - shop-web → application / P3 / application team
  - redis-cache cross-domain → infra / P3 / LangGraph / infra team
  - unsafe request → input rejection
  - informational deploy-window signal → deterministic suppression
  - unknown owner → output guardrail / review queue

## Artifact status

No screenshot or fallback video is stored here. Screenshot creation was skipped during
the automated run, and the available browser integration does not provide a recording
artifact. The UI and submission screen were verified through Playwright accessibility
snapshots instead.

No Bedrock smoke-test evidence is required for Layers 2–3. The account audit confirmed
Claude Sonnet authorization, but provider invocation remains optional Stage C scope.
