"""Static QA for n8n/peter-flow.json — Stage A.

Asserts required topology, guardrail branches, review route, four route
destinations, env-var-only URL references, no embedded secrets, and bearer
auth on all state-changing delivery nodes.  No network I/O; parses JSON only.

Run: python -m pytest n8n/ -q   (from repo root)
     python -m pytest -q        (from n8n/ directory)
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Fixture: load flow once per test session
# ---------------------------------------------------------------------------

FLOW_PATH = Path(__file__).parent.parent / "peter-flow.json"


@pytest.fixture(scope="module")
def flow() -> dict:
    return json.loads(FLOW_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def nodes_by_name(flow: dict) -> dict[str, dict]:
    return {n["name"]: n for n in flow["nodes"]}


@pytest.fixture(scope="module")
def connections(flow: dict) -> dict:
    return flow["connections"]


# ---------------------------------------------------------------------------
# Expected topology constants
# ---------------------------------------------------------------------------

REQUIRED_NODE_NAMES: list[str] = [
    # ingestion path
    "Signal Webhook",
    "Normalize Signal",
    # guardrail input
    "Guardrails Input Check",
    "Input Passed?",
    "Signal Accepted",
    "Reject Signal",
    "Respond 503 Guardrails Down",
    # context enrichment
    "Maintenance Window Stub",
    "Recent Deploys (GitHub)",
    "Shape DeployRefs",
    "Complaints Stub",
    "Merge Context",
    "Build IncidentContext",
    "Known Noise?",
    "Log Suppression",
    "Respond Suppressed",
    # extraction + assembly
    "Extract Incident Info",
    "Extractor Model (Mock Seam)",
    "Assemble Incident",
    # commander + tools
    "Incident Commander",
    "Commander Model (Mock Seam)",
    "Predictor Tool",
    "RAG Query Tool",
    "LangGraph Agent Tool",
    "Service Context Tool",
    # triage report
    "Write TriageReport",
    "Writer Model (Mock Seam)",
    "TriageReport Parser",
    "Fixture TriageReport Fallback",
    "Finalize TriageReport",
    # guardrail output
    "Guardrails Output Check",
    "Output Passed?",
    "Respond Flagged (Guardrails Down)",
    # routing
    "Prepare Routing",
    "Route by Category",
    "DB Team Webhook",
    "Infra Team Webhook",
    "App Team Webhook",
    "Manual Triage Webhook",
    "Respond TriageReport",
    # review queue
    "Send to Review Queue",
    "Respond Flagged for Review",
    # escalation + slack
    "P1?",
    "Escalation Dispatch (Preview-First)",
    "Slack Incident Channel Stub",
]

# All httpRequest nodes whose URL must reference a PETER_* env var
EXPECTED_ENV_VAR_URLS: dict[str, str] = {
    "Guardrails Input Check": "PETER_GUARDRAILS_URL",
    "Guardrails Output Check": "PETER_GUARDRAILS_URL",
    "Recent Deploys (GitHub)": "PETER_GITHUB_API",
    "Predictor Tool": "PETER_PREDICTOR_URL",
    "RAG Query Tool": "PETER_RAG_URL",
    "LangGraph Agent Tool": "PETER_LANGGRAPH_URL",
    "Service Context Tool": "PETER_TOOLS_URL",
    "Send to Review Queue": "PETER_REVIEW_QUEUE_URL",
    "DB Team Webhook": "PETER_DB_TEAM_WEBHOOK",
    "Infra Team Webhook": "PETER_INFRA_TEAM_WEBHOOK",
    "App Team Webhook": "PETER_APP_TEAM_WEBHOOK",
    "Manual Triage Webhook": "PETER_TRIAGE_TEAM_WEBHOOK",
    "Escalation Dispatch (Preview-First)": "PETER_TOOLS_URL",
    "Slack Incident Channel Stub": "PETER_SLACK_STUB_URL",
}

# All state-changing delivery nodes must use genericCredentialType + httpBearerAuth
DELIVERY_NODES_REQUIRING_BEARER: list[str] = [
    "Send to Review Queue",
    "DB Team Webhook",
    "Infra Team Webhook",
    "App Team Webhook",
    "Manual Triage Webhook",
    "Slack Incident Channel Stub",
]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _connected_to(connections: dict, source: str, output_slot: int) -> list[str]:
    """Return names of nodes connected from source at main[output_slot]."""
    main = connections.get(source, {}).get("main", [])
    if output_slot >= len(main):
        return []
    return [edge["node"] for edge in main[output_slot]]


def _params(node: dict) -> dict:
    return node.get("parameters", {})


# ---------------------------------------------------------------------------
# 1. Flow metadata
# ---------------------------------------------------------------------------


class TestFlowMetadata:
    def test_file_exists(self) -> None:
        assert FLOW_PATH.exists(), f"peter-flow.json not found at {FLOW_PATH}"

    def test_has_name(self, flow: dict) -> None:
        assert flow.get("name"), "Flow has no 'name' field"

    def test_active_is_false(self, flow: dict) -> None:
        """Flow must NOT be live (active: false prevents deregistering the production webhook)."""
        assert flow.get("active") is False, (
            f"Flow active={flow.get('active')!r} — must be false in committed JSON"
        )

    def test_has_execution_order_v1(self, flow: dict) -> None:
        assert flow.get("settings", {}).get("executionOrder") == "v1"

    def test_nodes_list_non_empty(self, flow: dict) -> None:
        assert isinstance(flow.get("nodes"), list) and len(flow["nodes"]) > 0

    def test_connections_dict_present(self, flow: dict) -> None:
        assert isinstance(flow.get("connections"), dict)

    def test_signal_webhook_requires_header_auth(self, nodes_by_name: dict) -> None:
        webhook = nodes_by_name["Signal Webhook"]
        assert _params(webhook).get("authentication") == "headerAuth"


# ---------------------------------------------------------------------------
# 2. Required nodes
# ---------------------------------------------------------------------------


class TestRequiredNodes:
    @pytest.mark.parametrize("name", REQUIRED_NODE_NAMES)
    def test_node_present(self, name: str, nodes_by_name: dict) -> None:
        assert name in nodes_by_name, (
            f"Required node {name!r} missing from peter-flow.json"
        )

    def test_no_duplicate_node_names(self, flow: dict) -> None:
        names = [n["name"] for n in flow["nodes"]]
        seen: set[str] = set()
        for name in names:
            assert name not in seen, f"Duplicate node name: {name!r}"
            seen.add(name)


# ---------------------------------------------------------------------------
# 3. Core connection edges
# ---------------------------------------------------------------------------


class TestCoreConnections:
    def test_webhook_to_normalize(self, connections: dict) -> None:
        assert "Normalize Signal" in _connected_to(connections, "Signal Webhook", 0)

    def test_normalize_to_guardrails_input(self, connections: dict) -> None:
        assert "Guardrails Input Check" in _connected_to(connections, "Normalize Signal", 0)

    def test_guardrails_input_success_to_input_passed(self, connections: dict) -> None:
        assert "Input Passed?" in _connected_to(connections, "Guardrails Input Check", 0)

    def test_input_passed_true_to_signal_accepted(self, connections: dict) -> None:
        assert "Signal Accepted" in _connected_to(connections, "Input Passed?", 0)

    def test_input_passed_false_to_reject_signal(self, connections: dict) -> None:
        assert "Reject Signal" in _connected_to(connections, "Input Passed?", 1)

    def test_build_context_to_known_noise(self, connections: dict) -> None:
        assert "Known Noise?" in _connected_to(connections, "Build IncidentContext", 0)

    def test_known_noise_true_to_log_suppression(self, connections: dict) -> None:
        assert "Log Suppression" in _connected_to(connections, "Known Noise?", 0)

    def test_known_noise_false_to_extract_info(self, connections: dict) -> None:
        assert "Extract Incident Info" in _connected_to(connections, "Known Noise?", 1)

    def test_finalize_to_guardrails_output(self, connections: dict) -> None:
        assert "Guardrails Output Check" in _connected_to(connections, "Finalize TriageReport", 0)

    def test_prepare_routing_fans_to_route(self, connections: dict) -> None:
        targets = _connected_to(connections, "Prepare Routing", 0)
        assert "Route by Category" in targets

    def test_prepare_routing_fans_to_p1_check(self, connections: dict) -> None:
        targets = _connected_to(connections, "Prepare Routing", 0)
        assert "P1?" in targets

    def test_prepare_routing_fans_to_slack(self, connections: dict) -> None:
        targets = _connected_to(connections, "Prepare Routing", 0)
        assert "Slack Incident Channel Stub" in targets

    def test_p1_true_to_escalation_dispatch(self, connections: dict) -> None:
        assert "Escalation Dispatch (Preview-First)" in _connected_to(connections, "P1?", 0)

    def test_deploy_filter_rejects_future_timestamps(self, nodes_by_name: dict) -> None:
        code = _params(nodes_by_name["Shape DeployRefs"]).get("jsCode", "")
        assert "age >= 0" in code

    def test_commander_prompt_prevents_duplicate_rag(self, nodes_by_name: dict) -> None:
        prompt = (
            _params(nodes_by_name["Incident Commander"])
            .get("options", {})
            .get("systemMessage", "")
        )
        assert "do not call RAG directly" in prompt

    def test_fixture_fallback_uses_tool_evidence(self, nodes_by_name: dict) -> None:
        code = _params(nodes_by_name["Fixture TriageReport Fallback"]).get(
            "jsCode", ""
        )
        assert "evidence.predictor" in code
        assert "evidence.service_context" in code
        assert "service.includes('postgres')" not in code

    def test_normalizer_preserves_nested_raw_metric_reference(
        self, nodes_by_name: dict
    ) -> None:
        assignments = (
            _params(nodes_by_name["Normalize Signal"])
            .get("assignments", {})
            .get("assignments", [])
        )
        raw_assignment = next(item for item in assignments if item.get("name") == "raw")
        assert "$json.body?.raw" in raw_assignment.get("value", "")


# ---------------------------------------------------------------------------
# 4. Guardrail branches — error outputs route to fallback responders
# ---------------------------------------------------------------------------


class TestGuardrailBranches:
    def test_guardrails_input_has_continue_error_output(
        self, nodes_by_name: dict
    ) -> None:
        node = nodes_by_name["Guardrails Input Check"]
        assert node.get("onError") == "continueErrorOutput", (
            "Guardrails Input Check must use onError=continueErrorOutput for graceful degradation"
        )

    def test_guardrails_input_error_branch_to_503_responder(
        self, connections: dict
    ) -> None:
        """main[1] on an onError=continueErrorOutput node is the error path."""
        targets = _connected_to(connections, "Guardrails Input Check", 1)
        assert "Respond 503 Guardrails Down" in targets, (
            "Error branch of Guardrails Input Check must route to Respond 503 Guardrails Down"
        )

    def test_guardrails_input_success_branch_to_if_node(
        self, connections: dict
    ) -> None:
        targets = _connected_to(connections, "Guardrails Input Check", 0)
        assert "Input Passed?" in targets

    def test_guardrails_output_has_continue_error_output(
        self, nodes_by_name: dict
    ) -> None:
        node = nodes_by_name["Guardrails Output Check"]
        assert node.get("onError") == "continueErrorOutput", (
            "Guardrails Output Check must use onError=continueErrorOutput"
        )

    def test_guardrails_output_error_branch_to_review_queue(
        self, connections: dict
    ) -> None:
        targets = _connected_to(connections, "Guardrails Output Check", 1)
        assert "Send to Review Queue" in targets, (
            "Output guardrail transport failures must be queued for human review"
        )

    def test_guardrails_output_success_branch_to_output_passed(
        self, connections: dict
    ) -> None:
        targets = _connected_to(connections, "Guardrails Output Check", 0)
        assert "Output Passed?" in targets

    def test_output_guardrail_receives_service_identity(
        self, nodes_by_name: dict
    ) -> None:
        body = _params(nodes_by_name["Guardrails Output Check"]).get("jsonBody", "")
        assert "service:" in body
        assert "environment:" in body
        assert "Assemble Incident" in body
        assert "require_tool_evidence: true" in body


# ---------------------------------------------------------------------------
# 5. Review route — failed output → review queue, not discarded
# ---------------------------------------------------------------------------


class TestReviewRoute:
    def test_output_passed_false_to_review_queue(self, connections: dict) -> None:
        """main[1] of Output Passed? is the 'false' (failed guardrail) branch."""
        targets = _connected_to(connections, "Output Passed?", 1)
        assert "Send to Review Queue" in targets, (
            "Output Passed? false branch must route to Send to Review Queue"
        )

    def test_output_passed_true_to_prepare_routing(self, connections: dict) -> None:
        targets = _connected_to(connections, "Output Passed?", 0)
        assert "Prepare Routing" in targets

    def test_review_queue_to_respond_flagged(self, connections: dict) -> None:
        targets = _connected_to(connections, "Send to Review Queue", 0)
        assert "Respond Flagged for Review" in targets, (
            "Send to Review Queue must respond with 'flagged_for_review' to the caller"
        )

    def test_review_queue_failure_returns_503(
        self, nodes_by_name: dict, connections: dict
    ) -> None:
        sender = nodes_by_name["Send to Review Queue"]
        assert sender.get("onError") == "continueErrorOutput"
        assert "Respond Flagged (Guardrails Down)" in _connected_to(
            connections, "Send to Review Queue", 1
        )
        params = _params(nodes_by_name["Respond Flagged (Guardrails Down)"])
        assert params.get("options", {}).get("responseCode") == 503

    def test_review_payload_merges_flags_into_triage_report(
        self, nodes_by_name: dict
    ) -> None:
        body = _params(nodes_by_name["Send to Review Queue"]).get("jsonBody", "")
        assert "guardrail_flags" in body
        assert "guardrails_unavailable" in body

    def test_respond_flagged_for_review_response_code_202(
        self, nodes_by_name: dict
    ) -> None:
        params = _params(nodes_by_name["Respond Flagged for Review"])
        assert params.get("options", {}).get("responseCode") == 202


# ---------------------------------------------------------------------------
# 6. Four route destinations: database / infra / application / unroutable
# ---------------------------------------------------------------------------


class TestFourRouteDestinations:
    def test_route_by_category_is_switch_node(self, nodes_by_name: dict) -> None:
        node = nodes_by_name["Route by Category"]
        assert "switch" in node["type"].lower(), (
            f"Route by Category type={node['type']!r} must be a Switch node"
        )

    @pytest.mark.parametrize(
        "output_key",
        ["database", "infra", "application"],
    )
    def test_named_route_key_present(
        self, output_key: str, nodes_by_name: dict
    ) -> None:
        rules = _params(nodes_by_name["Route by Category"]).get("rules", {}).get("values", [])
        keys = [r.get("outputKey") for r in rules]
        assert output_key in keys, f"Switch missing outputKey={output_key!r}; got: {keys}"

    def test_unroutable_fallback_configured(self, nodes_by_name: dict) -> None:
        opts = _params(nodes_by_name["Route by Category"]).get("options", {})
        assert opts.get("fallbackOutput") == "extra", (
            "Route by Category must have fallbackOutput='extra' for unroutable incidents"
        )
        assert opts.get("renameFallbackOutput") == "unroutable", (
            "Fallback output must be renamed to 'unroutable'"
        )

    def test_database_route_to_db_team_webhook(self, connections: dict) -> None:
        assert "DB Team Webhook" in _connected_to(connections, "Route by Category", 0)

    def test_infra_route_to_infra_team_webhook(self, connections: dict) -> None:
        assert "Infra Team Webhook" in _connected_to(connections, "Route by Category", 1)

    def test_application_route_to_app_team_webhook(self, connections: dict) -> None:
        assert "App Team Webhook" in _connected_to(connections, "Route by Category", 2)

    def test_unroutable_route_to_manual_triage(self, connections: dict) -> None:
        assert "Manual Triage Webhook" in _connected_to(connections, "Route by Category", 3)

    def test_all_team_webhooks_converge_on_respond(self, connections: dict) -> None:
        for webhook_node in (
            "DB Team Webhook",
            "Infra Team Webhook",
            "App Team Webhook",
            "Manual Triage Webhook",
        ):
            targets = _connected_to(connections, webhook_node, 0)
            assert "Respond TriageReport" in targets, (
                f"{webhook_node} must connect to Respond TriageReport"
            )


# ---------------------------------------------------------------------------
# 7. Env-var references — all integration URLs use $env.PETER_*
# ---------------------------------------------------------------------------


class TestEnvVarReferences:
    @pytest.mark.parametrize("node_name,expected_var", list(EXPECTED_ENV_VAR_URLS.items()))
    def test_url_references_env_var(
        self, node_name: str, expected_var: str, nodes_by_name: dict
    ) -> None:
        node = nodes_by_name[node_name]
        url_val = _params(node).get("url", "")
        assert f"$env.{expected_var}" in url_val, (
            f"Node {node_name!r} URL must reference $env.{expected_var}; got: {url_val!r}"
        )

    def test_all_env_var_names_start_with_peter(self, nodes_by_name: dict) -> None:
        """Spot-check: no stray $env references to non-PETER_ vars in integration nodes."""
        pattern = re.compile(r"\$env\.([A-Z0-9_]+)")
        for name, expected_var in EXPECTED_ENV_VAR_URLS.items():
            url_val = _params(nodes_by_name[name]).get("url", "")
            for match in pattern.finditer(url_val):
                var = match.group(1)
                assert var.startswith("PETER_"), (
                    f"Node {name!r} references unexpected env var ${var}; only PETER_* expected"
                )

    def test_sticky_note_documents_all_required_env_vars(self, flow: dict) -> None:
        """The sticky note must document every PETER_* env var referenced in integration nodes."""
        sticky_text = " ".join(
            n["parameters"].get("content", "")
            for n in flow["nodes"]
            if n["type"] == "n8n-nodes-base.stickyNote"
        )
        for var in EXPECTED_ENV_VAR_URLS.values():
            assert var in sticky_text, (
                f"Env var {var} is used by integration nodes but not documented in any sticky note"
            )


# ---------------------------------------------------------------------------
# 8. No embedded secret values or live resource IDs
# ---------------------------------------------------------------------------

# Patterns that would indicate a hardcoded secret (not an n8n expression or credential name)
_SECRET_PATTERNS: list[re.Pattern] = [
    # Classic API-key-style tokens: 20+ hex/base64 chars not inside a template expression
    re.compile(r'(?<!\$\{)(?<!\{\{)["\']([A-Za-z0-9+/]{32,}={0,2})["\']'),
    # Bearer <token> in a plain string (not inside an n8n expression)
    re.compile(r'[Bb]earer\s+(?!\$\{)(?!\{\{)([A-Za-z0-9._-]{20,})'),
    # sk- prefix (OpenAI-style keys)
    re.compile(r'"sk-[A-Za-z0-9]{20,}"'),
    # AWS access key pattern
    re.compile(r'"(?:AKIA|ASIA)[A-Z0-9]{16}"'),
]


def _all_string_values(obj: object) -> list[str]:
    """Recursively collect all string values from a JSON-like structure."""
    results: list[str] = []
    if isinstance(obj, str):
        results.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            results.extend(_all_string_values(v))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_all_string_values(item))
    return results


class TestNoEmbeddedSecrets:
    def test_flow_is_inactive(self, flow: dict) -> None:
        """active:false is the primary guard against live webhook registration."""
        assert flow.get("active") is False

    def test_no_hardcoded_secret_patterns(self, flow: dict) -> None:
        """No string value in the flow should match a known secret pattern."""
        all_strings = _all_string_values(flow)
        for s in all_strings:
            for pattern in _SECRET_PATTERNS:
                m = pattern.search(s)
                assert m is None, (
                    f"Possible embedded secret matching {pattern.pattern!r} "
                    f"found in flow string: {s[:120]!r}"
                )

    def test_no_hardcoded_http_urls_in_integration_nodes(
        self, nodes_by_name: dict
    ) -> None:
        """Integration node URLs must use $env.* expressions, not literal http:// addresses."""
        for node_name in EXPECTED_ENV_VAR_URLS:
            url = _params(nodes_by_name[node_name]).get("url", "")
            # Must be an n8n expression (starts with ={{)
            assert url.startswith("={{"), (
                f"Node {node_name!r} URL {url!r} is not an n8n expression (must start with ={{)"
            )
            # Must not contain a literal https?:// outside an expression template
            literal_url = re.search(r"https?://(?!\$)", url)
            assert literal_url is None, (
                f"Node {node_name!r} URL contains a literal HTTP address: {url!r}"
            )

    def test_pindata_is_empty(self, flow: dict) -> None:
        """pinData must be empty — pinned live data can expose real incident PII."""
        assert flow.get("pinData") == {}, (
            "pinData is non-empty — remove all pinned execution data before committing"
        )

    def test_model_ids_use_fixture_seam_not_live_keys(self, nodes_by_name: dict) -> None:
        """LLM model nodes must reference the fixture seam model, not live API model IDs."""
        seam_nodes = [
            "Extractor Model (Mock Seam)",
            "Commander Model (Mock Seam)",
            "Writer Model (Mock Seam)",
        ]
        for name in seam_nodes:
            node = nodes_by_name[name]
            model_value = _params(node).get("model", {}).get("value", "")
            assert model_value == "peter-stage-a-fixture", (
                f"Model node {name!r} references {model_value!r}; "
                "expected 'peter-stage-a-fixture' (Stage A seam)"
            )

    def test_fixture_models_use_chat_completions_for_parser_compatibility(
        self, nodes_by_name: dict
    ) -> None:
        for name in (
            "Extractor Model (Mock Seam)",
            "Commander Model (Mock Seam)",
            "Writer Model (Mock Seam)",
        ):
            assert _params(nodes_by_name[name]).get("responsesApiEnabled") is False, (
                f"{name} must disable Responses API for the Stage A OpenAI-compatible "
                "fixture and n8n structured output parsers"
            )


# ---------------------------------------------------------------------------
# 9. Bearer auth on all state-changing delivery nodes
# ---------------------------------------------------------------------------


class TestBearerAuthOnDeliveryNodes:
    @pytest.mark.parametrize("node_name", DELIVERY_NODES_REQUIRING_BEARER)
    def test_uses_generic_credential_type(
        self, node_name: str, nodes_by_name: dict
    ) -> None:
        params = _params(nodes_by_name[node_name])
        assert params.get("authentication") == "genericCredentialType", (
            f"Delivery node {node_name!r} must use authentication=genericCredentialType"
        )

    @pytest.mark.parametrize("node_name", DELIVERY_NODES_REQUIRING_BEARER)
    def test_uses_http_bearer_auth(
        self, node_name: str, nodes_by_name: dict
    ) -> None:
        params = _params(nodes_by_name[node_name])
        assert params.get("genericAuthType") == "httpBearerAuth", (
            f"Delivery node {node_name!r} must use genericAuthType=httpBearerAuth"
        )

    @pytest.mark.parametrize("node_name", DELIVERY_NODES_REQUIRING_BEARER)
    def test_sends_body_as_json(
        self, node_name: str, nodes_by_name: dict
    ) -> None:
        params = _params(nodes_by_name[node_name])
        assert params.get("sendBody") is True
        assert params.get("specifyBody") == "json"

    def test_service_call_nodes_also_use_bearer(self, nodes_by_name: dict) -> None:
        """Internal service call nodes (guardrails, predictor, rag, langgraph) also bear auth."""
        service_nodes = [
            "Guardrails Input Check",
            "Guardrails Output Check",
            "Predictor Tool",
            "RAG Query Tool",
            "LangGraph Agent Tool",
            "Service Context Tool",
            "Escalation Dispatch (Preview-First)",
        ]
        for name in service_nodes:
            params = _params(nodes_by_name[name])
            assert params.get("authentication") == "genericCredentialType", (
                f"Service node {name!r} must use authentication=genericCredentialType"
            )
            assert params.get("genericAuthType") == "httpBearerAuth", (
                f"Service node {name!r} must use genericAuthType=httpBearerAuth"
            )


# ---------------------------------------------------------------------------
# 10. TriageReport schema — frozen contract shape
# ---------------------------------------------------------------------------


class TestTriageReportSchema:
    def test_writer_is_basic_llm_chain_not_second_agent(
        self, nodes_by_name: dict
    ) -> None:
        writer = nodes_by_name["Write TriageReport"]
        assert writer["type"] == (
            "@n8n/n8n-nodes-langchain.chainLlm"
        )
        assert writer["typeVersion"] == 1.8, (
            "ChainLLM 1.9 routes BaseMessage output through getAgentStepsParser, "
            "which reads an empty .text value for this OpenAI-compatible fixture"
        )

    def test_writer_parser_failure_routes_to_deterministic_fixture_fallback(
        self, nodes_by_name: dict, connections: dict
    ) -> None:
        writer = nodes_by_name["Write TriageReport"]
        assert writer.get("onError") == "continueErrorOutput"
        assert "Fixture TriageReport Fallback" in _connected_to(
            connections, "Write TriageReport", 1
        )
        assert "Finalize TriageReport" in _connected_to(
            connections, "Fixture TriageReport Fallback", 0
        )

    def test_parser_node_has_manual_schema(self, nodes_by_name: dict) -> None:
        node = nodes_by_name["TriageReport Parser"]
        params = _params(node)
        assert params.get("schemaType") == "manual"
        schema_str = params.get("inputSchema", "")
        assert schema_str, "TriageReport Parser has no inputSchema"
        schema = json.loads(schema_str)
        assert schema.get("title") == "TriageReport"

    def test_triage_report_schema_required_fields(self, nodes_by_name: dict) -> None:
        schema_str = _params(nodes_by_name["TriageReport Parser"]).get("inputSchema", "{}")
        schema = json.loads(schema_str)
        required = set(schema.get("required", []))
        for field in ("incident_id", "category", "p_level", "summary", "citations", "confidence"):
            assert field in required, f"TriageReport schema missing required field: {field!r}"

    def test_category_enum_matches_route_keys(self, nodes_by_name: dict) -> None:
        schema_str = _params(nodes_by_name["TriageReport Parser"]).get("inputSchema", "{}")
        schema = json.loads(schema_str)
        category_enum = schema.get("properties", {}).get("category", {}).get("enum", [])
        assert set(category_enum) == {"infra", "database", "application"}, (
            f"Category enum {category_enum!r} must match Route by Category keys"
        )

    def test_p_level_enum_covers_all_priorities(self, nodes_by_name: dict) -> None:
        schema_str = _params(nodes_by_name["TriageReport Parser"]).get("inputSchema", "{}")
        schema = json.loads(schema_str)
        p_enum = schema.get("properties", {}).get("p_level", {}).get("enum", [])
        assert set(p_enum) == {"P1", "P2", "P3", "P4"}
