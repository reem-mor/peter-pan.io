# Graph Report - C:\dev\peter-pan.io  (2026-07-16)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1047 nodes · 1658 edges · 100 communities (57 shown, 43 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 83 edges (avg confidence: 0.69)
- Token cost: 0 this run (cluster-only, no extraction) · cumulative Gemini extraction ≥113,097 input / ≥6,999 output tokens (≈$0.09; see cost.json)

## Graph Freshness
- Built from commit: `3ae3222e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Dashboard Generator Service
- Tools API Service
- Escalation Service
- RAG Retrieval & Generation
- Incident History & Runbooks
- Notification Dispatch
- Predictor Service API
- UI Library & Shared Contracts
- Tools API Data Access
- PyTorch Classifier Training
- Ingestion Service
- Fixture LLM Service
- Incident Analysis & Environment Codes
- Image Analyzer Service
- LangGraph Agent Service
- Text Parsing Utilities
- n8n Bootstrap & Demo Assets
- Service Context Docs
- Agent Graph Logic
- LLM Client Protocols
- Local TF-IDF Retriever
- Alert Stream Generator
- Demo Data Generator
- Guardrail Rules & Errors
- RAG Service Contracts
- Tools API Contracts
- Observability Package
- Policy Engine Interface
- KB Corpus Loader
- n8n Hardening Script
- Canonical Contracts
- RAG Query API
- RAG Query Validation
- Guardrails Service
- Guardrails Contracts
- Integration Stubs Service
- Test Suite Runner
- Guardrail Check Logic
- AWS Demo Deployment README
- CloudFormation Validation (sh)
- Owner Verification
- Ingress 5xx Runbook
- Layer 3 Audit (2026-07-13)
- EC2 Provisioning Script
- Policy Input Checks
- Policy Output Checks
- JSON Schema Export
- EC2 Deploy Script (sh)
- GGUF Enablement Script
- Remote EC2 Deploy Script
- Ingestion Package Init
- LangGraph Agent Package Init
- Predictor Package Init
- RAG Package Init
- Tools API Package Init
- ADR 0002 - Model & Storage
- ADR 0003 - System Boundaries
- Agent Tooling Guide
- API Reference
- Architecture Doc
- AWS Deployment Guide
- Build Plan
- Compliance Matrix
- Demo Guide
- Docs Reconciliation
- Implementation Checklist
- Layer 2 Proposed Deletions
- Layer 2 Validation
- Local Validation Doc
- Local Development Guide
- Master Checklist
- Model & Memory Rationale
- n8n Workflow Doc
- Project Master Doc
- Spec Crosswalk
- Pre-Public Checklist
- Project Plan
- Output Auditor Prompt
- Topic Detection Prompt
- Security Doc
- Setup Doc
- Testing Doc
- External Type: Any
- External Type: Client
- RAG System Prompt (Log)
- RAG Service System Prompt
- Tools API Demo Data

## God Nodes (most connected - your core abstractions)
1. `ChatMessage` - 16 edges
2. `main()` - 12 edges
3. `analyze_incident()` - 12 edges
4. `NotificationDispatchError` - 12 edges
5. `dispatch_sms()` - 12 edges
6. `PETER Flow (n8n)` - 12 edges
7. `DataAccessError` - 11 edges
8. `_read_csv_rows()` - 11 edges
9. `build_escalation_preview()` - 11 edges
10. `TriageReport` - 10 edges

## Surprising Connections (you probably didn't know these)
- `PETER PAN Demo Script` --references--> `PETER Flow (n8n)`  [INFERRED]
  docs/presentation/DEMO-SCRIPT.md → n8n/peter-flow.json
- `Presentation Rubric Map` --references--> `E2E Evaluation Script`  [INFERRED]
  docs/presentation/RUBRIC-MAP.md → evaluation/run_e2e.py
- `PETER Flow (n8n)` --references--> `Extractor System Prompt`  [EXTRACTED]
  n8n/peter-flow.json → docs/prompt-log/prompts/surface-1-extractor.systemprompt.txt
- `PETER Flow (n8n)` --references--> `Agent System Message`  [EXTRACTED]
  n8n/peter-flow.json → docs/prompt-log/prompts/surface-2-agent.systemmessage.txt
- `EscalationServiceError` --uses--> `TriageReport`  [INFERRED]
  services/tools-api/tools_api/escalation_service.py → docs/contracts/contracts.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **PETER Orchestration Flow** — n8n_peter_flow, n8n_readme, scripts_bootstrap_n8n_local [EXTRACTED 1.00]
- **Orders API Dependency Chain** — services_rag_corpus_services_orders_api, services_rag_corpus_services_postgres_primary, services_rag_corpus_services_redis_cache, services_rag_corpus_services_payments_api [EXTRACTED 1.00]
- **Prompt Engineering & Validation Framework** — docs_prompt_log_readme, prompts_surface_1_extractor, prompts_surface_2_agent, prompts_surface_3_rag, docs_prompt_log_prompts_surface_4_output_auditor, docs_prompt_log_prompts_surface_4_topic_detection [EXTRACTED 1.00]
- **Stage A Integration & Verification Gate** — docs_audits_2026_07_10_end_to_end_audit, evaluation_run_e2e, docs_presentation_rubric_map [EXTRACTED 0.95]
- **PETER PAN 4-Layer Architecture** — ui_streamlit, n8n_peter_flow, services_ingestion_ingestion_service_app, services_predictor_predictor_service_app, services_rag_rag_service_app, services_guardrails_guardrails_service_app, services_tools_api_tools_api_app, services_langgraph_agent_langgraph_agent_app, services_fixture_llm_fixture_llm_app [EXTRACTED 1.00]
- **Incident Triage Knowledge Base** — services_rag_corpus_incidents_orders_api_deploy_incident, services_rag_corpus_runbooks_orders_api_error_spike, services_rag_rag_service_prompts_surface_3_rag_systemprompt [INFERRED 0.80]
- **Layer 3 Core Services** — services_rag_rag_service_app, services_predictor_predictor_service_app, services_guardrails_guardrails_service_app, services_langgraph_agent_langgraph_agent_app [EXTRACTED 1.00]

## Communities (100 total, 43 thin omitted)

### Community 0 - "Dashboard Generator Service"
Cohesion: 0.06
Nodes (38): create_dashboard(), DashboardRequest, DashboardResponse, list_scenarios(), Any, BaseModel, Dashboard Generator — fixture-first Grafana POST service (Session A, port 8008)., Bearer-token auth — enforced only when PETER_SERVICES_TOKEN is set. (+30 more)

### Community 1 - "Tools API Service"
Cohesion: 0.10
Nodes (41): The one artifact PETER PAN produces. Output-guardrail-checked before routing., TriageReport, audit(), escalation_preview(), EscalationPreviewRequest, EscalationRequest, EscalationResponse, _ok_or_404() (+33 more)

### Community 2 - "Escalation Service"
Cohesion: 0.08
Nodes (41): _check_files(), _check_schemas(), _load_csv(), _load_json(), main(), Any, format_escalation_messages(), _lines_actions() (+33 more)

### Community 3 - "RAG Retrieval & Generation"
Cohesion: 0.07
Nodes (34): load_seed(), main(), Populate the RAG incident vector store (rubric deliverable).  Seeded and idemp, main(), Manual RAG smoke: real ChromaDB retrieval + real GGUF generation.  NOT part of, build_prompt(), CompletionModel, get_generator() (+26 more)

### Community 4 - "Incident History & Runbooks"
Cohesion: 0.05
Nodes (42): Orders API Deployment Incident (INC-20260610-001), Resolution, Reuse Guidance, Root Cause, Summary, Timeline, Postgres Primary Connection Pool Exhaustion (INC-20260618-002), Resolution (+34 more)

### Community 5 - "Notification Dispatch"
Cohesion: 0.11
Nodes (36): _aws_region(), _boto3_client(), check_sms_account_ready(), check_sms_account_ready_cached(), _check_sms_topic_route(), _check_sms_voice_v2_ready(), _confirmed_sms_subscriptions(), dispatch_email() (+28 more)

### Community 6 - "Predictor Service API"
Cohesion: 0.07
Nodes (33): ADR 0004 — Guardrail result and predictor taxonomy contracts, JSONResponse, RequestValidationError, analyse(), AnalyseRequest, AnalyseResponse, Any, BaseModel (+25 more)

### Community 7 - "UI Library & Shared Contracts"
Cohesion: 0.05
Nodes (50): datetime, Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1 (+42 more)

### Community 8 - "Tools API Data Access"
Cohesion: 0.12
Nodes (34): Known owning teams — lets Guardrails verify an owner_team without a service slug, teams(), DataAccessError, _default_data_dir(), _get_pandas(), load_business_impact(), load_escalation_policies(), load_on_call_schedule() (+26 more)

### Community 9 - "PyTorch Classifier Training"
Cohesion: 0.12
Nodes (29): Module, Random, _build_model(), _load_checkpoint(), load_classifier(), preprocess(), Any, Trained PyTorch classifier serving path (pytorch-predictor skill).  Architectu (+21 more)

### Community 10 - "Ingestion Service"
Cohesion: 0.08
Nodes (28): _build_client(), create_signal(), _forward_to_n8n(), _normalize_service_slug(), Any, AsyncClient, Signal, Ingestion Service — accepts, validates, normalizes and forwards Signals.  BUIL (+20 more)

### Community 11 - "Fixture LLM Service"
Cohesion: 0.14
Nodes (32): End-to-End Audit (2026-07-10), Presentation Rubric Map, E2E Evaluation Script, AWS CloudFormation Template, _agent_evidence(), _agent_sequence(), chat_completions(), ChatCompletionRequest (+24 more)

### Community 12 - "Incident Analysis & Environment Codes"
Cohesion: 0.15
Nodes (26): normalize_environment(), Canonical environment codes and optional aliases for demo datasets and tools., Return canonical environment code; pass through unknown values lowercased., Validate and normalize an environment code.      Returns ``(canonical, None)``, validate_environment(), analyze_incident(), _check_runbook_reference(), _classify_priority() (+18 more)

### Community 13 - "Image Analyzer Service"
Cohesion: 0.09
Nodes (21): Image, analyze_image(), get_model(), FastAPI app for the Image Analyzer microservice (Stage A: ResNet room classifica, Lazy-load model on first request., Bearer-token auth dependency, enforced only when PETER_SERVICES_TOKEN is set., Analyze a property image for room type and condition., require_bearer_token() (+13 more)

### Community 14 - "LangGraph Agent Service"
Cohesion: 0.10
Nodes (24): agent_run(), AgentRunRequest, _build_client(), AsyncClient, BaseModel, LangGraph Agent Service — ``POST /agent/run`` (BUILD_PLAN §3, LangGraph agent r, Factory so tests can monkeypatch in an ``httpx.MockTransport`` client     witho, HTTPAuthorizationCredentials (+16 more)

### Community 15 - "Text Parsing Utilities"
Cohesion: 0.13
Nodes (25): extract_reference_metadata(), _first_meaningful_line(), format_answer_sections(), format_citation_label(), format_citation_preview(), _format_json_alert_preview(), _join_bucket(), _normalize_step_buckets() (+17 more)

### Community 16 - "n8n Bootstrap & Demo Assets"
Cohesion: 0.13
Nodes (25): PETER PAN Demo Script, Prompt Engineering Log README, Surface 1: n8n Information Extractor Log, Surface 2: n8n AI Agent Log, PETER Flow (n8n), n8n Layer 2 Orchestration README, Configuration (never inline in the flow), Flow ↔ diagram mapping (+17 more)

### Community 17 - "Service Context Docs"
Cohesion: 0.08
Nodes (24): K8s Ingress Service Context, Business Impact, Dependencies, Owner, Orders API Service Context, Business Impact, Dependencies, Owner (+16 more)

### Community 18 - "Agent Graph Logic"
Cohesion: 0.25
Nodes (19): AgentState, _auth_headers(), _build_citations(), _build_graph(), _call_rag(), _call_tool(), _categorize_service(), _normalize_escalation_path() (+11 more)

### Community 19 - "LLM Client Protocols"
Cohesion: 0.22
Nodes (13): BedrockLLMClient, build_llm_client(), FixtureLLMClient, GeminiLLMClient, LLMClient, LLMResult, OllamaLLMClient, Any (+5 more)

### Community 20 - "Local TF-IDF Retriever"
Cohesion: 0.16
Nodes (11): get_retriever(), LocalRetriever, Path, Pure-Python TF-IDF + keyword retriever for offline RAG.  Stage A deterministic, Return the top-k chunks ranked by TF-IDF cosine similarity., Cached retriever so the corpus is parsed once per process., A single ranked chunk of a corpus document., Split a markdown document into heading-delimited chunks. (+3 more)

### Community 21 - "Alert Stream Generator"
Cohesion: 0.21
Nodes (15): configure_output(), gen_affected_users(), gen_error_rate(), gen_inter_arrival_seconds(), gen_status(), gen_title(), generate(), main() (+7 more)

### Community 22 - "Demo Data Generator"
Cohesion: 0.22
Nodes (15): configure_output(), consistency_checks(), main(), parse_args(), Namespace, Path, PETER PAN — demo data generator. Produces all CSV/JSON files in data/source wit, write_alerts() (+7 more)

### Community 23 - "Guardrail Rules & Errors"
Cohesion: 0.19
Nodes (12): GuardrailViolation, Exception, Guardrail-specific exceptions.  This service is self-contained and never impor, Raised when a deterministic regex/policy check rejects a request or response., check_operator_guardrails(), Deterministic regex guardrail floor, isolated from the retired legacy applicatio, Return every disallowed-operational-action match found in ``text``., Flag junk/off-topic text that lacks any operational markers. (+4 more)

### Community 25 - "RAG Service Contracts"
Cohesion: 0.19
Nodes (14): Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla (+6 more)

### Community 26 - "Tools API Contracts"
Cohesion: 0.19
Nodes (14): Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla (+6 more)

### Community 27 - "Observability Package"
Cohesion: 0.15
Nodes (10): BaseHTTPMiddleware, LogRecord, configure_logging(), CorrelationMiddleware, default_readiness(), _JsonFormatter, Any, Request (+2 more)

### Community 28 - "Policy Engine Interface"
Cohesion: 0.26
Nodes (13): CheckInputRequest, CheckOutputRequest, BaseModel, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla, The one artifact PETER PAN produces. Output-guardrail-checked before routing., Signal, TriageReport, NoopPolicyEngine (+5 more)

### Community 29 - "KB Corpus Loader"
Cohesion: 0.22
Nodes (12): document_text(), iter_corpus_json_paths(), kb_root(), load_kb_document(), load_kb_manifest(), Any, Path, Load the PETER PAN RAG corpus (JSON documents under ``corpus/``).  Self-contai (+4 more)

### Community 30 - "n8n Hardening Script"
Cohesion: 0.27
Nodes (12): api_base(), api_key(), ensure_retries(), fix_if_left_value(), main(), Harden PETER Stage A workflow via n8n REST API (Cloud or self-hosted).  Fixes:, Write TriageReport stores system text under messages.messageValues[].message., Export-safe copy: keep structure, drop active credential ids if present. (+4 more)

### Community 31 - "Canonical Contracts"
Cohesion: 0.23
Nodes (11): DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla, Output of the n8n context-enrichment branches (nodes MW/DEP/CMP → merge). (+3 more)

### Community 32 - "RAG Query API"
Cohesion: 0.24
Nodes (10): Citation, BaseModel, query(), QueryRequest, QueryResponse, FastAPI app for the RAG microservice.  Retrieval backends (``PETER_VECTOR_BACK, Bearer-token auth dependency, enforced only when PETER_SERVICES_TOKEN is set., Backend-selected retrieval; chroma degrades to TF-IDF when unavailable     (mis (+2 more)

### Community 33 - "RAG Query Validation"
Cohesion: 0.20
Nodes (9): Exception, QueryValidationError, Domain errors for the RAG service.  This service no longer calls Bedrock direc, Raised when an incoming /query question fails validation.      Carries a ``cod, Pure question validation for the RAG /query endpoint.  Operator/destructive-ac, Extract searchable tokens (length > 1, not stopwords)., Return the trimmed question or raise QueryValidationError with a stable code., tokenize() (+1 more)

### Community 34 - "Guardrails Service"
Cohesion: 0.22
Nodes (8): _build_http_client(), get_http_client(), AsyncClient, FastAPI app for the Guardrails microservice (BUILD_PLAN §3, GRD row).  Two end, Bearer-token auth gate — only enforced when PETER_SERVICES_TOKEN is set., Yield the shared outbound httpx client — overridden in tests with a     MockTra, require_auth(), Guardrails microservice — deterministic input/output floor (BUILD_PLAN §3, GRD r

### Community 35 - "Guardrails Contracts"
Cohesion: 0.25
Nodes (10): Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Output of the n8n context-enrichment branches (nodes MW/DEP/CMP → merge). (+2 more)

### Community 36 - "Integration Stubs Service"
Cohesion: 0.35
Nodes (9): _check_delivery_auth(), clear_deliveries(), deliveries(), github_deployments(), Any, Local fixtures for GitHub, Slack, and team webhooks — zero external egress., review_queue(), slack_stub() (+1 more)

### Community 37 - "Test Suite Runner"
Cohesion: 0.33
Nodes (8): _has_pytest_suite(), _iter_suites(), main(), Path, Run every test suite from its own rootdir (BUILD_PLAN §2).  Each services/<nam, Return True if *p* looks like a pytest suite (pytest.ini or tests/ dir present)., Return ordered list of directories to run pytest in.      Services come first, Run all discovered suites; return 0 on full success, 1 on any failure.

### Community 38 - "Guardrail Check Logic"
Cohesion: 0.36
Nodes (8): GuardrailResult, _bounded_reason(), check_input(), check_output(), _validation_reason(), find_destructive_steps(), Return the subset of ``steps`` that contain a disallowed destructive command., ValidationError

### Community 39 - "AWS Demo Deployment README"
Cohesion: 0.29
Nodes (7): AWS Demo Deployment README, Deploy, PETER PAN — AWS demo deployment, Security notes, Sizing, Teardown, Validate locally

### Community 40 - "CloudFormation Validation (sh)"
Cohesion: 0.60
Nodes (5): fail(), header(), pass(), validate-cfn.sh script, warn()

### Community 41 - "Owner Verification"
Cohesion: 0.40
Nodes (5): _auth_headers(), AsyncClient, Owner-team verification against the Tools API — fail-closed by design., Return True when owner_team is confirmed via Tools API.      When ``service``, verify_owner_team()

### Community 42 - "Ingress 5xx Runbook"
Cohesion: 0.33
Nodes (6): K8s Ingress 5xx Troubleshooting Runbook, Escalation, Investigation Steps (read-only), Remediation, Triage Decision Tree, Verification

### Community 43 - "Layer 3 Audit (2026-07-13)"
Cohesion: 0.40
Nodes (4): Doc discrepancies noted (not fixed here), Gaps vs Session A targets, PETER PAN — Session A Layer 3 Audit (2026-07-13), Service inventory

### Community 46 - "EC2 Provisioning Script"
Cohesion: 0.67
Nodes (3): log(), MSYS_NO_PATHCONV, provision_ec2.sh script

## Knowledge Gaps
- **105 isolated node(s):** `Service inventory`, `Gaps vs Session A targets`, `Doc discrepancies noted (not fixed here)`, `MSYS_NO_PATHCONV`, `remote_deploy_ec2.sh script` (+100 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **43 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `PETER Flow (n8n)` connect `n8n Bootstrap & Demo Assets` to `RAG Query API`, `Tools API Service`, `Guardrails Service`, `Predictor Service API`, `UI Library & Shared Contracts`, `Ingestion Service`, `LangGraph Agent Service`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Why does `DashboardValidationError` connect `Dashboard Generator Service` to `Escalation Service`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **What connects `Service inventory`, `Gaps vs Session A targets`, `Doc discrepancies noted (not fixed here)` to the rest of the system?**
  _105 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Dashboard Generator Service` be split into smaller, more focused modules?**
  _Cohesion score 0.05844155844155844 - nodes in this community are weakly interconnected._
- **Should `Tools API Service` be split into smaller, more focused modules?**
  _Cohesion score 0.10253699788583509 - nodes in this community are weakly interconnected._
- **Should `Escalation Service` be split into smaller, more focused modules?**
  _Cohesion score 0.07610993657505286 - nodes in this community are weakly interconnected._
- **Should `RAG Retrieval & Generation` be split into smaller, more focused modules?**
  _Cohesion score 0.06976744186046512 - nodes in this community are weakly interconnected._