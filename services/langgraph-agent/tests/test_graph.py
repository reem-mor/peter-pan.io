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
