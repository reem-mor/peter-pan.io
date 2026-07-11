"""POST /check/output — the plan's output-check table (BUILD_PLAN §3, GRD row):
invented owner, destructive step, uncited claim, valid report + verified owner.

The Tools API call inside owner verification is mocked via ``httpx.MockTransport``
injected through the ``get_http_client`` FastAPI dependency override — no real
network call is ever made.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from contextlib import contextmanager
from typing import Any, Callable

import httpx
from fastapi.testclient import TestClient

from guardrails_service.app import app, get_http_client

_VALID_REPORT: dict[str, Any] = {
    "incident_id": "inc-abc12345",
    "category": "infra",
    "p_level": "P2",
    "summary": "Elevated 5xx on orders-api after last deploy.",
    "probable_cause": "Bad config rollout correlated with the deploy window.",
    "citations": [
        {
            "source_id": "runbook-orders-api-5xx",
            "source_type": "runbook",
            "quote": "Roll back the last deploy and monitor error rate for 15 minutes.",
        }
    ],
    "owner_team": "orders-platform",
    "escalation_path": ["orders-platform-oncall"],
    "recommended_steps": [
        "Roll back the last deploy",
        "Monitor error rate for 15 minutes",
    ],
    "confidence": 0.82,
    "guardrail_flags": [],
    "generated_at": "2026-07-10T10:05:00Z",
    "model_meta": {"provider": "fixture", "model_id": "fixture-v1"},
}

Handler = Callable[[httpx.Request], httpx.Response]


@contextmanager
def _tools_api_client(handler: Handler) -> Iterator[TestClient]:
    """Override get_http_client with an httpx.MockTransport-backed client."""

    async def _override() -> AsyncIterator[httpx.AsyncClient]:
        transport = httpx.MockTransport(handler)
        async with httpx.AsyncClient(transport=transport) as client:
            yield client

    app.dependency_overrides[get_http_client] = _override
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_http_client, None)


def test_valid_report_with_verified_owner_passes(monkeypatch) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"teams": ["orders-platform"]})

    with _tools_api_client(handler) as client:
        resp = client.post("/check/output", json={"report": _VALID_REPORT})

    assert resp.status_code == 200
    body = resp.json()
    assert body["passed"] is True
    assert body["flags"] == []


def test_existing_report_flags_fail_closed(monkeypatch) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"teams": ["orders-platform"]})

    report = {**_VALID_REPORT, "guardrail_flags": ["predictor_unverified"]}
    with _tools_api_client(handler) as client:
        response = client.post("/check/output", json={"report": report})

    assert response.json()["passed"] is False
    assert "report_flagged" in response.json()["flags"]


def test_predictor_severity_mismatch_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"teams": ["orders-platform"]})

    report = {
        **_VALID_REPORT,
        "model_meta": {"provider": "fixture-fallback", "predictor_severity": "5"},
    }
    with _tools_api_client(handler) as client:
        response = client.post("/check/output", json={"report": report})

    assert response.json()["passed"] is False
    assert "priority_mismatch" in response.json()["flags"]


def test_required_tool_evidence_fails_when_predictor_metadata_missing(
    monkeypatch,
) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"teams": ["orders-platform"]})

    with _tools_api_client(handler) as client:
        response = client.post(
            "/check/output",
            json={"report": _VALID_REPORT, "require_tool_evidence": True},
        )

    assert response.json()["passed"] is False
    assert "tool_evidence_unverified" in response.json()["flags"]


def test_required_tool_evidence_passes_for_grounded_normal_path(monkeypatch) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"teams": ["orders-platform"]})

    report = {
        **_VALID_REPORT,
        "model_meta": {
            "provider": "fixture-fallback",
            "predictor_severity": "4",
            "evidence": "predictor,rag,service_context",
        },
    }
    with _tools_api_client(handler) as client:
        response = client.post(
            "/check/output",
            json={"report": report, "require_tool_evidence": True},
        )

    assert response.json()["passed"] is True


def test_invented_owner_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200, json={"error": "Unknown owner_team 'orders-platform'"}
        )

    with _tools_api_client(handler) as client:
        resp = client.post("/check/output", json={"report": _VALID_REPORT})

    assert resp.status_code == 200
    body = resp.json()
    assert body["passed"] is False
    assert "owner_unverified" in body["flags"]


def test_missing_tools_url_fails_closed(monkeypatch) -> None:
    monkeypatch.delenv("PETER_TOOLS_URL", raising=False)

    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError(
            "Tools API should not be called when PETER_TOOLS_URL is unset"
        )

    with _tools_api_client(handler) as client:
        resp = client.post("/check/output", json={"report": _VALID_REPORT})

    assert resp.status_code == 200
    body = resp.json()
    assert body["passed"] is False
    assert "owner_unverified" in body["flags"]


def test_destructive_step_fails(monkeypatch) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"teams": ["orders-platform"]})

    report = {
        **_VALID_REPORT,
        "recommended_steps": [
            "rm -rf /var/lib/orders-api/cache",
            "Restart the service",
        ],
    }
    with _tools_api_client(handler) as client:
        resp = client.post("/check/output", json={"report": report})

    assert resp.status_code == 200
    body = resp.json()
    assert body["passed"] is False
    assert "destructive_step" in body["flags"]


def test_uncited_claim_fails(monkeypatch) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"teams": ["orders-platform"]})

    report = {
        **_VALID_REPORT,
        "citations": [
            {
                "source_id": "runbook-orders-api-5xx",
                "source_type": "runbook",
                "quote": "",
            }
        ],
    }
    with _tools_api_client(handler) as client:
        resp = client.post("/check/output", json={"report": report})

    assert resp.status_code == 200
    body = resp.json()
    assert body["passed"] is False
    assert "uncited" in body["flags"]


def test_schema_invalid_report_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:  # pragma: no cover
        raise AssertionError(
            "Tools API should not be called for a schema-invalid report"
        )

    report = {**_VALID_REPORT, "citations": []}
    with _tools_api_client(handler) as client:
        resp = client.post("/check/output", json={"report": report})

    assert resp.status_code == 200
    body = resp.json()
    assert body["passed"] is False
    assert body["flags"] == ["schema_invalid"]


def test_tools_api_network_error_fails_closed(monkeypatch) -> None:
    monkeypatch.setenv("PETER_TOOLS_URL", "http://tools-api.test")

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("simulated timeout", request=request)

    with _tools_api_client(handler) as client:
        resp = client.post("/check/output", json={"report": _VALID_REPORT})

    assert resp.status_code == 200
    body = resp.json()
    assert body["passed"] is False
    assert "owner_unverified" in body["flags"]
