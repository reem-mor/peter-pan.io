"""Ingestion Service tests: schema accept/reject table, contract round-trip,
forwarding (httpx.MockTransport / monkeypatch — no real network), auth.
"""

from __future__ import annotations

import json as jsonlib

import httpx
import pytest
from fastapi.testclient import TestClient

from ingestion_service import app as app_module
from ingestion_service.contracts import Signal

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Every test starts with no n8n URL and no auth token unless it opts in."""
    monkeypatch.delenv("N8N_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)


def _valid_payload(**overrides) -> dict:
    payload = {
        "id": "sig-abc12345",
        "source": "grafana",
        "kind": "alert",
        "received_at": "2026-07-10T12:00:00Z",
        "title": "high error rate",
        "body": "",
        "service": None,
        "environment": None,
        "severity_hint": None,
        "labels": {},
        "raw": {},
    }
    payload.update(overrides)
    return payload


# ---------------------------------------------------------------------------
# Schema accept/reject table (BUILD_PLAN §3, Ingestion API row)
# ---------------------------------------------------------------------------

ACCEPT_CASES = {
    "minimal_grafana_alert": _valid_payload(),
    "manual_webui_signal": _valid_payload(
        id="sig-webui0001",
        source="webui",
        kind="manual",
        title="manual incident report",
        service="Shop Web",
        environment="production",
    ),
    "github_deploy_event": _valid_payload(
        id="sig-deploy0001",
        source="github",
        kind="deploy_event",
        title="deploy shop-web v1.2.3",
        severity_hint="info",
    ),
    "slack_complaint_with_labels_and_raw": _valid_payload(
        id="sig-complaint01",
        source="slack",
        kind="complaint",
        title="users reporting checkout errors",
        body="multiple reports in #support",
        severity_hint="warning",
        labels={"team": "orders"},
        raw={"channel": "#support", "message_ts": "1720000000.000100"},
    ),
}

REJECT_CASES = {
    "bad_id_pattern_uppercase": _valid_payload(id="SIG-ABC12345"),
    "bad_id_pattern_too_short": _valid_payload(id="sig-a1"),
    "missing_title": {k: v for k, v in _valid_payload().items() if k != "title"},
    "empty_title": _valid_payload(title=""),
    "invalid_source_literal": _valid_payload(source="pagerduty"),
    "invalid_kind_literal": _valid_payload(kind="ping"),
    "extra_field_forbidden": _valid_payload(unexpected_field="nope"),
    "missing_received_at": {
        k: v for k, v in _valid_payload().items() if k != "received_at"
    },
    "title_too_long": _valid_payload(title="x" * 301),
}


@pytest.mark.parametrize("payload", ACCEPT_CASES.values(), ids=ACCEPT_CASES.keys())
def test_accepts_valid_signals(payload):
    response = client.post("/signals", json=payload)
    assert response.status_code == 202, response.text
    body = response.json()
    assert body["forwarded"] is False
    assert body["reason"] == "n8n webhook not configured"


@pytest.mark.parametrize("payload", REJECT_CASES.values(), ids=REJECT_CASES.keys())
def test_rejects_invalid_signals(payload):
    response = client.post("/signals", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_contract_round_trip():
    payload = _valid_payload(service="Orders API")
    signal = Signal.model_validate(payload)
    assert signal.id == "sig-abc12345"
    dumped = signal.model_dump(mode="json")
    reloaded = Signal.model_validate(dumped)
    assert reloaded == signal


# ---------------------------------------------------------------------------
# Forwarding — httpx.MockTransport, no real network
# ---------------------------------------------------------------------------


def test_forwards_to_n8n_when_configured(monkeypatch):
    monkeypatch.setenv("N8N_WEBHOOK_URL", "https://n8n.example.test/webhook/peter-pan")

    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = request.content
        return httpx.Response(200, json={"ok": True})

    def fake_build_client():
        return httpx.AsyncClient(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(app_module, "_build_client", fake_build_client)

    payload = _valid_payload(id="sig-fwdtest01", service="Payments API")
    response = client.post("/signals", json=payload)

    assert response.status_code == 202
    body = response.json()
    assert body["forwarded"] is True
    assert body["signal_id"] == "sig-fwdtest01"
    assert body["n8n_status"] == 200
    assert body["n8n_response"] == {"ok": True}
    assert captured["url"] == "https://n8n.example.test/webhook/peter-pan"

    forwarded_body = jsonlib.loads(captured["body"])
    assert forwarded_body["service"] == "payments-api"  # normalized before forwarding
    assert forwarded_body["id"] == "sig-fwdtest01"


def test_forwarding_failure_degrades_gracefully(monkeypatch):
    monkeypatch.setenv("N8N_WEBHOOK_URL", "https://n8n.example.test/webhook/peter-pan")

    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        raise httpx.ConnectError("connection refused", request=request)

    def fake_build_client():
        return httpx.AsyncClient(transport=httpx.MockTransport(handler))

    monkeypatch.setattr(app_module, "_build_client", fake_build_client)

    payload = _valid_payload(id="sig-failtest01")
    response = client.post("/signals", json=payload)

    assert response.status_code == 202  # ingestion still ack's; degrades gracefully
    body = response.json()
    assert body["forwarded"] is False
    assert body["signal_id"] == "sig-failtest01"
    assert "reason" in body
    assert attempts["count"] == 2  # initial attempt + 1 retry


def test_unconfigured_n8n_still_validates_and_returns_202():
    payload = _valid_payload(id="sig-noconfig01")
    response = client.post("/signals", json=payload)
    assert response.status_code == 202
    assert response.json() == {
        "forwarded": False,
        "reason": "n8n webhook not configured",
    }


# ---------------------------------------------------------------------------
# Bearer auth
# ---------------------------------------------------------------------------


def test_healthz_never_requires_auth(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cret")
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "ingestion"}


def test_signals_requires_bearer_token_when_configured(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cret")
    payload = _valid_payload(id="sig-authtest1")
    response = client.post("/signals", json=payload)
    assert response.status_code == 401


def test_signals_accepts_valid_bearer_token(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cret")
    payload = _valid_payload(id="sig-authtest2")
    response = client.post(
        "/signals", json=payload, headers={"Authorization": "Bearer s3cret"}
    )
    assert response.status_code == 202
