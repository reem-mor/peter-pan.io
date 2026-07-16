# Graph Report - peter-pan.io  (2026-07-16)

## Corpus Check
- 293 files · ~146,994 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2458 nodes · 3570 edges · 192 communities (152 shown, 40 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 299 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b3cd7c61`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- escalation_service.py
- notification_dispatch.py
- generate_alert_stream.py
- graph.py
- data_access.py
- bootstrap_n8n_local.py
- test_signals.py
- vector_rag.py
- incident_analysis.py
- PETER PAN — Layer 3 Spec-Compliance Matrix
- text_utils.py
- Layer 2 Validation Report — PETER PAN
- Path
- test_run_e2e.py
- app.py
- test_app.py
- llm_client.py
- generator.py
- test_observability.py
- PETER PAN — 5–7 Minute Demo Script
- run_e2e.py
- contracts.py
- test_graph.py
- What You Must Do When Invoked
- test_fixture_llm.py
- deny
- datetime
- PETER PAN — Documentation Reconciliation & Fix Report
- PETER PAN — Final Project Plan & Guideline Crosswalk
- test_rag.py
- PETER PAN — End-to-End Project Document
- _params
- rules.py
- app.py
- _make_signal
- Security — PETER PAN
- _connected_to
- PETER PAN — Master Requirements & Build Checklist
- test_owner_check.py
- kb_corpus.py
- app.py
- app.py
- CLAUDE.md — PETER PAN
- Surface 1: n8n Information Extractor (Node 4) — systemPromptTemplate
- validate_question
- test_app.py
- test_safety_boundaries.py
- PETER PAN — Build Plan
- PETER PAN — Implementation Checklist (Course Spec Audit)
- _tools_api_client
- generate_demo_data.py
- grafana_client.py
- validator.py
- PermissivePolicyEngine
- test_analyse.py
- SubmissionResult
- README.md
- test_app.py
- contracts.py
- contracts.py
- LocalRetriever
- BUILD_PLAN.md
- TestNoEmbeddedSecrets
- app.py
- score
- API Reference — PETER PAN
- Testing — PETER PAN
- harden_stage_a_n8n.py
- chat_sync
- contracts.py
- app.py
- test_check_input.py
- test_torch_classifier.py
- local_rag.py
- test_smoke.py
- Guardrails Testing
- Incident Triage
- AWS Deployment — PETER PAN
- Local Development — PETER PAN
- test_bootstrap_config.py
- GrafanaClient
- graphify reference: extra exports and benchmark
- RAG Evaluation & Grounding
- Grafana Dashboard JSON — Generation Rules
- PETER PAN — End-to-End Audit (2026-07-10)
- PETER PAN — Model, Memory & Database Decisions
- TestFlowMetadata
- TestGuardrailBranches
- TestFourRouteDestinations
- _iter_suites
- fixtures_loader.py
- _run_classifier
- Prompt Engineering Log
- RAG Pipeline Internals — Service 1
- test_flow_static.py
- TestReviewRoute
- TestClient
- test_classifier.py
- TestCheckHealth
- PETER PAN — EC2 demo deployment
- PETER PAN MCP Integration
- AWS Deployment — PETER PAN
- FastAPI Service Conventions
- n8n Flow Conventions — PETER PAN Triage Pipeline
- Observability & Incidents — Domain Truth
- PyTorch Predictor — ML/DL Rules
- Decision
- Agent tooling — PETER PAN
- Setup — PETER PAN
- test_prompt_surfaces.py
- PETER PAN — Agentic incident-response platform
- Orders API Deployment Incident — INC-20260610-001
- Postgres Primary Connection Pool Exhaustion — INC-20260618-002
- Redis Cache Degradation — INC-20260625-003
- Database Connectivity Runbook
- Deployment Rollback Runbook
- K8s Ingress 5xx Troubleshooting Runbook
- Orders API Error Spike Runbook
- Redis Cache Degradation Runbook
- graphify reference: query, path, explain
- PETER PAN Evaluation
- Demo Script Guard (days 9–12)
- Prompt Engineering Log — Required Format (25% of grade)
- Streamlit UI — Professional Demo Standards
- pull_request_template.md
- PETER PAN — AWS demo deployment
- validate-cfn.sh script
- TestEnvVarReferences
- test_nonfinite.py
- Caveman Explainer
- PETER PAN — Session A Layer 3 Audit (2026-07-13)
- request_validation_error
- n8n — Layer 2 orchestration (the PETER flow)
- Reconciliation Steps 4–5
- K8s Ingress Service Context
- Orders API Service Context
- Payments API Service Context
- Postgres Primary Service Context
- Redis Cache Service Context
- Shop Web Service Context
- AGENTS.md — PETER PAN
- graphify reference: add a URL and watch a folder
- graphify reference: commit hook and native CLAUDE.md integration
- graphify reference: incremental update and cluster-only
- ADR 0004 — Guardrail result and predictor taxonomy contracts
- Presentation Evidence — 2026-07-11
- provision_ec2.sh
- .check_input
- .check_output
- test_contracts_identity.py
- test_data_corpus.py
- test_data_access_cache.py
- SKILL.md
- graphify reference: GitHub clone and cross-repo merge
- graphify reference: transcribe video and audio
- export_json_schema.py
- log
- enable_gguf_ec2.sh
- remote_deploy_ec2.sh
- conftest.py
- test_contracts_identity.py
- test_golden_signals.py
- test_contracts_identity.py
- test_contracts_identity.py
- conftest.py
- test_contracts_identity.py
- conftest.py
- test_contracts_identity.py
- CLAUDE.md
- extraction-spec.md
- LAYER-2-PROPOSED-DELETIONS.md
- conftest.py
- copilot-instructions.md
- __init__.py
- __init__.py
- __init__.py
- __init__.py
- README.md
- __init__.py

## God Nodes (most connected - your core abstractions)
1. `_connected_to()` - 32 edges
2. `_params()` - 31 edges
3. `TestCoreConnections` - 27 edges
4. `Layer 2 Validation Report — PETER PAN` - 24 edges
5. `deny` - 18 edges
6. `dispatch_sms()` - 18 edges
7. `_make_transport()` - 16 edges
8. `ChatMessage` - 16 edges
9. `_tools_api_client()` - 16 edges
10. `DataAccessError` - 15 edges

## Surprising Connections (you probably didn't know these)
- `PermissivePolicyEngine` --uses--> `Signal`  [INFERRED]
  services/guardrails/tests/test_floor_priority.py → docs/contracts/contracts.py
- `PermissivePolicyEngine` --uses--> `TriageReport`  [INFERRED]
  services/guardrails/tests/test_floor_priority.py → docs/contracts/contracts.py
- `EscalationServiceError` --uses--> `TriageReport`  [INFERRED]
  services/tools-api/tools_api/escalation_service.py → docs/contracts/contracts.py
- `main()` --indirect_call--> `client()`  [INFERRED]
  evaluation/run_e2e.py → services/image-analyzer/tests/test_app.py
- `main()` --calls--> `get_vector_retriever()`  [INFERRED]
  scripts/smoke_rag.py → services/rag/rag_service/vector_rag.py

## Import Cycles
- None detected.

## Communities (192 total, 40 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.05
Nodes (65): The one artifact PETER PAN produces. Output-guardrail-checked before routing., TriageReport, Unit tests for enrichment tools against the canonical data/ demo scenarios., test_correlate_deployments_demo(), test_enrich_triage_demo_bundle(), test_find_similar_incidents_demo(), test_lookup_owner_demo(), test_orders_api_storm_enrichment() (+57 more)

### Community 1 - "escalation_service.py"
Cohesion: 0.05
Nodes (66): Tests for escalation message formatting., test_enrich_escalation_context_fills_owner_from_catalog(), test_format_escalation_email_includes_on_call_and_war_room(), test_format_escalation_sms_is_concise(), TriageReport, Tests for the preview-first escalation service (no Lambda, no dispatch)., _report(), test_build_escalation_preview_never_dispatches() (+58 more)

### Community 2 - "notification_dispatch.py"
Cohesion: 0.08
Nodes (49): Tests for SNS/SES notification dispatch.  Not wired into any Tools API route (, test_check_sms_account_ready_ok(), test_dispatch_sms_can_use_topic_when_enabled(), test_dispatch_sms_falls_back_to_whatsapp_when_sms_blocked(), test_dispatch_sms_preflight_blocks_when_account_not_ready(), test_dispatch_sms_stays_direct_when_topic_subscriber_confirmed(), test_dispatch_sms_uses_direct_phone_by_default(), test_dispatch_sms_uses_voice_v2_by_default() (+41 more)

### Community 3 - "generate_alert_stream.py"
Cohesion: 0.07
Nodes (44): Module, configure_output(), gen_affected_users(), gen_error_rate(), gen_inter_arrival_seconds(), gen_status(), gen_title(), generate() (+36 more)

### Community 4 - "graph.py"
Cohesion: 0.08
Nodes (43): agent_run(), AgentRunRequest, _build_client(), AsyncClient, BaseModel, LangGraph Agent Service — ``POST /agent/run`` (BUILD_PLAN §3, LangGraph agent r, Factory so tests can monkeypatch in an ``httpx.MockTransport`` client     witho, HTTPAuthorizationCredentials (+35 more)

### Community 5 - "data_access.py"
Cohesion: 0.08
Nodes (37): Tests for the canonical data layer (tools_api/data_access.py)., test_json_wrong_shape_raises(), test_malformed_json_raises(), test_missing_columns_raises(), test_missing_csv_raises(), DataAccessError, _default_data_dir(), _get_pandas() (+29 more)

### Community 6 - "bootstrap_n8n_local.py"
Cohesion: 0.06
Nodes (38): Image, _archive_conflicting_peter_workflows(), _credential_id(), _ensure_owner(), _find_workflow(), main(), _patch_and_activate(), _publish_workflow() (+30 more)

### Community 7 - "test_signals.py"
Cohesion: 0.06
Nodes (38): _build_client(), create_signal(), _forward_to_n8n(), _normalize_service_slug(), Any, AsyncClient, Signal, Ingestion Service — accepts, validates, normalizes and forwards Signals.  BUIL (+30 more)

### Community 8 - "vector_rag.py"
Cohesion: 0.08
Nodes (33): load_seed(), main(), Populate the RAG incident vector store (rubric deliverable).  Seeded and idemp, _build_retriever(), chroma_path(), ChromaRetriever, Embedder, embedding_model_matches() (+25 more)

### Community 9 - "incident_analysis.py"
Cohesion: 0.10
Nodes (35): Environment code normalization and validation., test_normalize_environment(), test_validate_accepts_aliases(), test_validate_accepts_canonical_codes(), test_validate_rejects_unknown_environment(), Integration tests for structured incident analysis (data/ + runbooks manifest)., test_orders_api_production_p1_full_flow(), test_priority_raises_p3_to_p2_on_revenue() (+27 more)

### Community 10 - "PETER PAN — Layer 3 Spec-Compliance Matrix"
Cohesion: 0.06
Nodes (33): §4.1 — RAG Service (`:8003`), §4.2 — Image Analyzer (`:8007`) — status only (Alex ruling), §4.2 — Predictor (`:8002`) *(crosswalk of Image Analyser)*, §4.3 — Guardrails (`:8004`), §4.4 — LangGraph Agent (`:8006`), §4 cross-cutting, §6 — Prompt Log scoreboard (5 surfaces), §7 — Deliverables inventory (Layer-3 items, status-only) (+25 more)

### Community 11 - "text_utils.py"
Cohesion: 0.10
Nodes (33): Tests for answer/citation formatting helpers., test_extract_reference_metadata_score_and_chunk(), test_format_answer_sections_derives_steps_from_plain_text(), test_format_answer_sections_inline_numbered_and_escalation(), test_format_answer_sections_parses_headings(), test_format_answer_sections_parses_structured_headings(), test_format_citation_preview_markdown_heading(), test_format_citation_preview_parses_json_alert() (+25 more)

### Community 12 - "Layer 2 Validation Report — PETER PAN"
Cohesion: 0.06
Nodes (32): 10. API test results (sanitized), 11. Playwright results, 12. EC2 service results, 13. Guardrail results, 14. RAG evaluation results, 15. Predictor decision, 16. Image Analyzer decision, 17. LangGraph / LangChain decision (+24 more)

### Community 13 - "Path"
Cohesion: 0.14
Nodes (9): CaptureFixture, _make_service(), _make_subprocess_result(), _make_suite(), Path, TDD tests for scripts/run_all_tests.py.  Tests the NEW behaviour: extending se, TestHasPytestSuite, TestIterSuites (+1 more)

### Community 14 - "test_run_e2e.py"
Cohesion: 0.13
Nodes (22): _client_factory(), _fast_monotonic(), _json_resp(), _make_transport(), Any, Response, Unit tests for evaluation/run_e2e.py.  Strategy: inject an httpx.Client backed, Build a MockTransport from ``{(METHOD, url_prefix): response_or_callable}``. (+14 more)

### Community 15 - "app.py"
Cohesion: 0.17
Nodes (28): _agent_evidence(), _agent_sequence(), chat_completions(), ChatCompletionRequest, ChatMessage, _commander_evidence(), _detect_task(), _extract_response() (+20 more)

### Community 16 - "test_app.py"
Cohesion: 0.08
Nodes (18): _isolated_audit_db(), FastAPI route tests for the Tools API service., Point every test at its own throwaway audit DB (never the repo's)., There must be no DELETE/PATCH route on /audit (immutable log)., GET /audit must return at most 50 entries even if more exist., Audit log must be ordered newest-first (DESC created_at)., Every audit entry must have dispatched=False (preview-only service)., POST /escalations preview=True must never invoke notification_dispatch. (+10 more)

### Community 17 - "llm_client.py"
Cohesion: 0.12
Nodes (22): BedrockLLMClient, build_llm_client(), FixtureLLMClient, GeminiLLMClient, LLMClient, LLMResult, OllamaLLMClient, Any (+14 more)

### Community 18 - "generator.py"
Cohesion: 0.11
Nodes (23): main(), Manual RAG smoke: real ChromaDB retrieval + real GGUF generation.  NOT part of, build_prompt(), CompletionModel, get_generator(), LlamaGenerator, _load(), Any (+15 more)

### Community 19 - "test_observability.py"
Cohesion: 0.09
Nodes (18): BaseHTTPMiddleware, LogRecord, configure_logging(), CorrelationMiddleware, default_readiness(), _JsonFormatter, Any, Request (+10 more)

### Community 20 - "PETER PAN — 5–7 Minute Demo Script"
Cohesion: 0.07
Nodes (25): 1. Context (30s), 2. Assistant tab (1 min), 3. Incident submission (3 min), 4. Guardrail rejection (1 min), 5. Architecture callout (1 min), 6. Evidence (30s), Architecture (submission diagram), Demo Guide — PETER PAN (+17 more)

### Community 21 - "run_e2e.py"
Cohesion: 0.18
Nodes (27): _check_health(), _find_triage_delivery(), _headers(), _incident_from_signal(), _layer3_source_hash(), _load_contracts(), _load_golden(), _looks_like_triage_report() (+19 more)

### Community 22 - "contracts.py"
Cohesion: 0.14
Nodes (25): CheckInputRequest, CheckOutputRequest, BaseModel, Citation, DeployRef, GuardrailResult, Incident, IncidentContext (+17 more)

### Community 23 - "test_graph.py"
Cohesion: 0.15
Nodes (22): _everything_down_handler(), _healthy_handler(), _patch_client(), Request, Response, P1 vs P3 fixture incidents walk expected paths (BUILD_PLAN §3, LangGraph agent, redis-* service names must route to the infra category., k8s-* / ingress service names must route to the infra category. (+14 more)

### Community 24 - "What You Must Do When Invoked"
Cohesion: 0.08
Nodes (24): For /graphify add and --watch, For /graphify query, For the commit hook and native CLAUDE.md integration, For --update and --cluster-only, /graphify, Honesty Rules, Interpreter guard for subcommands, Part A - Structural extraction for code files (+16 more)

### Community 25 - "test_fixture_llm.py"
Cohesion: 0.09
Nodes (7): _commander_request(), Tests for Fixture LLM OpenAI-compatible seam., The 6→3 mapping lives only in the n8n flow — the fixture must copy     predicto, test_commander_calls_simple_incident_tools_then_returns_evidence(), test_commander_uses_langgraph_without_direct_rag_for_complex_infra(), test_tool_grounded_synthesis_requires_flow_routing_category(), _tool_roundtrip()

### Community 26 - "deny"
Cohesion: 0.09
Nodes (22): hooks, PreToolUse, permissions, deny, $schema, Bash(aws ec2 terminate-instances:*), Bash(aws s3 rb:*), Bash(aws s3 rm:*) (+14 more)

### Community 27 - "datetime"
Cohesion: 0.12
Nodes (18): datetime, _handle_submission(), Any, Signal, PETER PAN Layer 1 — Streamlit WebUI.  Two tabs:   - Assistant: grounded SRE c, Render webhook outcome and update review queue when flagged., Structured TriageReport blocks (metrics + citations + steps)., _render_guardrail_card() (+10 more)

### Community 28 - "PETER PAN — Documentation Reconciliation & Fix Report"
Cohesion: 0.09
Nodes (22): 0. How to use this, 1. Severity summary, 2. DELETE — duplicate / superseded files, 3. FIX — conflicts, ranked, 4. IMPROVE, 5. Decisions you must make (before the fix pass), 6. File-by-file verdict (navigation), 7. Recommended execution order (+14 more)

### Community 29 - "PETER PAN — Final Project Plan & Guideline Crosswalk"
Cohesion: 0.09
Nodes (23): 10 · Build order & milestones, 11 · Optional extensions (guideline §10) — all four planned, 12 · Deployment & security (guideline §11), 13 · Top risks & mitigations (abridged — full register in BUILD_PLAN §5), 1 · Executive summary, 2 · Domain translation — the crosswalk dictionary, 3 · Learning objectives coverage (guideline §1.2), 4 · Architecture at a glance (+15 more)

### Community 30 - "test_rag.py"
Cohesion: 0.10
Nodes (15): get_retriever(), Cached retriever so the corpus is parsed once per process., Tests for the offline TF-IDF retriever and the /query endpoint.  Replaces the, The MIN_SCORE filter must exclude sub-threshold chunks from every result., Nonsense token strings have no corpus overlap → empty hit list., When the retriever produces no hits, /query must refuse (never guess)., Verify the complete refused-response contract shape., test_refusal_response_has_correct_contract_shape() (+7 more)

### Community 31 - "PETER PAN — End-to-End Project Document"
Cohesion: 0.09
Nodes (21): 1. The Idea in One Sentence (for the lecturer), 2. Crosswalk Table — Course Requirements vs. My Implementation, 3. The Architecture — Layer by Layer, 4. Prompt Engineering Log — 25% of the Grade (!), 5. Deliverables — Submission Checklist, 6. Rubric Mapping, 7. 12-Day Plan, 8. Cursor Skills — What to Add and Why, by Phase (+13 more)

### Community 32 - "_params"
Cohesion: 0.12
Nodes (4): _params(), Internal service call nodes (guardrails, predictor, rag, langgraph) also bear au, TestBearerAuthOnDeliveryNodes, TestTriageReportSchema

### Community 33 - "rules.py"
Cohesion: 0.16
Nodes (18): GuardrailViolation, Exception, Guardrail-specific exceptions.  This service is self-contained and never impor, Raised when a deterministic regex/policy check rejects a request or response., check_operator_guardrails(), Deterministic regex guardrail floor, isolated from the retired legacy applicatio, Return every disallowed-operational-action match found in ``text``., Flag junk/off-topic text that lacks any operational markers. (+10 more)

### Community 34 - "app.py"
Cohesion: 0.13
Nodes (10): _check_delivery_auth(), clear_deliveries(), deliveries(), github_deployments(), Any, Local fixtures for GitHub, Slack, and team webhooks — zero external egress., review_queue(), slack_stub() (+2 more)

### Community 35 - "_make_signal"
Cohesion: 0.18
Nodes (8): POST a validated Signal JSON to the n8n webhook.      Returns a SubmissionResu, submit_signal(), _make_signal(), _mock_response(), Signal, Payload sent to webhook must satisfy Signal contract., TestSignalModel, TestSubmitSignal

### Community 36 - "Security — PETER PAN"
Cohesion: 0.10
Nodes (19): 1. Skills / tooling cleanup (tooling-only, no product code), 2. Security / residue pass (surgical remediation — accepted), 3. Kaggle finding — reclassified as FALSE POSITIVE, 4. Public-release gate — ALL must be checked before `--public`, Appendix — history purge (ONLY if §3 finds a real literal token), Pre-Public Checklist — PETER PAN, Containers, Cursor rules (+11 more)

### Community 37 - "_connected_to"
Cohesion: 0.17
Nodes (3): _connected_to(), Return names of nodes connected from source at main[output_slot]., TestCoreConnections

### Community 38 - "PETER PAN — Master Requirements & Build Checklist"
Cohesion: 0.10
Nodes (19): 0. How to drive this with Cursor + Claude Code, 10. Optional extensions (extra credit) — PETER PAN native coverage, 11. Declared deviations (state to Alex upfront), 12. Two-week build order (T1 = rubric/demo-critical), 13. Pre-submission final gate, 1. Rubric = your priority map (100%), 2. Requirement crosswalk (guideline → PETER PAN), 3. The four layers (+11 more)

### Community 39 - "test_owner_check.py"
Cohesion: 0.21
Nodes (17): _auth_headers(), AsyncClient, Owner-team verification against the Tools API — fail-closed by design., Return True when owner_team is confirmed via Tools API.      When ``service``, verify_owner_team(), Unit tests for owner_check.verify_owner_team — fail-closed on every edge case., _run(), test_returns_false_on_error_body() (+9 more)

### Community 40 - "kb_corpus.py"
Cohesion: 0.17
Nodes (16): document_text(), iter_corpus_json_paths(), kb_root(), load_kb_document(), load_kb_manifest(), Any, Path, Load the PETER PAN RAG corpus (JSON documents under ``corpus/``).  Self-contai (+8 more)

### Community 41 - "app.py"
Cohesion: 0.16
Nodes (16): GuardrailResult, _bounded_reason(), _build_http_client(), check_input(), check_output(), get_http_client(), AsyncClient, FastAPI app for the Guardrails microservice (BUILD_PLAN §3, GRD row).  Two end (+8 more)

### Community 42 - "app.py"
Cohesion: 0.15
Nodes (14): analyse(), AnalyseRequest, AnalyseResponse, BaseModel, Predictor Service — anomaly-detection floor (BUILD_PLAN §3, Predictive Engine r, HTTPAuthorizationCredentials, Shared bearer-auth dependency for non-health routes.  Vendored per-service (AG, require_bearer_token() (+6 more)

### Community 43 - "CLAUDE.md — PETER PAN"
Cohesion: 0.11
Nodes (18): 1. Think before coding, 2. Simplicity first, 3. Surgical changes, 4. Goal-driven execution, Canonical project references, CLAUDE.md — PETER PAN, Declared deviations (state upfront, never hide), Definition of done (per change) (+10 more)

### Community 44 - "Surface 1: n8n Information Extractor (Node 4) — systemPromptTemplate"
Cohesion: 0.11
Nodes (15): Honesty rules (from the skill — binding), Layout, Prompt Engineering Log — PETER PAN, Surfaces, Final, Surface 1: n8n Information Extractor (Node 4) — systemPromptTemplate, Test suite, V1 — Baseline (+7 more)

### Community 45 - "validate_question"
Cohesion: 0.19
Nodes (14): Exception, QueryValidationError, Domain errors for the RAG service.  This service no longer calls Bedrock direc, Raised when an incoming /query question fails validation.      Carries a ``cod, Pure question validation for the RAG /query endpoint.  Operator/destructive-ac, Return the trimmed question or raise QueryValidationError with a stable code., validate_question(), Tests for shared question validation. (+6 more)

### Community 46 - "test_app.py"
Cohesion: 0.18
Nodes (16): AppTest, at(), MonkeyPatch, PETER PAN Layer 1 UI tests.  Two test classes:   - Unit tests for ``lib.py``, AppTest with all external URLs cleared — no network I/O during tests., Off-topic keywords must return the refusal string without any LLM call., On-topic query with no LLM backends shows graceful error, not crash., After an off-topic exchange, clearing resets session messages. (+8 more)

### Community 47 - "test_safety_boundaries.py"
Cohesion: 0.12
Nodes (15): Guardrails safety-boundary tests (BUILD_PLAN A3, GRD row).  Covers: - Prompt-, Unicode, Hebrew, emoji titles must not raise and must return valid JSON., A body at the schema maximum (8000 chars) with no blocked content must pass., A body of 8001 chars must be rejected at schema validation level., severity_hint is optional (default None); explicitly passing null must pass., FPR must be 0%: none of the 15 clearly-safe operational signals should be blocke, Prompt-injection payloads must return a structured 200, never 500., Injections that embed a blocked keyword (FLUSHALL, DROP TABLE) must be flagged. (+7 more)

### Community 48 - "PETER PAN — Build Plan"
Cohesion: 0.12
Nodes (16): 1 · Contracts first, 2 · Packaging decision, 3 · Component inventory (mapped to diagram nodes), 4 · Stages, 5 · Risk register (top 5), 6 · Effort honesty (> 2–3 sessions flagged), 7 · Conflicts (listed, not silently resolved), Knowledge & Comms seams (`KNOW`/`HUM`) (+8 more)

### Community 49 - "PETER PAN — Implementation Checklist (Course Spec Audit)"
Cohesion: 0.12
Nodes (16): Guardrails (`:8004`), Image Analyser → **Predictor** (`:8002`), LangGraph Agent (`:8006`), PETER PAN — Implementation Checklist (Course Spec Audit), Phase 10 — Documentation, Phase 1 — Repository Audit, Phase 2 — Local Development, Phase 3 — Required Services (Course §4 crosswalk) (+8 more)

### Community 50 - "_tools_api_client"
Cohesion: 0.22
Nodes (15): Handler, POST /check/output — the plan's output-check table (BUILD_PLAN §3, GRD row): in, Override get_http_client with an httpx.MockTransport-backed client., test_destructive_step_fails(), test_existing_report_flags_fail_closed(), test_invented_owner_fails_closed(), test_missing_tools_url_fails_closed(), test_predictor_severity_mismatch_fails_closed() (+7 more)

### Community 51 - "generate_demo_data.py"
Cohesion: 0.22
Nodes (15): configure_output(), consistency_checks(), main(), parse_args(), Namespace, Path, PETER PAN — demo data generator. Produces all CSV/JSON files in data/source wit, write_alerts() (+7 more)

### Community 52 - "grafana_client.py"
Cohesion: 0.18
Nodes (13): _fetch_prometheus_uid(), get_grafana_client(), GrafanaPoster, Protocol, Grafana HTTP client — datasource UID resolved once at startup., Cached client; fixture mode when GRAFANA_API_TOKEN is unset., reset_client_cache(), Grafana client tests (fixture mode — no network). (+5 more)

### Community 53 - "validator.py"
Cohesion: 0.22
Nodes (14): assert_valid_dashboard(), _extract_metric_tokens(), _metric_allowed(), _panel_rect(), Any, Validate Grafana dashboard JSON before any POST (grafana-dashboard-json skill)., Return a list of validation errors (empty = valid)., _rects_overlap() (+6 more)

### Community 54 - "PermissivePolicyEngine"
Cohesion: 0.16
Nodes (12): _golden_valid_signals(), permissive_engine(), PermissivePolicyEngine, Any, MonkeyPatch, Signal, TriageReport, Floor-priority proof + false-positive rate on the golden valid alerts.  Two Se (+4 more)

### Community 55 - "test_analyse.py"
Cohesion: 0.12
Nodes (3): POST /analyse tests for the typed six-class response (BUILD_PLAN §3, Predictor, Pin the fixed-weight stub for tests asserting stub-specific     window-shape be, _stub_engine()

### Community 56 - "SubmissionResult"
Cohesion: 0.17
Nodes (11): is_off_topic(), new_sig_id(), BaseModel, Return True if the query contains an off-topic keyword., Generate a valid Signal ID: ``sig-<12 lowercase hex chars>``., Minimal UI vendor of the canonical Signal contract., Result of a webhook submission attempt., Signal (+3 more)

### Community 57 - "README.md"
Cohesion: 0.15
Nodes (6): Documented limitations, Executive summary, Fixes applied during this pass, How to re-verify, Local Layer 1→3→2→4 Validation Report, Pass / fail matrix

### Community 58 - "test_app.py"
Cohesion: 0.14
Nodes (6): FixtureGrafanaClient, Test double — validates and returns a synthetic success body., _fixture_grafana(), MonkeyPatch, HTTP tests for the Dashboard Generator service., test_fixture_grafana_substitutes_datasource_uid()

### Community 59 - "contracts.py"
Cohesion: 0.19
Nodes (14): Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla (+6 more)

### Community 60 - "contracts.py"
Cohesion: 0.19
Nodes (14): Citation, DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla (+6 more)

### Community 61 - "LocalRetriever"
Cohesion: 0.20
Nodes (8): LocalRetriever, Path, Return the top-k chunks ranked by TF-IDF cosine similarity., A single ranked chunk of a corpus document., TF-IDF retriever over the corpus JSON documents., RetrievedChunk, Extract searchable tokens (length > 1, not stopwords)., tokenize()

### Community 62 - "BUILD_PLAN.md"
Cohesion: 0.23
Nodes (5): PETER PAN - AI Incident Operations Platform, ADR 0002 — Model routing, memory, and storage decisions, Consequences, Decisions, Architecture

### Community 63 - "TestNoEmbeddedSecrets"
Cohesion: 0.14
Nodes (8): _all_string_values(), Recursively collect all string values from a JSON-like structure., active:false is the primary guard against live webhook registration., No string value in the flow should match a known secret pattern., Integration node URLs must use $env.* expressions, not literal http:// addresses, pinData must be empty — pinned live data can expose real incident PII., LLM model nodes must reference the fixture seam model, not live API model IDs., TestNoEmbeddedSecrets

### Community 64 - "app.py"
Cohesion: 0.20
Nodes (10): create_dashboard(), DashboardRequest, DashboardResponse, list_scenarios(), Any, BaseModel, Dashboard Generator — fixture-first Grafana POST service (Session A, port 8008)., Bearer-token auth — enforced only when PETER_SERVICES_TOKEN is set. (+2 more)

### Community 65 - "score"
Cohesion: 0.22
Nodes (12): Deterministic EWMA (exponentially weighted moving average) anomaly scorer.  St, Score a metric window for anomalies.      Returns ``{"point_scores": [...], "o, Deterministic overall-score -> 1..5 severity mapping. Public so it's     direct, score(), severity_band(), EWMA known-series table (BUILD_PLAN §3, Predictor row): flat series -> low seve, test_empty_window_is_safe(), test_flat_series_is_severity_one_with_zero_score() (+4 more)

### Community 66 - "API Reference — PETER PAN"
Cohesion: 0.15
Nodes (13): API Reference — PETER PAN, Fixture LLM — `POST /v1/chat/completions`, Guardrails, Image Analyzer — `POST /analyze`, Ingestion — `POST /signals`, LangGraph — `POST /agent/run`, OpenAPI, Port map (local compose) (+5 more)

### Community 67 - "Testing — PETER PAN"
Cohesion: 0.15
Nodes (13): CI, Compose syntax, Coverage bars, curl smoke, E2E harness, Health checks, Lint, Per-service pytest (+5 more)

### Community 68 - "harden_stage_a_n8n.py"
Cohesion: 0.27
Nodes (12): api_base(), api_key(), ensure_retries(), fix_if_left_value(), main(), Harden PETER Stage A workflow via n8n REST API (Cloud or self-hosted).  Fixes:, Write TriageReport stores system text under messages.messageValues[].message., Export-safe copy: keep structure, drop active credential ids if present. (+4 more)

### Community 69 - "chat_sync"
Cohesion: 0.21
Nodes (8): call_fixture_llm(), call_ollama(), chat_sync(), POST to an OpenAI-compatible /chat/completions endpoint (fixture LLM)., POST to Ollama /api/chat endpoint., Try fixture LLM; fall back to Ollama.  Raises ``RuntimeError`` if both fail., Empty fixture_url must not attempt any POST to fixture endpoint., TestChatSync

### Community 70 - "contracts.py"
Cohesion: 0.23
Nodes (11): DeployRef, GuardrailResult, Incident, IncidentContext, BaseModel, PETER PAN shared contracts — pydantic v2. Frozen at Stage A start (BUILD_PLAN §1, Anything that enters the system: Grafana alert, WebUI form, deploy event, compla, Output of the n8n context-enrichment branches (nodes MW/DEP/CMP → merge). (+3 more)

### Community 71 - "app.py"
Cohesion: 0.24
Nodes (10): Citation, BaseModel, query(), QueryRequest, QueryResponse, FastAPI app for the RAG microservice.  Retrieval backends (``PETER_VECTOR_BACK, Bearer-token auth dependency, enforced only when PETER_SERVICES_TOKEN is set., Backend-selected retrieval; chroma degrades to TF-IDF when unavailable     (mis (+2 more)

### Community 72 - "test_check_input.py"
Cohesion: 0.17
Nodes (3): POST /check/input — accept/reject table (BUILD_PLAN §3, GRD row)., Ops markers in the text must keep FP rate low even if a food word appears., test_ops_alert_with_food_metaphor_still_passes()

### Community 74 - "local_rag.py"
Cohesion: 0.25
Nodes (9): Pure-Python TF-IDF + keyword retriever for offline RAG.  Stage A deterministic, Split a markdown document into heading-delimited chunks., _split_chunks(), _case_hits(), _load_cases(), Golden-set retrieval evaluation for the BUILD_PLAN §4 exit gate.  Runs each ca, Not a hard gate (see hit-rate test), but surfaces which cases miss., test_each_eval_case_is_individually_traceable() (+1 more)

### Community 76 - "Guardrails Testing"
Cohesion: 0.20
Nodes (9): Adversarial cases to include, Frozen response contract (docs/contracts/contracts.py), Frozen test sets (do NOT mutate mid-iteration), Guardrails Testing, Input rail — what it must catch (`/check/input`), Output rail — what it must block (`/check/output`), Target metric, When editing here (+1 more)

### Community 77 - "Incident Triage"
Cohesion: 0.20
Nodes (9): Idempotency, Incident Triage, Routing (deterministic map, node 8), Severity -> P-level (deterministic, not LLM-decided), The 6 predictor classes (fixed set — never invent new ones), TriageReport contract (FROZEN — matches docs/contracts/contracts.py), Two different taxonomies — do not conflate, When editing here (+1 more)

### Community 78 - "AWS Deployment — PETER PAN"
Cohesion: 0.20
Nodes (10): AWS Deployment — PETER PAN, Deploy application, Enable GGUF (optional Session D), Instance sizing, n8n on EC2, Persistent storage, Post-deploy checks, Provision (CloudFormation) (+2 more)

### Community 79 - "Local Development — PETER PAN"
Cohesion: 0.20
Nodes (10): curl examples, End-to-end harness, Health validation, Local Development — PETER PAN, Playwright smokes (UI + n8n login), Populate ChromaDB (optional, chroma backend), Quick start (one command sequence), Tear down (+2 more)

### Community 80 - "test_bootstrap_config.py"
Cohesion: 0.29
Nodes (6): _load_bootstrap(), Fail-fast configuration checks for the privileged local n8n bootstrap., test_owner_password_is_required_before_network_access(), test_publish_workflow_uses_authenticated_rest_version(), test_service_token_is_required_before_network_access(), test_webhook_secret_is_required_before_network_access()

### Community 81 - "GrafanaClient"
Cohesion: 0.29
Nodes (3): GrafanaClient, Any, POST /api/dashboards/db with Bearer auth.

### Community 82 - "graphify reference: extra exports and benchmark"
Cohesion: 0.22
Nodes (8): graphify reference: extra exports and benchmark, Step 6b - Wiki (only if --wiki flag), Step 7 - Neo4j export (only if --neo4j or --neo4j-push flag), Step 7a - FalkorDB export (only if --falkordb or --falkordb-push flag), Step 7b - SVG export (only if --svg flag), Step 7c - GraphML export (only if --graphml flag), Step 7d - MCP server (only if --mcp flag), Step 8 - Token reduction benchmark (only if total_words > 5000)

### Community 83 - "RAG Evaluation & Grounding"
Cohesion: 0.22
Nodes (8): Corpus discipline, Frozen eval set (10 queries), Metrics to persist, RAG Evaluation & Grounding, Retrieval safety floor (deterministic), The grounding contract, Vector store adapters, When editing here

### Community 84 - "Grafana Dashboard JSON — Generation Rules"
Cohesion: 0.22
Nodes (8): Golden rules, Grafana Dashboard JSON — Generation Rules, Grafana HTTP API, Layout rules, Minimal valid dashboard (the template — extend, don't replace), Panel selection by incident_class (guidance for the LLM prompt), Panel template (timeseries — the default panel type), What NOT to do

### Community 85 - "PETER PAN — End-to-End Audit (2026-07-10)"
Cohesion: 0.22
Nodes (8): Baseline QA (pre-hardening), Decision log, File disposition manifest, Open risks, PETER PAN — End-to-End Audit (2026-07-10), Post-hardening verification (2026-07-11), Remaining rubric gaps, Understanding lock (confirmed)

### Community 86 - "PETER PAN — Model, Memory & Database Decisions"
Cohesion: 0.22
Nodes (8): 1 · Model routing — why three tiers, not one, 2 · Memory — where it belongs and where it must NOT, 3 · Database / vector store — two stores, two jobs, 4 · Summary — the mental model to present, PETER PAN — Model, Memory & Database Decisions, The reasoning behind every AI/data choice in the n8n flow (for Alex), Why Bedrock remains an optional Stage C reasoning provider, Why NOT the uploaded workflow's choices

### Community 90 - "_iter_suites"
Cohesion: 0.33
Nodes (8): _has_pytest_suite(), _iter_suites(), main(), Path, Run every test suite from its own rootdir (BUILD_PLAN §2).  Each services/<nam, Return True if *p* looks like a pytest suite (pytest.ini or tests/ dir present)., Return ordered list of directories to run pytest in.      Services come first, Run all discovered suites; return 0 on full success, 1 on any failure.

### Community 91 - "fixtures_loader.py"
Cohesion: 0.28
Nodes (8): allowed_metric_names(), load_fixture(), metrics_catalog(), Any, Path, Load committed dashboard fixtures and the metrics catalog., Repo-root fixtures (dev), service-tree copy (pytest), or image COPY target., _resolve_fixtures_dir()

### Community 92 - "_run_classifier"
Cohesion: 0.28
Nodes (8): Any, Tiered classification: context markers -> trained model -> stub., _run_classifier(), match_context(), predict(), PyTorch-free classifier stub (Stage A fixture, BUILD_PLAN §3 Predictor row)., Deterministic incident-class from explicit metric/symptom markers, or     ``Non, Return a deterministic six-class fixture prediction.

### Community 93 - "Prompt Engineering Log"
Cohesion: 0.25
Nodes (7): Anti-patterns (will cost marks), Output, Prompt Engineering Log, Required format per surface (this exact shape is graded), Rules, The five surfaces (all required), When editing here

### Community 94 - "RAG Pipeline Internals — Service 1"
Cohesion: 0.25
Nodes (7): ChromaDB, Embedder, Llama.cpp inference, Pre-population (rubric deliverable: script + 20+ records), RAG Pipeline Internals — Service 1, Tests (fixture-first, no live model in CI), The retrieval prompt (prompt surface #3 — versioned file)

### Community 97 - "TestClient"
Cohesion: 0.39
Nodes (7): Bearer auth dependency — only enforced when PETER_SERVICES_TOKEN is set., test_accepts_correct_bearer_token_when_configured(), test_healthz_never_requires_auth(), test_no_auth_required_when_token_unset(), test_rejects_missing_bearer_token_when_configured(), test_rejects_wrong_bearer_token_when_configured(), TestClient

### Community 99 - "TestCheckHealth"
Cohesion: 0.39
Nodes (3): check_health(), Probe a /healthz endpoint.      Returns ``(status, detail)`` where status is o, TestCheckHealth

### Community 100 - "PETER PAN — EC2 demo deployment"
Cohesion: 0.29
Nodes (6): Compose files, Invariants, Known traps, n8n owner recovery (lost password / lost .env), PETER PAN — EC2 demo deployment, Standard sequence

### Community 101 - "PETER PAN MCP Integration"
Cohesion: 0.29
Nodes (6): Configuration pattern, PETER PAN MCP Integration, Repository defaults, Source of truth, Verification, Workflow

### Community 102 - "AWS Deployment — PETER PAN"
Cohesion: 0.29
Nodes (6): Audit-first rule for ANY aws CLI call, AWS Deployment — PETER PAN, Cost & hygiene, Deploy procedure, Managing from Cursor / Claude Code, Stack shape (CloudFormation)

### Community 103 - "FastAPI Service Conventions"
Cohesion: 0.29
Nodes (6): Contracts, Docker, FastAPI Service Conventions, Layout (mirror the existing services — verify against repo before assuming), Performance & optimization (demo-scale rules — do NOT over-engineer), Tests

### Community 104 - "n8n Flow Conventions — PETER PAN Triage Pipeline"
Cohesion: 0.29
Nodes (6): Environment & deliverable, Expression gotchas (the usual failure points), n8n Flow Conventions — PETER PAN Triage Pipeline, Parallel calls and the merge (the dashed lines), The 8 nodes (fixed — do not add/remove without explicit approval), Webhook payload contract (UI → flow)

### Community 105 - "Observability & Incidents — Domain Truth"
Cohesion: 0.29
Nodes (6): Enrichment pipeline (capability #1), Incident model, Log & metric conventions (synthetic, demo-scale), Observability & Incidents — Domain Truth, The core story (one line, use it in docs/demos), What is OUT of scope (do not build, do not scaffold "for later")

### Community 106 - "PyTorch Predictor — ML/DL Rules"
Cohesion: 0.29
Nodes (6): Data, Honesty rules (Karpathy), Model, PyTorch Predictor — ML/DL Rules, Serving, Training script requirements (rubric deliverables)

### Community 107 - "Decision"
Cohesion: 0.29
Nodes (7): ADR 0003 — System boundaries and service inventory, Consequences, Decision, Four graded primary services (Layer 3 core), Orchestration rule, RAG invocation rule, Supporting infrastructure (not a fifth/fourth graded deviation)

### Community 108 - "Agent tooling — PETER PAN"
Cohesion: 0.29
Nodes (7): Agent tooling — PETER PAN, Cursor MCP, Optional n8n MCP, Project skills, Project subagents, Security, Verification commands

### Community 109 - "Setup — PETER PAN"
Cohesion: 0.29
Nodes (7): Clone and virtualenv, Environment file, Next steps, Ollama (Layer 1 assistant), Prerequisites, Setup — PETER PAN, Verify before first run

### Community 110 - "test_prompt_surfaces.py"
Cohesion: 0.43
Nodes (5): _file_bytes(), Prompt surfaces are versioned files — node content must match byte-for-byte., test_surface1_extractor_prompt_matches_file(), test_surface2_agent_system_message_matches_file(), test_surface2_tool_descriptions_match_file()

### Community 111 - "PETER PAN — Agentic incident-response platform"
Cohesion: 0.29
Nodes (7): Architecture, Development tooling, Documentation, Layout, License, PETER PAN — Agentic incident-response platform, Quick start

### Community 112 - "Orders API Deployment Incident — INC-20260610-001"
Cohesion: 0.29
Nodes (6): Orders API Deployment Incident — INC-20260610-001, Resolution, Reuse Guidance, Root Cause, Summary, Timeline

### Community 113 - "Postgres Primary Connection Pool Exhaustion — INC-20260618-002"
Cohesion: 0.29
Nodes (6): Postgres Primary Connection Pool Exhaustion — INC-20260618-002, Resolution, Reuse Guidance, Root Cause, Summary, Timeline

### Community 114 - "Redis Cache Degradation — INC-20260625-003"
Cohesion: 0.29
Nodes (6): Redis Cache Degradation — INC-20260625-003, Resolution, Reuse Guidance, Root Cause, Summary, Timeline

### Community 115 - "Database Connectivity Runbook"
Cohesion: 0.29
Nodes (6): Database Connectivity Runbook, Escalation, Investigation Steps (read-only), Remediation, Triage Decision Tree, Verification

### Community 116 - "Deployment Rollback Runbook"
Cohesion: 0.29
Nodes (6): Deployment Rollback Runbook, Escalation, Investigation Steps (read-only), Remediation, Triage Decision Tree, Verification

### Community 117 - "K8s Ingress 5xx Troubleshooting Runbook"
Cohesion: 0.29
Nodes (6): Escalation, Investigation Steps (read-only), K8s Ingress 5xx Troubleshooting Runbook, Remediation, Triage Decision Tree, Verification

### Community 118 - "Orders API Error Spike Runbook"
Cohesion: 0.29
Nodes (6): Escalation, Investigation Steps (read-only), Orders API Error Spike Runbook, Remediation, Triage Decision Tree, Verification

### Community 119 - "Redis Cache Degradation Runbook"
Cohesion: 0.29
Nodes (6): Escalation, Investigation Steps (read-only), Redis Cache Degradation Runbook, Remediation, Triage Decision Tree, Verification

### Community 120 - "graphify reference: query, path, explain"
Cohesion: 0.33
Nodes (5): For /graphify explain, For /graphify path, graphify reference: query, path, explain, Step 0 — Constrained query expansion (REQUIRED before traversal), Step 1 — Traversal

### Community 121 - "PETER PAN Evaluation"
Cohesion: 0.33
Nodes (5): Evidence rules, Fast gate, Full Stage A gate, Invariants, PETER PAN Evaluation

### Community 122 - "Demo Script Guard (days 9–12)"
Cohesion: 0.33
Nodes (5): Demo Script Guard (days 9–12), Freeze rules (active from day 9), Narration, Rehearsal checklist (run twice before recording), The four required video segments (5–8 min total)

### Community 123 - "Prompt Engineering Log — Required Format (25% of grade)"
Cohesion: 0.33
Nodes (5): Entry format per surface (exact structure, no deviations), Honesty rules, Mechanics, Prompt Engineering Log — Required Format (25% of grade), The 5 surfaces (fixed list)

### Community 124 - "Streamlit UI — Professional Demo Standards"
Cohesion: 0.33
Nodes (5): Demo-safety, Non-negotiable UX rules, Streamlit UI — Professional Demo Standards, Structure (per course requirement — two tabs), Visual discipline

### Community 125 - "pull_request_template.md"
Cohesion: 0.33
Nodes (5): Links, Security checklist, Summary, Test plan, Type

### Community 126 - "PETER PAN — AWS demo deployment"
Cohesion: 0.33
Nodes (6): Deploy, PETER PAN — AWS demo deployment, Security notes, Sizing, Teardown, Validate locally

### Community 127 - "validate-cfn.sh script"
Cohesion: 0.60
Nodes (5): fail(), header(), pass(), validate-cfn.sh script, warn()

### Community 128 - "TestEnvVarReferences"
Cohesion: 0.33
Nodes (3): Spot-check: no stray $env references to non-PETER_ vars in integration nodes., The sticky note must document every PETER_* env var referenced in integration no, TestEnvVarReferences

### Community 129 - "test_nonfinite.py"
Cohesion: 0.33
Nodes (3): Predictor: non-finite (NaN/Inf) metric-window safety (TDD red → green).  The E, Non-finite values in the window must not leak into the scored output., test_ewma_score_nonfinite_input_returns_finite_output()

### Community 130 - "Caveman Explainer"
Cohesion: 0.40
Nodes (4): Caveman Explainer, Rules, Test, The ladder (always in this order)

### Community 131 - "PETER PAN — Session A Layer 3 Audit (2026-07-13)"
Cohesion: 0.40
Nodes (4): Doc discrepancies noted (not fixed here), Gaps vs Session A targets, PETER PAN — Session A Layer 3 Audit (2026-07-13), Service inventory

### Community 132 - "request_validation_error"
Cohesion: 0.40
Nodes (5): JSONResponse, RequestValidationError, Request, Return JSON-safe validation errors even when the rejected input is NaN/Inf., request_validation_error()

### Community 133 - "n8n — Layer 2 orchestration (the PETER flow)"
Cohesion: 0.40
Nodes (4): Configuration (never inline in the flow), Flow ↔ diagram mapping, Local compose bootstrap, n8n — Layer 2 orchestration (the PETER flow)

### Community 134 - "Reconciliation Steps 4–5"
Cohesion: 0.40
Nodes (4): Execution, Reconciliation Steps 4–5, Scope, Success criteria

### Community 135 - "K8s Ingress Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, K8s Ingress Service Context, Owner

### Community 136 - "Orders API Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Orders API Service Context, Owner

### Community 137 - "Payments API Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Owner, Payments API Service Context

### Community 138 - "Postgres Primary Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Owner, Postgres Primary Service Context

### Community 139 - "Redis Cache Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Owner, Redis Cache Service Context

### Community 140 - "Shop Web Service Context"
Cohesion: 0.40
Nodes (4): Business Impact, Dependencies, Owner, Shop Web Service Context

### Community 141 - "AGENTS.md — PETER PAN"
Cohesion: 0.50
Nodes (4): AGENTS.md — PETER PAN, Conventions, Imported Claude Cowork project instructions, Scope

### Community 142 - "graphify reference: add a URL and watch a folder"
Cohesion: 0.50
Nodes (3): For /graphify add, For --watch, graphify reference: add a URL and watch a folder

### Community 143 - "graphify reference: commit hook and native CLAUDE.md integration"
Cohesion: 0.50
Nodes (3): For git commit hook, For native CLAUDE.md integration, graphify reference: commit hook and native CLAUDE.md integration

### Community 144 - "graphify reference: incremental update and cluster-only"
Cohesion: 0.50
Nodes (3): For --cluster-only, For --update (incremental re-extraction), graphify reference: incremental update and cluster-only

### Community 145 - "ADR 0004 — Guardrail result and predictor taxonomy contracts"
Cohesion: 0.50
Nodes (4): ADR 0004 — Guardrail result and predictor taxonomy contracts, Consequences, Decision, Related decisions

### Community 146 - "Presentation Evidence — 2026-07-11"
Cohesion: 0.50
Nodes (3): Artifact status, Presentation Evidence — 2026-07-11, Verified

### Community 148 - "provision_ec2.sh"
Cohesion: 0.67
Nodes (3): log(), MSYS_NO_PATHCONV, provision_ec2.sh script

## Knowledge Gaps
- **556 isolated node(s):** `$schema`, `Read(./.env)`, `Read(**/*secret*)`, `Read(**/*credential*)`, `Read(**/id_rsa)` (+551 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DashboardValidationError` connect `app.py` to `llm_client.py`, `validator.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `resolve_demo_recipients()` connect `escalation_service.py` to `llm_client.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `_validate_cases()` connect `run_e2e.py` to `llm_client.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **What connects `$schema`, `Read(./.env)`, `Read(**/*secret*)` to the rest of the system?**
  _556 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05228070175438596 - nodes in this community are weakly interconnected._
- **Should `escalation_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05070422535211268 - nodes in this community are weakly interconnected._
- **Should `notification_dispatch.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07676767676767676 - nodes in this community are weakly interconnected._