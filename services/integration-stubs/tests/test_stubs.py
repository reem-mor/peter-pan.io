"""Tests for local integration stubs."""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import integration_stubs.app as app_module
from integration_stubs.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_runtime(monkeypatch):
    monkeypatch.delenv("PETER_WEBHOOK_SECRET", raising=False)
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)
    client.delete("/deliveries")


def test_github_deployments_fixture():
    response = client.get("/github/deployments")
    assert response.status_code == 200
    assert response.json()["deployments"]


def test_team_webhook_records_delivery():
    response = client.post("/teams/database", json={"summary": "test"})
    assert response.status_code == 200
    deliveries = client.get("/deliveries").json()
    assert len(deliveries) == 1


def test_review_queue_records_flagged_report():
    response = client.post(
        "/review-queue",
        json={"incident_id": "inc-review001", "guardrail_flags": ["invented-owner"]},
    )

    assert response.status_code == 202
    assert response.json() == {"status": "accepted", "queue": "human-review"}
    assert client.get("/deliveries").json() == [
        {
            "channel": "review",
            "payload": {
                "incident_id": "inc-review001",
                "guardrail_flags": ["invented-owner"],
            },
        }
    ]


def test_review_queue_accepts_internal_service_token(monkeypatch):
    monkeypatch.setenv("PETER_WEBHOOK_SECRET", "webhook-secret")
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "service-token")

    response = client.post(
        "/review-queue",
        headers={"Authorization": "Bearer service-token"},
        json={"incident_id": "inc-review002"},
    )

    assert response.status_code == 202


def test_slack_stub_requires_and_accepts_internal_token(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "service-token")

    rejected = client.post("/slack", json={"summary": "test"})
    accepted = client.post(
        "/slack",
        headers={"Authorization": "Bearer service-token"},
        json={"summary": "test"},
    )

    assert rejected.status_code == 401
    assert accepted.status_code == 200
    assert client.get(
        "/deliveries",
        headers={"Authorization": "Bearer service-token"},
    ).json() == [
        {"channel": "slack", "payload": {"summary": "test"}}
    ]


def test_team_webhook_accepts_internal_service_token(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "service-token")

    response = client.post(
        "/teams/infra",
        headers={"Authorization": "Bearer service-token"},
        json={"summary": "test"},
    )

    assert response.status_code == 200


def test_delivery_state_requires_internal_auth_when_configured(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "service-token")
    headers = {"Authorization": "Bearer service-token"}

    assert client.get("/deliveries").status_code == 401
    assert client.delete("/deliveries").status_code == 401
    assert client.get("/deliveries", headers=headers).status_code == 200
    assert client.delete("/deliveries", headers=headers).status_code == 200


def test_webhook_secret_uses_constant_time_comparison(monkeypatch):
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
    monkeypatch.setenv("PETER_WEBHOOK_SECRET", "expected-secret")

    response = client.post(
        "/teams/database",
        headers={"X-Peter-Webhook-Secret": "wrong-secret"},
        json={"summary": "test"},
    )

    assert response.status_code == 401
    assert calls == [("wrong-secret", "expected-secret")]
