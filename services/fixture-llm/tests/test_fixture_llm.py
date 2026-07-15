"""Tests for Fixture LLM OpenAI-compatible seam."""

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import fixture_llm.app as app_module
from fixture_llm.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clear_service_token(monkeypatch):
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)


def test_healthz():
    assert client.get("/healthz").json()["service"] == "fixture-llm"


def test_extract_task_detection():
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": "Extract incident fields. Never infer severity."},
                {"role": "user", "content": "orders-api errors in production"},
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["peter_meta"]["task"] == "extract"
    extracted = json.loads(body["choices"][0]["message"]["content"])
    assert extracted["service"] == "orders-api"
    assert set(extracted) == {
        "service",
        "environment",
        "started_at",
        "symptom",
        "affected_metric",
        "error_signature",
        "customer_impact",
        "mentioned_deploys",
    }
    assert all(isinstance(value, str) for value in extracted.values())


def test_responses_api_returns_openai_compatible_output_text():
    response = client.post(
        "/v1/responses",
        json={
            "model": "peter-stage-a-fixture",
            "instructions": "Extract incident fields. Never infer severity.",
            "input": "orders-api errors in production",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "response"
    assert body["status"] == "completed"
    content = body["output"][0]["content"][0]
    assert content["type"] == "output_text"
    assert "orders-api" in content["text"]
    assert body["peter_meta"]["task"] == "extract"


def test_responses_api_accepts_message_content_parts():
    response = client.post(
        "/v1/responses",
        json={
            "model": "peter-stage-a-fixture",
            "instructions": "Extract incident fields.",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "postgres connection pool exhausted",
                        }
                    ],
                }
            ],
        },
    )

    content = response.json()["output"][0]["content"][0]["text"]
    assert json.loads(content)["service"] == "postgres-primary"


def test_responses_api_detects_extractor_despite_json_schema_instructions():
    response = client.post(
        "/v1/responses",
        json={
            "model": "peter-stage-a-fixture",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You must format output as JSON Schema with service, "
                                "affected_metric, error_signature, customer_impact, "
                                "and mentioned_deploys. Extract structured incident facts. "
                                "orders-api 5xx spike after deploy."
                            ),
                        }
                    ],
                }
            ],
        },
    )

    assert response.json()["peter_meta"]["task"] == "extract"


@pytest.mark.parametrize(
    ("signal_text", "expected_service"),
    [
        ("postgres connection pool exhausted in production", "postgres-primary"),
        ("users report checkout latency on shop-web", "shop-web"),
        ("redis-cache eviction rate is elevated", "redis-cache"),
        (
            "redis-cache latency\n\nCross-domain cache issue affects orders-api",
            "redis-cache",
        ),
    ],
)
def test_extract_normalizes_known_demo_services(signal_text, expected_service):
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": "Extract incident fields. Never infer severity."},
                {"role": "user", "content": signal_text},
            ]
        },
    )

    extracted = json.loads(response.json()["choices"][0]["message"]["content"])
    assert extracted["service"] == expected_service


def test_synthesis_returns_triage_shape():
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": "Write a TriageReport JSON schema structured output."},
                {"role": "user", "content": "synthesise report"},
            ]
        },
    )
    assert response.status_code == 200
    content = response.json()["choices"][0]["message"]["content"]
    assert "incident_id" in content
    assert "citations" in content


def test_synthesis_prefers_commander_tool_evidence_over_service_guessing():
    commander_evidence = {
        "predictor": {
            "incident_class": "db_lock_contention",
            "severity": 5,
            "confidence": 0.93,
        },
        "rag": {
            "answer": "Connection pool exhaustion is documented.",
            "citations": [
                {
                    "source_id": "database_connectivity",
                    "source_type": "runbook",
                    "quote": "Check active connections.",
                }
            ],
        },
        "service_context": {
            "owner_team": "Database Reliability",
            "escalation_path": ["Primary Database Reliability On-Call"],
        },
    }
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {
                    "role": "system",
                    "content": "Write a TriageReport structured output.",
                },
                {
                    "role": "user",
                    "content": (
                        'Incident: {"id":"inc-toolground01","service":"orders-api"}\n\n'
                        'Predictor policy: {"incident_class":"db_lock_contention",'
                        '"severity":5,"p_level":"P1","routing_category":"database",'
                        '"outcome":"routable"}\n\n'
                        f"Commander findings: {json.dumps(commander_evidence)}"
                    ),
                },
            ]
        },
    )

    report = json.loads(response.json()["choices"][0]["message"]["content"])
    assert report["category"] == "database"
    assert report["p_level"] == "P1"
    assert report["owner_team"] == "Database Reliability"
    assert report["model_meta"]["predictor_severity"] == "5"


def test_tool_grounded_synthesis_requires_flow_routing_category():
    """The 6→3 mapping lives only in the n8n flow — the fixture must copy
    predictor_policy.routing_category, never derive category from the class."""
    commander_evidence = {
        "predictor": {
            "incident_class": "db_lock_contention",
            "severity": 5,
            "confidence": 0.93,
        },
    }
    with pytest.raises(ValueError, match="routing_category"):
        client.post(
            "/v1/chat/completions",
            json={
                "messages": [
                    {
                        "role": "system",
                        "content": "Write a TriageReport structured output.",
                    },
                    {
                        "role": "user",
                        "content": (
                            'Incident: {"id":"inc-toolground02","service":"orders-api"}\n\n'
                            f"Commander findings: {json.dumps(commander_evidence)}"
                        ),
                    },
                ]
            },
        )


def test_synthesis_populates_parsed_message_for_json_schema_requests():
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {
                    "role": "system",
                    "content": "Write a TriageReport structured output.",
                },
                {
                    "role": "user",
                    "content": (
                        'Incident: {"id":"inc-orders0002","service":"orders-api"}'
                    ),
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {"name": "TriageReport", "schema": {"type": "object"}},
            },
        },
    )

    message = response.json()["choices"][0]["message"]
    assert message["parsed"]["incident_id"] == "inc-orders0002"
    assert message["parsed"]["category"] == "application"


def test_synthesis_honors_n8n_markdown_codeblock_instruction():
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Write a triage report. Include the enclosing markdown codeblock."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        'Incident: {"id":"inc-orders0003","service":"orders-api"}'
                    ),
                },
            ]
        },
    )

    content = response.json()["choices"][0]["message"]["content"]
    assert content.startswith("```json\n")
    assert content.endswith("\n```")


def test_synthesis_uses_n8n_structured_output_tool_when_offered():
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the incident report writer. Copy owner fields from "
                        "tool results and return one TriageReport."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        'Incident: {"id":"inc-orders0001","service":"orders-api"}'
                    ),
                },
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "format_final_json_response",
                        "description": "Return the final structured report.",
                        "parameters": {"type": "object"},
                    },
                }
            ],
        },
    )

    choice = response.json()["choices"][0]
    assert choice["finish_reason"] == "tool_calls"
    assert choice["message"]["content"] is None
    tool_call = choice["message"]["tool_calls"][0]
    assert tool_call["function"]["name"] == "format_final_json_response"
    report = json.loads(tool_call["function"]["arguments"])
    assert report["incident_id"] == "inc-orders0001"


@pytest.mark.parametrize(
    ("incident_text", "expected_id", "expected_category", "expected_p_level", "expected_owner"),
    [
        (
            'Incident: {"id":"inc-postgres001","service":"postgres-primary","symptom":"connection pool exhausted"}',
            "inc-postgres001",
            "database",
            "P1",
            "Database Reliability",
        ),
        (
            'Incident: {"id":"inc-orders0001","service":"orders-api","symptom":"5xx spike after deploy"}',
            "inc-orders0001",
            "application",
            "P3",
            "App Platform",
        ),
        (
            'Incident: {"id":"inc-redis00001","service":"redis-cache","symptom":"cache latency elevated"}',
            "inc-redis00001",
            "infra",
            "P2",
            "Infra SRE",
        ),
    ],
)
def test_synthesis_is_keyed_to_incident_ground_truth(
    incident_text,
    expected_id,
    expected_category,
    expected_p_level,
    expected_owner,
):
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {
                    "role": "system",
                    "content": "Write a TriageReport JSON schema structured output.",
                },
                {"role": "user", "content": incident_text},
            ]
        },
    )

    report = json.loads(response.json()["choices"][0]["message"]["content"])
    assert report["incident_id"] == expected_id
    assert report["category"] == expected_category
    assert report["p_level"] == expected_p_level
    assert report["owner_team"] == expected_owner
    assert report["citations"]


@pytest.mark.parametrize(
    ("system_prompt", "expected_task"),
    [
        ("You are the incident commander. Select the appropriate tool.", "agent"),
        ("Generate an answer with a runbook citation.", "rag_generate"),
        ("You are the grounded SRE assistant. Refuse off-topic requests.", "assistant"),
        ("Unrecognized fixture request.", "extract"),
    ],
)
def test_all_fixture_task_routes(system_prompt, expected_task):
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "orders-api needs investigation"},
            ]
        },
    )

    assert response.status_code == 200
    assert response.json()["peter_meta"]["task"] == expected_task


_COMMANDER_TOOLS = [
    {
        "type": "function",
        "function": {"name": name, "parameters": {"type": "object"}},
    }
    for name in (
        "Predictor_Tool",
        "RAG_Query_Tool",
        "Service_Context_Tool",
        "LangGraph_Agent_Tool",
    )
]


def _commander_request(messages):
    return client.post(
        "/v1/chat/completions",
        json={"messages": messages, "tools": _COMMANDER_TOOLS},
    ).json()["choices"][0]


def _tool_roundtrip(messages, choice, result):
    call = choice["message"]["tool_calls"][0]
    return [
        *messages,
        choice["message"],
        {
            "role": "tool",
            "name": call["function"]["name"],
            "tool_call_id": call["id"],
            "content": json.dumps(result),
        },
    ]


def test_commander_calls_simple_incident_tools_then_returns_evidence():
    messages = [
        {"role": "system", "content": "You are the incident commander. Use tools."},
        {
            "role": "user",
            "content": 'Incident: {"service":"orders-api","symptom":"5xx spike"}',
        },
    ]

    predictor = _commander_request(messages)
    assert predictor["message"]["tool_calls"][0]["function"]["name"] == "Predictor_Tool"
    messages = _tool_roundtrip(
        messages,
        predictor,
        [{"incident_class": "error_rate_spike", "severity": 3, "confidence": 0.91}],
    )

    rag = _commander_request(messages)
    assert rag["message"]["tool_calls"][0]["function"]["name"] == "RAG_Query_Tool"
    messages = _tool_roundtrip(
        messages,
        rag,
        [{
            "answer": "Check deployment correlation.",
            "citations": [
                {
                    "source_id": "orders_api_error_spike",
                    "source_type": "runbook",
                    "quote": "Check recent deployments.",
                }
            ],
            "refused": False,
        }],
    )

    owner = _commander_request(messages)
    assert owner["message"]["tool_calls"][0]["function"]["name"] == "Service_Context_Tool"
    messages = _tool_roundtrip(
        messages,
        owner,
        [{
            "owner_team": "App Platform",
            "escalation_path": ["Primary App Platform On-Call"],
        }],
    )

    final = _commander_request(messages)
    assert final["finish_reason"] == "stop"
    evidence = json.loads(final["message"]["content"])
    assert evidence["predictor"]["severity"] == 3
    assert evidence["rag"]["citations"][0]["source_id"] == "orders_api_error_spike"
    assert evidence["service_context"]["owner_team"] == "App Platform"


def test_commander_uses_langgraph_without_direct_rag_for_complex_infra():
    messages = [
        {"role": "system", "content": "You are the incident commander. Use tools."},
        {
            "role": "user",
            "content": (
                'Incident: {"service":"redis-cache","symptom":"cross-domain cache '
                'latency affecting checkout"}'
            ),
        },
    ]
    predictor = _commander_request(messages)
    messages = _tool_roundtrip(
        messages,
        predictor,
        [{"incident_class": "memory_leak", "severity": 4, "confidence": 0.9}],
    )

    deep = _commander_request(messages)
    assert deep["message"]["tool_calls"][0]["function"]["name"] == "LangGraph_Agent_Tool"
    messages = _tool_roundtrip(
        messages,
        deep,
        [{
            "category": "infra",
            "p_level": "P2",
            "owner_team": "Infra SRE",
            "escalation_path": ["Primary Infra SRE On-Call"],
            "citations": [
                {
                    "source_id": "redis_cache_degradation",
                    "source_type": "runbook",
                    "quote": "Inspect cache saturation.",
                }
            ],
        }],
    )

    final = _commander_request(messages)
    evidence = json.loads(final["message"]["content"])
    assert "rag" not in evidence
    assert evidence["langgraph"]["owner_team"] == "Infra SRE"


def test_extractor_does_not_invent_unknown_service():
    response = client.post(
        "/v1/chat/completions",
        json={
            "messages": [
                {"role": "system", "content": "Extract incident fields."},
                {"role": "user", "content": "An unnamed component is slow."},
            ]
        },
    )
    extracted = json.loads(response.json()["choices"][0]["message"]["content"])
    assert extracted["service"] == ""


def test_bearer_token_uses_constant_time_comparison(monkeypatch):
    calls: list[tuple[str, str]] = []

    def compare_digest(provided: str, expected: str) -> bool:
        calls.append((provided, expected))
        return provided == expected

    monkeypatch.setattr(
        app_module,
        "hmac",
        SimpleNamespace(compare_digest=compare_digest),
        raising=False,
    )
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "expected-token")

    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer wrong-token"},
        json={"messages": [{"role": "user", "content": "extract incident"}]},
    )

    assert response.status_code == 401
    assert calls == [("wrong-token", "expected-token")]
