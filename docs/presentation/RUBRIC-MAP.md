# Presentation Rubric Map

## Demonstrated now

- **n8n orchestration:** tracked 8-node spine, context branches, input/output guardrails,
  category routing, review route, P1 preview escalation, and static flow tests.
- **FastAPI services:** isolated deployment units, Pydantic validation, health endpoints,
  structured failure paths, service-level pytest, and enforced coverage floors.
- **Predictive safety:** deterministic EWMA severity floor and non-finite input rejection.
- **Guardrails:** destructive-action checks, prompt-injection cases, Unicode handling,
  owner verification, citation enforcement, and measured safe-input false-positive tests.
- **LangGraph:** real planner → specialists → synthesiser topology with infra, database,
  application, and dependency-failure tests.
- **RAG:** real offline TF-IDF retrieval with citations, refusal threshold, and golden-set
  retrieval evaluation.
- **WebUI:** Streamlit assistant/submission tabs, live health panel, webhook configuration,
  and AppTest/Playwright smoke validation.
- **Enterprise engineering:** least-privilege CloudFormation improvements, generated CI
  credentials, internal no-egress test network, frozen contracts, and audit evidence.
- **EC2 demo deployment:** The Stage A demo EC2 instance is currently running, and the
  full n8n-path E2E passed 7/7 on EC2 on 2026-07-11.

## Verified presentation scenario

`orders-api 5xx spike after deploy`:

- Expected category: `application`
- Expected priority: `P3`
- Expected route: `team:application`
- Result: passed through Ingestion → n8n → output guardrails → route

The same gate also verified:

- `postgres-primary` → `database` / `P1` / `team:database`
- `shop-web` → `application` / `P3` / `team:application`

## Not yet claimable

- Trained PyTorch 1D-CNN/GRU and >75% held-out accuracy
- Corpus size of at least 55 documents
- Five measured prompt iterations across every graded surface
- Real Bedrock Sonnet, Gemini, llama.cpp, or Ollama execution
- Playwright screenshot/recording artifact
- Production deployment path beyond the Stage A demo EC2 instance

These are follow-on rubric items, not hidden as completed Stage A work.
