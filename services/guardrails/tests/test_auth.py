"""Bearer auth dependency — only enforced when PETER_SERVICES_TOKEN is set."""

from __future__ import annotations

from fastapi.testclient import TestClient

from guardrails_service.app import app

_SIGNAL = {
    "id": "sig-abc12345",
    "source": "grafana",
    "kind": "alert",
    "received_at": "2026-07-10T10:00:00Z",
    "title": "P1 latency spike on orders-api",
    "body": "",
}


def test_no_auth_required_when_token_unset(monkeypatch) -> None:
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)
    client = TestClient(app)
    resp = client.post("/check/input", json={"signal": _SIGNAL})
    assert resp.status_code == 200


def test_rejects_missing_bearer_token_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cr3t")
    client = TestClient(app)
    resp = client.post("/check/input", json={"signal": _SIGNAL})
    assert resp.status_code == 401


def test_rejects_wrong_bearer_token_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cr3t")
    client = TestClient(app)
    resp = client.post(
        "/check/input",
        json={"signal": _SIGNAL},
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert resp.status_code == 401


def test_accepts_correct_bearer_token_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cr3t")
    client = TestClient(app)
    resp = client.post(
        "/check/input",
        json={"signal": _SIGNAL},
        headers={"Authorization": "Bearer s3cr3t"},
    )
    assert resp.status_code == 200


def test_healthz_never_requires_auth(monkeypatch) -> None:
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cr3t")
    client = TestClient(app)
    resp = client.get("/healthz")
    assert resp.status_code == 200
