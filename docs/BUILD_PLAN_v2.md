# PETER PAN — Build Plan & Milestone Gates

This document defines the strict local-first build order required by guideline §11.2, enforced as stages. 

## Stage A: Core Pipeline & Fixture Seams
**Goal:** Build the complete data flow (Layers 2 & 3) using deterministic fixtures to prove the architecture before spending API credits.

### 1. Ingestion & Shared Contracts
- Define `Signal`, `Incident`, `TriageReport` in `docs/contracts/contracts.py`.
- Implement `ingestion_service` to validate incoming payloads and forward to n8n webhook.

### 2. Service Stubs & Floors
- `predictor_service`: Implement EWMA/z-score floor. Stub PyTorch inference with fixed weights.
- `guardrails_service`: Implement regex floor for input/output checks. Stub NeMo layer.
- `tools_api`: Implement SQlite-backed API for owners, deploys, and audit logs.
- `fixture_llm`: Implement an OpenAI-compatible endpoint that returns canned responses for predictable testing.

### 3. n8n Orchestration Spine
- Build the 8-node flow in n8n.
- Connect nodes to local service endpoints.
- Configure LM nodes to point to `fixture_llm`.
- Implement context-enrichment branches (maintenance window, GitHub deploys).
- Export flow to `n8n/peter-flow.json`.

### 4. Stage A Evaluation
- Prepare `evaluation/golden_signals.json` with 7 scenarios.
- Run `evaluation/run_e2e.py` to assert the pipeline successfully processes all golden signals and produces valid `TriageReport`s.

**Exit Gate A:** `run_all_tests.py` passes, E2E harness produces expected reports via `fixture_llm`. Tag `v0.1-stage-a`.

## Stage B: User Interface & Active Response Basics
**Goal:** Build the UI and basic active routing mechanisms.

### 1. Streamlit WebUI (`ui/`)
- Implement SRE Assistant chat tab (backed by `fixture_llm` temporarily).
- Implement Incident Submission form tab.
- Render generated `TriageReport`s in the UI.

### 2. Active Routing (n8n Node 8)
- Integrate basic Slack API to create channels and post reports.
- Implement preview-first P1 escalation logic.

**Exit Gate B:** Manual submission from Streamlit flows through n8n and returns a rendered report. Tag `v0.2-stage-b`.

## Stage C: Real Models, RAG, & Deployment
**Goal:** Swap fixtures for real models, implement RAG, train the classifier, and deploy.

### 1. External LLMs
- Configure n8n LM nodes to use Bedrock (Claude Sonnet) and Gemini 2.5 Flash.
- Update `ui/` to use Ollama for local chat.

### 2. RAG Implementation
- Implement Supabase pgvector integration in `rag_service`.
- Populate KB using `scripts/seed_kb.py` (≥55 docs).
- Implement TF-IDF or llama.cpp for retrieval/generation.

### 3. PyTorch Training
- Generate synthetic metrics dataset (`predictive/datagen`).
- Train 1D-CNN/GRU model and integrate checkpoint into `predictor_service`.

### 4. Enterprise Extensions
- Implement Open WebUI review queue.
- Configure Twilio for voice calls on P1s.
- Finalize monitoring dashboard.

### 5. Deployment
- Provision AWS EC2 `t3.large`.
- Deploy stack using `docker-compose`.

**Exit Gate C:** Full E2E suite passes against real LLM providers. EC2 deployment is live. All extensions are functional. Tag `v0.3-stage-c`.
