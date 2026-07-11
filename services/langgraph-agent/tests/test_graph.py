"""P1 vs P3 fixture incidents walk expected paths (BUILD_PLAN §3, LangGraph
agent row); RAG/Tools mocked via httpx.MockTransport — no real network.
Output always validates as the vendored TriageReport; owner_team/
escalation_path only ever come from the mocked Tools API response.
"""

from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

from langgraph_agent import app as app_module
from langgraph_agent.contracts import TriageReport

client = TestClient(app_module.app)

RAG_URL = "https://rag.example.test"
TOOLS_URL = "https://tools.example.test"

MOCK_OWNER_TEAM = "Database Platform"
MOCK_ESCALATION_PATH = ["db-oncall", "db-team-lead", "incident-commander"]


def _healthy_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/query":
        return httpx.Response(
            200,
            json={
                "answer": "Check connection pool exhaustion and recent migrations.",
                "citations": [
                    {
                        "source_id": "runbook:database-connectivity",
                        "source_type": "runbook",
                        "quote": "Restart the connection pooler if saturated.",
                    }
                ],
            },
        )
    if path == "/tools/service_context":
        return httpx.Response(
            200,
            json={
                "owner_team": MOCK_OWNER_TEAM,
                "escalation_path": MOCK_ESCALATION_PATH,
            },
        )
    if path == "/tools/similar_incidents":
        return httpx.Response(
            200,
            json={
                "similar_incidents": [
                    {
                        "incident_id": "inc-hist0001",
                        "root_cause": "connection pool exhaustion",
                    }
                ],
                "count": 1,
            },
        )
    return httpx.Response(404, json={"detail": "not found"})


def _tools_down_handler(request: httpx.Request) -> httpx.Response:
    path = request.url.path
    if path == "/query":
        return _healthy_handler(request)
    raise httpx.ConnectError("connection refused", request=request)


def _everything_down_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("connection refused", request=request)


def _patch_client(monkeypatch, handler):
    def fake_build_client():
        return httpx.AsyncClient(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(app_module, "_build_client", fake_build_client)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)
    monkeypatch.setenv("PETER_RAG_URL", RAG_URL)
    monkeypatch.setenv("PETER_TOOLS_URL", TOOLS_URL)


P1_INCIDENT = {
    "id": "inc-p1demo001",
    "service": "postgres-primary",
    "environment": "production",
    "symptom": "connections exhausted, queries timing out",
    "context": {"severity": 5},
}

P3_INCIDENT = {
    "id": "inc-p3demo001",
    "service": "shop-web",
    "environment": "production",
    "symptom": "elevated latency on checkout page",
    "context": {"severity": 3},
}


def test_p1_incident_walks_expected_path(monkeypatch):
    _patch_client(monkeypatch, _healthy_handler)

    response = client.post(
        "/agent/run", json={"incident": P1_INCIDENT, "question": "what's going on?"}
    )
    assert response.status_code == 200, response.text
    body = response.json()

    report = TriageReport.model_validate(body)  # never emit an invalid report
    assert report.category == "database"
    assert report.p_level == "P1"
    assert report.confidence == pytest.approx(0.9)
    assert report.owner_team == MOCK_OWNER_TEAM  # only from mocked Tools response
    assert report.escalation_path == MOCK_ESCALATION_PATH
    assert report.guardrail_flags == []
    assert len(report.citations) >= 2  # RAG citation + tool_result citation(s)
    assert any(c.source_type == "tool_result" for c in report.citations)
    assert any(c.source_type == "runbook" for c in report.citations)


def test_p3_incident_walks_expected_path(monkeypatch):
    _patch_client(monkeypatch, _healthy_handler)

    response = client.post("/agent/run", json={"incident": P3_INCIDENT})
    assert response.status_code == 200, response.text
    body = response.json()

    report = TriageReport.model_validate(body)
    assert report.category == "application"
    assert report.p_level == "P3"
    assert report.confidence == pytest.approx(0.9)
    assert report.owner_team == MOCK_OWNER_TEAM
    assert report.escalation_path == MOCK_ESCALATION_PATH
    assert report.guardrail_flags == []


def test_missing_severity_defaults_to_p3_with_lowered_confidence(monkeypatch):
    _patch_client(monkeypatch, _healthy_handler)

    incident = {**P3_INCIDENT, "context": {}}
    response = client.post("/agent/run", json={"incident": incident})
    assert response.status_code == 200
    report = TriageReport.model_validate(response.json())
    assert report.p_level == "P3"
    assert report.confidence == pytest.approx(0.4)


def test_canonical_incident_p_level_is_preserved(monkeypatch):
    _patch_client(monkeypatch, _healthy_handler)
    incident = {**P1_INCIDENT, "p_level": "P1", "context": {}}

    response = client.post("/agent/run", json={"incident": incident})

    assert response.status_code == 200
    report = TriageReport.model_validate(response.json())
    assert report.p_level == "P1"
    assert report.confidence == pytest.approx(0.9)


def test_tools_failure_marks_owner_unverified_but_rag_citations_survive(monkeypatch):
    _patch_client(monkeypatch, _tools_down_handler)

    response = client.post("/agent/run", json={"incident": P1_INCIDENT})
    assert response.status_code == 200
    report = TriageReport.model_validate(response.json())

    assert report.owner_team == "unknown"
    assert report.escalation_path == []
    assert "owner_unverified" in report.guardrail_flags
    # RAG still succeeded — its citation must still be present.
    assert any(c.source_type == "runbook" for c in report.citations)
    assert len(report.citations) >= 1


def test_total_dependency_failure_still_produces_valid_report(monkeypatch):
    _patch_client(monkeypatch, _everything_down_handler)

    response = client.post("/agent/run", json={"incident": P1_INCIDENT})
    assert response.status_code == 200, response.text
    report = TriageReport.model_validate(response.json())

    assert report.owner_team == "unknown"
    assert report.escalation_path == []
    assert "owner_unverified" in report.guardrail_flags
    assert "insufficient_citations" in report.guardrail_flags
    assert len(report.citations) >= 1  # schema-enforced non-empty, even degraded


def test_unconfigured_rag_and_tools_urls_degrade_gracefully(monkeypatch):
    monkeypatch.delenv("PETER_RAG_URL", raising=False)
    monkeypatch.delenv("PETER_TOOLS_URL", raising=False)

    def handler(request: httpx.Request) -> httpx.Response:  # should never be called
        raise AssertionError("no HTTP call should be made when URLs are unconfigured")

    _patch_client(monkeypatch, handler)

    response = client.post("/agent/run", json={"incident": P1_INCIDENT})
    assert response.status_code == 200
    report = TriageReport.model_validate(response.json())
    assert report.owner_team == "unknown"
    assert "owner_unverified" in report.guardrail_flags


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "langgraph-agent"}


def test_requires_bearer_token_when_configured(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cret")
    _patch_client(monkeypatch, _healthy_handler)
    response = client.post("/agent/run", json={"incident": P1_INCIDENT})
    assert response.status_code == 401


def test_accepts_valid_bearer_token(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cret")
    _patch_client(monkeypatch, _healthy_handler)
    response = client.post(
        "/agent/run",
        json={"incident": P1_INCIDENT},
        headers={"Authorization": "Bearer s3cret"},
    )
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Infra category path
# ---------------------------------------------------------------------------

REDIS_INFRA_INCIDENT = {
    "id": "inc-redis-infra001",
    "service": "redis-cache",
    "environment": "production",
    "symptom": "cache miss rate elevated, memory usage high",
    "context": {"severity": 4},
}

K8S_INFRA_INCIDENT = {
    "id": "inc-k8s-infra001",
    "service": "k8s-ingress",
    "environment": "production",
    "symptom": "5xx errors from ingress controller",
    "context": {"severity": 3},
}


def test_redis_cache_incident_category_is_infra(monkeypatch):
    """redis-* service names must route to the infra category."""
    _patch_client(monkeypatch, _healthy_handler)

    resp = client.post("/agent/run", json={"incident": REDIS_INFRA_INCIDENT})
    assert resp.status_code == 200, resp.text

    report = TriageReport.model_validate(resp.json())
    assert report.category == "infra"
    assert report.p_level == "P2"  # severity 4 → P2
    assert report.confidence == pytest.approx(0.9)
    assert report.guardrail_flags == []


def test_k8s_ingress_incident_category_is_infra(monkeypatch):
    """k8s-* / ingress service names must route to the infra category."""
    _patch_client(monkeypatch, _healthy_handler)

    resp = client.post("/agent/run", json={"incident": K8S_INFRA_INCIDENT})
    assert resp.status_code == 200, resp.text

    report = TriageReport.model_validate(resp.json())
    assert report.category == "infra"
    assert report.p_level == "P3"  # severity 3 → P3


# ---------------------------------------------------------------------------
# Graph topology: plan → specialists → synthesise
# ---------------------------------------------------------------------------


def test_graph_visits_plan_then_specialists_then_synthesise(monkeypatch):
    """The LangGraph topology must execute nodes in plan → specialists → synthesise order."""
    import langgraph_agent.graph as graph_mod

    visited: list[str] = []

    orig_plan = graph_mod.plan_node
    orig_specialists = graph_mod.specialists_node
    orig_synthesise = graph_mod.synthesise_node

    def tracking_plan(state):
        visited.append("plan")
        return orig_plan(state)

    async def tracking_specialists(state, *, rag_url, tools_url, client):
        visited.append("specialists")
        return await orig_specialists(
            state, rag_url=rag_url, tools_url=tools_url, client=client
        )

    def tracking_synthesise(state):
        visited.append("synthesise")
        return orig_synthesise(state)

    monkeypatch.setattr(graph_mod, "plan_node", tracking_plan)
    monkeypatch.setattr(graph_mod, "specialists_node", tracking_specialists)
    monkeypatch.setattr(graph_mod, "synthesise_node", tracking_synthesise)
    _patch_client(monkeypatch, _healthy_handler)

    resp = client.post("/agent/run", json={"incident": P1_INCIDENT})
    assert resp.status_code == 200, resp.text

    assert visited == ["plan", "specialists", "synthesise"], (
        f"Expected plan → specialists → synthesise, got: {visited}"
    )
