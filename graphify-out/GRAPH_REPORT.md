# Graph Report - peter-pan.io  (2026-07-16)

## Corpus Check
- 188 files · ~98,498 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1451 nodes · 2126 edges · 102 communities (89 shown, 13 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 81 edges (avg confidence: 0.69)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7091f4ca`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- incident_analysis.py
- validator.py
- app.py
- graph.py
- escalation_service.py
- vector_rag.py
- notification_dispatch.py
- app.py
- PETER PAN — Layer 3 Spec-Compliance Matrix
- data_access.py
- Layer 2 Validation Report — PETER PAN
- train.py
- app.py
- app.py
- PETER PAN — 5–7 Minute Demo Script
- run_e2e.py
- app.py
- text_utils.py
- PETER PAN — Documentation Reconciliation & Fix Report
- PETER PAN — Final Project Plan & Guideline Crosswalk
- PETER PAN — End-to-End Project Document
- llm_client.py
- Security — PETER PAN
- PETER PAN — Master Requirements & Build Checklist
- LocalRetriever
- CLAUDE.md — PETER PAN
- Surface 1: n8n Information Extractor (Node 4) — systemPromptTemplate
- PETER PAN — Build Plan
- PETER PAN — Implementation Checklist (Course Spec Audit)
- generate_alert_stream.py
- generate_demo_data.py
- BUILD_PLAN.md
- rules.py
- contracts.py
- contracts.py
- contracts.py
- observability.py
- PolicyEngine
- kb_corpus.py
- API Reference — PETER PAN
- Testing — PETER PAN
- harden_stage_a_n8n.py
- app.py
- bootstrap_n8n_local.py
- validators.py
- app.py
- contracts.py
- app.py
- AWS Deployment — PETER PAN
- Local Development — PETER PAN
- PETER PAN — End-to-End Audit (2026-07-10)
- PETER PAN — Model, Memory & Database Decisions
- _iter_suites
- Agent tooling — PETER PAN
- check_output
- Decision
- Setup — PETER PAN
- PETER PAN — Agentic incident-response platform
- Orders API Deployment Incident — INC-20260610-001
- Postgres Primary Connection Pool Exhaustion — INC-20260618-002
- Redis Cache Degradation — INC-20260625-003
- Database Connectivity Runbook
- Deployment Rollback Runbook
- K8s Ingress 5xx Troubleshooting Runbook
- Orders API Error Spike Runbook
- Redis Cache Degradation Runbook
- Local Layer 1→3→2→4 Validation Report
- PETER PAN — AWS demo deployment
- validate-cfn.sh script
- verify_owner_team
- PETER PAN — Session A Layer 3 Audit (2026-07-13)
- n8n — Layer 2 orchestration (the PETER flow)
- Reconciliation Steps 4–5
- K8s Ingress Service Context
- Orders API Service Context
- Payments API Service Context
- Postgres Primary Service Context
- Redis Cache Service Context
- Shop Web Service Context
- ADR 0004 — Guardrail result and predictor taxonomy contracts
- provision_ec2.sh
- .check_input
- .check_output
- ADR 0002 — Model routing, memory, and storage decisions
- export_json_schema.py
- log
- enable_gguf_ec2.sh
- remote_deploy_ec2.sh
- LAYER-2-PROPOSED-DELETIONS.md
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- README.md
- __init__.py

## God Nodes (most connected - your core abstractions)
1. `Layer 2 Validation Report — PETER PAN` - 24 edges
2. `ChatMessage` - 16 edges
3. `PETER PAN — Master Requirements & Build Checklist` - 15 edges
4. `CLAUDE.md — PETER PAN` - 14 edges
5. `PETER PAN — Final Project Plan & Guideline Crosswalk` - 14 edges
6. `Security — PETER PAN` - 13 edges
7. `Testing — PETER PAN` - 13 edges
8. `main()` - 12 edges
9. `analyze_incident()` - 12 edges
10. `NotificationDispatchError` - 12 edges

## Surprising Connections (you probably didn't know these)
- `EscalationServiceError` --uses--> `TriageReport`  [INFERRED]
  services/tools-api/tools_api/escalation_service.py → docs/contracts/contracts.py
- `QueryRequest` --uses--> `Citation`  [INFERRED]
  services/rag/rag_service/app.py → docs/contracts/contracts.py
- `QueryResponse` --uses--> `Citation`  [INFERRED]
  services/rag/rag_service/app.py → docs/contracts/contracts.py
- `EscalationPreviewRequest` --uses--> `TriageReport`  [INFERRED]
  services/tools-api/tools_api/app.py → docs/contracts/contracts.py
- `EscalationRequest` --uses--> `TriageReport`  [INFERRED]
  services/tools-api/tools_api/app.py → docs/contracts/contracts.py

## Import Cycles
- None detected.

## Communities (102 total, 13 thin omitted)

### Community 0 - "incident_analysis.py"
Cohesion: 0.05
Nodes (62): datetime, normalize_environment(), Canonical environment codes and optional aliases for demo datasets and tools., Return canonical environment code; pass through unknown values lowercased., Validate and normalize an environment code.      Returns ``(canonical, None)``, validate_environment(), analyze_incident(), _check_runbook_reference() (+54 more)

### Community 1 - "validator.py"
Cohesion: 0.06
Nodes (38): create_dashboard(), DashboardRequest, DashboardResponse, list_scenarios(), Any, BaseModel, Dashboard Generator — fixture-first Grafana POST service (Session A, port 8008)., Bearer-token auth — enforced only when PETER_SERVICES_TOKEN is set. (+30 more)

### Community 2 - "app.py"
Cohesion: 0.08
Nodes (50): DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla, Output of the n8n context-enrichment branches (nodes MW/DEP/CMP → merge). (+42 more)

### Community 3 - "graph.py"
Cohesion: 0.08
Nodes (43): agent_run(), AgentRunRequest, _build_client(), AsyncClient, BaseModel, LangGraph Agent Service — ``POST /agent/run`` (BUILD_PLAN §3, LangGraph agent r, Factory so tests can monkeypatch in an ``httpx.MockTransport`` client     witho, HTTPAuthorizationCredentials (+35 more)

### Community 4 - "escalation_service.py"
Cohesion: 0.07
Nodes (43): _check_files(), _check_schemas(), _load_csv(), _load_json(), main(), Any, enrich_escalation_context(), format_escalation_messages() (+35 more)

### Community 5 - "vector_rag.py"
Cohesion: 0.07
Nodes (34): load_seed(), main(), Populate the RAG incident vector store (rubric deliverable).  Seeded and idemp, main(), Manual RAG smoke: real ChromaDB retrieval + real GGUF generation.  NOT part of, build_prompt(), CompletionModel, get_generator() (+26 more)

### Community 6 - "notification_dispatch.py"
Cohesion: 0.11
Nodes (36): _aws_region(), _boto3_client(), check_sms_account_ready(), check_sms_account_ready_cached(), _check_sms_topic_route(), _check_sms_voice_v2_ready(), _confirmed_sms_subscriptions(), dispatch_email() (+28 more)

### Community 7 - "app.py"
Cohesion: 0.07
Nodes (32): JSONResponse, RequestValidationError, analyse(), AnalyseRequest, AnalyseResponse, Any, BaseModel, Request (+24 more)

### Community 8 - "PETER PAN — Layer 3 Spec-Compliance Matrix"
Cohesion: 0.06
Nodes (33): §4.1 — RAG Service (`:8003`), §4.2 — Image Analyzer (`:8007`) — status only (Alex ruling), §4.2 — Predictor (`:8002`) *(crosswalk of Image Analyser)*, §4.3 — Guardrails (`:8004`), §4.4 — LangGraph Agent (`:8006`), §4 cross-cutting, §6 — Prompt Log scoreboard (5 surfaces), §7 — Deliverables inventory (Layer-3 items, status-only) (+25 more)

### Community 9 - "data_access.py"
Cohesion: 0.12
Nodes (34): Known owning teams — lets Guardrails verify an owner_team without a service slug, teams(), DataAccessError, _default_data_dir(), _get_pandas(), load_business_impact(), load_escalation_policies(), load_on_call_schedule() (+26 more)

### Community 10 - "Layer 2 Validation Report — PETER PAN"
Cohesion: 0.06
Nodes (32): 10. API test results (sanitized), 11. Playwright results, 12. EC2 service results, 13. Guardrail results, 14. RAG evaluation results, 15. Predictor decision, 16. Image Analyzer decision, 17. LangGraph / LangChain decision (+24 more)

### Community 11 - "train.py"
Cohesion: 0.12
Nodes (29): Module, Random, _build_model(), _load_checkpoint(), load_classifier(), preprocess(), Any, Trained PyTorch classifier serving path (pytorch-predictor skill).  Architectu (+21 more)

### Community 12 - "app.py"
Cohesion: 0.08
Nodes (28): _build_client(), create_signal(), _forward_to_n8n(), _normalize_service_slug(), Any, AsyncClient, Signal, Ingestion Service — accepts, validates, normalizes and forwards Signals.  BUIL (+20 more)

### Community 13 - "app.py"
Cohesion: 0.17
Nodes (28): _agent_evidence(), _agent_sequence(), chat_completions(), ChatCompletionRequest, ChatMessage, _commander_evidence(), _detect_task(), _extract_response() (+20 more)

### Community 14 - "PETER PAN — 5–7 Minute Demo Script"
Cohesion: 0.07
Nodes (25): 1. Context (30s), 2. Assistant tab (1 min), 3. Incident submission (3 min), 4. Guardrail rejection (1 min), 5. Architecture callout (1 min), 6. Evidence (30s), Architecture (submission diagram), Demo Guide — PETER PAN (+17 more)

### Community 15 - "run_e2e.py"
Cohesion: 0.18
Nodes (27): _check_health(), _find_triage_delivery(), _headers(), _incident_from_signal(), _layer3_source_hash(), _load_contracts(), _load_golden(), _looks_like_triage_report() (+19 more)

### Community 16 - "app.py"
Cohesion: 0.09
Nodes (21): Image, analyze_image(), get_model(), FastAPI app for the Image Analyzer microservice (Stage A: ResNet room classifica, Lazy-load model on first request., Bearer-token auth dependency, enforced only when PETER_SERVICES_TOKEN is set., Analyze a property image for room type and condition., require_bearer_token() (+13 more)

### Community 17 - "text_utils.py"
Cohesion: 0.13
Nodes (25): extract_reference_metadata(), _first_meaningful_line(), format_answer_sections(), format_citation_label(), format_citation_preview(), _format_json_alert_preview(), _join_bucket(), _normalize_step_buckets() (+17 more)

### Community 18 - "PETER PAN — Documentation Reconciliation & Fix Report"
Cohesion: 0.09
Nodes (22): 0. How to use this, 1. Severity summary, 2. DELETE — duplicate / superseded files, 3. FIX — conflicts, ranked, 4. IMPROVE, 5. Decisions you must make (before the fix pass), 6. File-by-file verdict (navigation), 7. Recommended execution order (+14 more)

### Community 19 - "PETER PAN — Final Project Plan & Guideline Crosswalk"
Cohesion: 0.09
Nodes (23): 10 · Build order & milestones, 11 · Optional extensions (guideline §10) — all four planned, 12 · Deployment & security (guideline §11), 13 · Top risks & mitigations (abridged — full register in BUILD_PLAN §5), 1 · Executive summary, 2 · Domain translation — the crosswalk dictionary, 3 · Learning objectives coverage (guideline §1.2), 4 · Architecture at a glance (+15 more)

### Community 20 - "PETER PAN — End-to-End Project Document"
Cohesion: 0.09
Nodes (21): 1. The Idea in One Sentence (for the lecturer), 2. Crosswalk Table — Course Requirements vs. My Implementation, 3. The Architecture — Layer by Layer, 4. Prompt Engineering Log — 25% of the Grade (!), 5. Deliverables — Submission Checklist, 6. Rubric Mapping, 7. 12-Day Plan, 8. Cursor Skills — What to Add and Why, by Phase (+13 more)

### Community 21 - "llm_client.py"
Cohesion: 0.18
Nodes (15): BedrockLLMClient, build_llm_client(), FixtureLLMClient, GeminiLLMClient, LLMClient, LLMResult, OllamaLLMClient, Any (+7 more)

### Community 22 - "Security — PETER PAN"
Cohesion: 0.10
Nodes (19): 1. Skills / tooling cleanup (tooling-only, no product code), 2. Security / residue pass (surgical remediation — accepted), 3. Kaggle finding — reclassified as FALSE POSITIVE, 4. Public-release gate — ALL must be checked before `--public`, Appendix — history purge (ONLY if §3 finds a real literal token), Pre-Public Checklist — PETER PAN, Containers, Cursor rules (+11 more)

### Community 23 - "PETER PAN — Master Requirements & Build Checklist"
Cohesion: 0.10
Nodes (19): 0. How to drive this with Cursor + Claude Code, 10. Optional extensions (extra credit) — PETER PAN native coverage, 11. Declared deviations (state to Alex upfront), 12. Two-week build order (T1 = rubric/demo-critical), 13. Pre-submission final gate, 1. Rubric = your priority map (100%), 2. Requirement crosswalk (guideline → PETER PAN), 3. The four layers (+11 more)

### Community 24 - "LocalRetriever"
Cohesion: 0.16
Nodes (11): get_retriever(), LocalRetriever, Path, Pure-Python TF-IDF + keyword retriever for offline RAG.  Stage A deterministic, Return the top-k chunks ranked by TF-IDF cosine similarity., Cached retriever so the corpus is parsed once per process., A single ranked chunk of a corpus document., Split a markdown document into heading-delimited chunks. (+3 more)

### Community 25 - "CLAUDE.md — PETER PAN"
Cohesion: 0.11
Nodes (18): 1. Think before coding, 2. Simplicity first, 3. Surgical changes, 4. Goal-driven execution, Canonical project references, CLAUDE.md — PETER PAN, Declared deviations (state upfront, never hide), Definition of done (per change) (+10 more)

### Community 26 - "Surface 1: n8n Information Extractor (Node 4) — systemPromptTemplate"
Cohesion: 0.11
Nodes (15): Honesty rules (from the skill — binding), Layout, Prompt Engineering Log — PETER PAN, Surfaces, Final, Surface 1: n8n Information Extractor (Node 4) — systemPromptTemplate, Test suite, V1 — Baseline (+7 more)

### Community 27 - "PETER PAN — Build Plan"
Cohesion: 0.12
Nodes (16): 1 · Contracts first, 2 · Packaging decision, 3 · Component inventory (mapped to diagram nodes), 4 · Stages, 5 · Risk register (top 5), 6 · Effort honesty (> 2–3 sessions flagged), 7 · Conflicts (listed, not silently resolved), Knowledge & Comms seams (`KNOW`/`HUM`) (+8 more)

### Community 28 - "PETER PAN — Implementation Checklist (Course Spec Audit)"
Cohesion: 0.12
Nodes (16): Guardrails (`:8004`), Image Analyser → **Predictor** (`:8002`), LangGraph Agent (`:8006`), PETER PAN — Implementation Checklist (Course Spec Audit), Phase 10 — Documentation, Phase 1 — Repository Audit, Phase 2 — Local Development, Phase 3 — Required Services (Course §4 crosswalk) (+8 more)

### Community 29 - "generate_alert_stream.py"
Cohesion: 0.21
Nodes (15): configure_output(), gen_affected_users(), gen_error_rate(), gen_inter_arrival_seconds(), gen_status(), gen_title(), generate(), main() (+7 more)

### Community 30 - "generate_demo_data.py"
Cohesion: 0.22
Nodes (15): configure_output(), consistency_checks(), main(), parse_args(), Namespace, Path, PETER PAN — demo data generator. Produces all CSV/JSON files in data/source wit, write_alerts() (+7 more)

### Community 31 - "BUILD_PLAN.md"
Cohesion: 0.21
Nodes (6): AGENTS.md — PETER PAN, Conventions, Imported Claude Cowork project instructions, PETER PAN - AI Incident Operations Platform, Scope, Architecture

### Community 32 - "rules.py"
Cohesion: 0.19
Nodes (12): GuardrailViolation, Exception, Guardrail-specific exceptions.  This service is self-contained and never impor, Raised when a deterministic regex/policy check rejects a request or response., check_operator_guardrails(), Deterministic regex guardrail floor, isolated from the retired legacy applicatio, Return every disallowed-operational-action match found in ``text``., Flag junk/off-topic text that lacks any operational markers. (+4 more)

### Community 33 - "contracts.py"
Cohesion: 0.19
Nodes (14): Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla (+6 more)

### Community 34 - "contracts.py"
Cohesion: 0.19
Nodes (14): Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla (+6 more)

### Community 35 - "contracts.py"
Cohesion: 0.19
Nodes (14): Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla (+6 more)

### Community 36 - "observability.py"
Cohesion: 0.15
Nodes (10): BaseHTTPMiddleware, LogRecord, configure_logging(), CorrelationMiddleware, default_readiness(), _JsonFormatter, Any, Request (+2 more)

### Community 37 - "PolicyEngine"
Cohesion: 0.26
Nodes (13): CheckInputRequest, CheckOutputRequest, BaseModel, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla, The one artifact PETER PAN produces. Output-guardrail-checked before routing., Signal, TriageReport, NoopPolicyEngine (+5 more)

### Community 38 - "kb_corpus.py"
Cohesion: 0.22
Nodes (12): document_text(), iter_corpus_json_paths(), kb_root(), load_kb_document(), load_kb_manifest(), Any, Path, Load the PETER PAN RAG corpus (JSON documents under ``corpus/``).  Self-contai (+4 more)

### Community 39 - "API Reference — PETER PAN"
Cohesion: 0.15
Nodes (13): API Reference — PETER PAN, Fixture LLM — `POST /v1/chat/completions`, Guardrails, Image Analyzer — `POST /analyze`, Ingestion — `POST /signals`, LangGraph — `POST /agent/run`, OpenAPI, Port map (local compose) (+5 more)

### Community 40 - "Testing — PETER PAN"
Cohesion: 0.15
Nodes (13): CI, Compose syntax, Coverage bars, curl smoke, E2E harness, Health checks, Lint, Per-service pytest (+5 more)

### Community 41 - "harden_stage_a_n8n.py"
Cohesion: 0.27
Nodes (12): api_base(), api_key(), ensure_retries(), fix_if_left_value(), main(), Harden PETER Stage A workflow via n8n REST API (Cloud or self-hosted).  Fixes:, Write TriageReport stores system text under messages.messageValues[].message., Export-safe copy: keep structure, drop active credential ids if present. (+4 more)

### Community 42 - "app.py"
Cohesion: 0.24
Nodes (10): Citation, BaseModel, query(), QueryRequest, QueryResponse, FastAPI app for the RAG microservice.  Retrieval backends (``PETER_VECTOR_BACK, Bearer-token auth dependency, enforced only when PETER_SERVICES_TOKEN is set., Backend-selected retrieval; chroma degrades to TF-IDF when unavailable     (mis (+2 more)

### Community 43 - "bootstrap_n8n_local.py"
Cohesion: 0.39
Nodes (11): _archive_conflicting_peter_workflows(), _credential_id(), _ensure_owner(), _find_workflow(), main(), _patch_and_activate(), _publish_workflow(), Any (+3 more)

### Community 44 - "validators.py"
Cohesion: 0.20
Nodes (9): Exception, QueryValidationError, Domain errors for the RAG service.  This service no longer calls Bedrock direc, Raised when an incoming /query question fails validation.      Carries a ``cod, Pure question validation for the RAG /query endpoint.  Operator/destructive-ac, Extract searchable tokens (length > 1, not stopwords)., Return the trimmed question or raise QueryValidationError with a stable code., tokenize() (+1 more)

### Community 45 - "app.py"
Cohesion: 0.22
Nodes (8): _build_http_client(), get_http_client(), AsyncClient, FastAPI app for the Guardrails microservice (BUILD_PLAN §3, GRD row).  Two end, Bearer-token auth gate — only enforced when PETER_SERVICES_TOKEN is set., Yield the shared outbound httpx client — overridden in tests with a     MockTra, require_auth(), Guardrails microservice — deterministic input/output floor (BUILD_PLAN §3, GRD r

### Community 46 - "contracts.py"
Cohesion: 0.25
Nodes (10): Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Output of the n8n context-enrichment branches (nodes MW/DEP/CMP → merge). (+2 more)

### Community 47 - "app.py"
Cohesion: 0.35
Nodes (9): _check_delivery_auth(), clear_deliveries(), deliveries(), github_deployments(), Any, Local fixtures for GitHub, Slack, and team webhooks — zero external egress., review_queue(), slack_stub() (+1 more)

### Community 48 - "AWS Deployment — PETER PAN"
Cohesion: 0.20
Nodes (10): AWS Deployment — PETER PAN, Deploy application, Enable GGUF (optional Session D), Instance sizing, n8n on EC2, Persistent storage, Post-deploy checks, Provision (CloudFormation) (+2 more)

### Community 49 - "Local Development — PETER PAN"
Cohesion: 0.20
Nodes (10): curl examples, End-to-end harness, Health validation, Local Development — PETER PAN, Playwright smokes (UI + n8n login), Populate ChromaDB (optional, chroma backend), Quick start (one command sequence), Tear down (+2 more)

### Community 51 - "PETER PAN — End-to-End Audit (2026-07-10)"
Cohesion: 0.22
Nodes (8): Baseline QA (pre-hardening), Decision log, File disposition manifest, Open risks, PETER PAN — End-to-End Audit (2026-07-10), Post-hardening verification (2026-07-11), Remaining rubric gaps, Understanding lock (confirmed)

### Community 52 - "PETER PAN — Model, Memory & Database Decisions"
Cohesion: 0.22
Nodes (8): 1 · Model routing — why three tiers, not one, 2 · Memory — where it belongs and where it must NOT, 3 · Database / vector store — two stores, two jobs, 4 · Summary — the mental model to present, PETER PAN — Model, Memory & Database Decisions, The reasoning behind every AI/data choice in the n8n flow (for Alex), Why Bedrock remains an optional Stage C reasoning provider, Why NOT the uploaded workflow's choices

### Community 53 - "_iter_suites"
Cohesion: 0.33
Nodes (8): _has_pytest_suite(), _iter_suites(), main(), Path, Run every test suite from its own rootdir (BUILD_PLAN §2).  Each services/<nam, Return True if *p* looks like a pytest suite (pytest.ini or tests/ dir present)., Return ordered list of directories to run pytest in.      Services come first, Run all discovered suites; return 0 on full success, 1 on any failure.

### Community 54 - "Agent tooling — PETER PAN"
Cohesion: 0.25
Nodes (8): Agent tooling — PETER PAN, Cursor MCP, Graphify, Optional n8n MCP, Project skills, Project subagents, Security, Verification commands

### Community 55 - "check_output"
Cohesion: 0.36
Nodes (8): GuardrailResult, _bounded_reason(), check_input(), check_output(), _validation_reason(), find_destructive_steps(), Return the subset of ``steps`` that contain a disallowed destructive command., ValidationError

### Community 56 - "Decision"
Cohesion: 0.29
Nodes (7): ADR 0003 — System boundaries and service inventory, Consequences, Decision, Four graded primary services (Layer 3 core), Orchestration rule, RAG invocation rule, Supporting infrastructure (not a fifth/fourth graded deviation)

### Community 57 - "Setup — PETER PAN"
Cohesion: 0.29
Nodes (7): Clone and virtualenv, Environment file, Next steps, Ollama (Layer 1 assistant), Prerequisites, Setup — PETER PAN, Verify before first run

### Community 58 - "PETER PAN — Agentic incident-response platform"
Cohesion: 0.29
Nodes (7): Architecture, Development tooling, Documentation, Layout, License, PETER PAN — Agentic incident-response platform, Quick start

### Community 59 - "Orders API Deployment Incident — INC-20260610-001"
Cohesion: 0.29
Nodes (6): Orders API Deployment Incident — INC-20260610-001, Resolution, Reuse Guidance, Root Cause, Summary, Timeline

### Community 60 - "Postgres Primary Connection Pool Exhaustion — INC-20260618-002"
Cohesion: 0.29
Nodes (6): Postgres Primary Connection Pool Exhaustion — INC-20260618-002, Resolution, Reuse Guidance, Root Cause, Summary, Timeline

### Community 61 - "Redis Cache Degradation — INC-20260625-003"
Cohesion: 0.29
Nodes (6): Redis Cache Degradation — INC-20260625-003, Resolution, Reuse Guidance, Root Cause, Summary, Timeline

### Community 62 - "Database Connectivity Runbook"
Cohesion: 0.29
Nodes (6): Database Connectivity Runbook, Escalation, Investigation Steps (read-only), Remediation, Triage Decision Tree, Verification

### Community 63 - "Deployment Rollback Runbook"
Cohesion: 0.29
Nodes (6): Deployment Rollback Runbook, Escalation, Investigation Steps (read-only), Remediation, Triage Decision Tree, Verification

### Community 64 - "K8s Ingress 5xx Troubleshooting Runbook"
Cohesion: 0.29
Nodes (6): Escalation, Investigation Steps (read-only), K8s Ingress 5xx Troubleshooting Runbook, Remediation, Triage Decision Tree, Verification

### Community 65 - "Orders API Error Spike Runbook"
Cohesion: 0.29
Nodes (6): Escalation, Investigation Steps (read-only), Orders API Error Spike Runbook, Remediation, Triage Decision Tree, Verification

### Community 66 - "Redis Cache Degradation Runbook"
Cohesion: 0.29
Nodes (6): Escalation, Investigation Steps (read-only), Redis Cache Degradation Runbook, Remediation, Triage Decision Tree, Verification

### Community 67 - "Local Layer 1→3→2→4 Validation Report"
Cohesion: 0.33
Nodes (6): Documented limitations, Executive summary, Fixes applied during this pass, How to re-verify, Local Layer 1→3→2→4 Validation Report, Pass / fail matrix

### Community 68 - "PETER PAN — AWS demo deployment"
Cohesion: 0.33
Nodes (6): Deploy, PETER PAN — AWS demo deployment, Security notes, Sizing, Teardown, Validate locally

### Community 69 - "validate-cfn.sh script"
Cohesion: 0.60
Nodes (5): fail(), header(), pass(), validate-cfn.sh script, warn()

### Community 70 - "verify_owner_team"
Cohesion: 0.40
Nodes (5): _auth_headers(), AsyncClient, Owner-team verification against the Tools API — fail-closed by design., Return True when owner_team is confirmed via Tools API.      When ``service``, verify_owner_team()

### Community 71 - "PETER PAN — Session A Layer 3 Audit (2026-07-13)"
Cohesion: 0.40
Nodes (4): Doc discrepancies noted (not fixed here), Gaps vs Session A targets, PETER PAN — Session A Layer 3 Audit (2026-07-13), Service inventory

### Community 72 - "n8n — Layer 2 orchestration (the PETER flow)"
Cohesion: 0.40
Nodes (4): Configuration (never inline in the flow), Flow ↔ diagram mapping, Local compose bootstrap, n8n — Layer 2 orchestration (the PETER flow)

### Community 73 - "Reconciliation Steps 4–5"
Cohesion: 0.40
Nodes (4): Execution, Reconciliation Steps 4–5, Scope, Success criteria

### Community 74 - "K8s Ingress Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, K8s Ingress Service Context, Owner

### Community 75 - "Orders API Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Orders API Service Context, Owner

### Community 76 - "Payments API Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Owner, Payments API Service Context

### Community 77 - "Postgres Primary Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Owner, Postgres Primary Service Context

### Community 78 - "Redis Cache Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Owner, Redis Cache Service Context

### Community 79 - "Shop Web Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Owner, Shop Web Service Context

### Community 80 - "ADR 0004 — Guardrail result and predictor taxonomy contracts"
Cohesion: 0.50
Nodes (4): ADR 0004 — Guardrail result and predictor taxonomy contracts, Consequences, Decision, Related decisions

### Community 82 - "provision_ec2.sh"
Cohesion: 0.67
Nodes (3): log(), MSYS_NO_PATHCONV, provision_ec2.sh script

### Community 85 - "ADR 0002 — Model routing, memory, and storage decisions"
Cohesion: 0.67
Nodes (3): ADR 0002 — Model routing, memory, and storage decisions, Consequences, Decisions

## Knowledge Gaps
- **390 isolated node(s):** `MSYS_NO_PATHCONV`, `remote_deploy_ec2.sh script`, `Conventions`, `Scope`, `Imported Claude Cowork project instructions` (+385 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DashboardValidationError` connect `validator.py` to `escalation_service.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `_validate_cases()` connect `run_e2e.py` to `escalation_service.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **What connects `MSYS_NO_PATHCONV`, `remote_deploy_ec2.sh script`, `Conventions` to the rest of the system?**
  _390 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `incident_analysis.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05081585081585081 - nodes in this community are weakly interconnected._
- **Should `validator.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05844155844155844 - nodes in this community are weakly interconnected._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07756813417190776 - nodes in this community are weakly interconnected._
- **Should `graph.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07712765957446809 - nodes in this community are weakly interconnected._