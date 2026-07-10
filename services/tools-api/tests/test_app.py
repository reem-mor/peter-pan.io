"""FastAPI route tests for the Tools API service."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from tools_api.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_audit_db(tmp_path, monkeypatch):
    """Point every test at its own throwaway audit DB (never the repo's)."""
    monkeypatch.setenv("TOOLS_AUDIT_DB", str(tmp_path / "audit.sqlite"))
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)
    yield


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "service": "tools-api"}


def test_recent_deployments_happy_path():
    resp = client.post(
        "/tools/recent_deployments",
        json={
            "service": "orders-api",
            "environment": "production",
            "alert_time": "2026-06-15T10:02:55Z",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["likely_deploy_correlation"] is True
    assert body["suspect_deployment"]["service"] == "orders-api"


def test_recent_deployments_unknown_service_is_404():
    resp = client.post(
        "/tools/recent_deployments",
        json={
            "service": "ghost-svc",
            "environment": "production",
            "alert_time": "2026-06-15T10:02:55Z",
        },
    )
    assert resp.status_code == 404


def test_service_context_happy_path():
    resp = client.post(
        "/tools/service_context",
        json={"service": "orders-api", "severity": "P1", "environment": "production"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["owner_team"] == "App Platform"
    assert body["slack_channel"] == "#app-platform"
    assert body["business_impact"]["revenue_impact_usd_per_hour"] == 372000


def test_service_context_unknown_service_is_404():
    resp = client.post("/tools/service_context", json={"service": "ghost-svc"})
    assert resp.status_code == 404


def test_similar_incidents_happy_path():
    resp = client.post(
        "/tools/similar_incidents",
        json={
            "service": "orders-api",
            "symptom": "100% error rate nodes unresponsive outage",
            "environment": "production",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] >= 1
    assert body["similar_incidents"][0]["resolution"]


def _sample_report() -> dict:
    return {
        "incident_id": "inc-orders-api-p1-0001",
        "category": "application",
        "p_level": "P1",
        "summary": "orders-api error rate 100% following a bad deploy.",
        "probable_cause": "Connection pool exhaustion from a retry storm after DEP-20260615-002.",
        "citations": [
            {
                "source_id": "deployment_rollback.json",
                "source_type": "runbook",
                "quote": "Roll back and validate downstream health.",
            }
        ],
        "owner_team": "App Platform",
        "escalation_path": [],
        "recommended_steps": [
            "Roll back the deploy",
            "Validate downstream payment calls",
        ],
        "confidence": 0.9,
        "guardrail_flags": [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model_meta": {"provider": "fixture", "model": "test"},
    }


def test_post_escalation_is_preview_only_and_audited():
    resp = client.post(
        "/escalations", json={"report": _sample_report(), "preview": True}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["preview"] is True
    assert body["escalation_id"].startswith("ESC-")
    assert body["message"]
    assert body["escalation_path"]

    audit_resp = client.get("/audit")
    assert audit_resp.status_code == 200
    entries = audit_resp.json()
    assert len(entries) == 1
    assert entries[0]["escalation_id"] == body["escalation_id"]
    assert entries[0]["dispatched"] is False


def test_post_escalation_unknown_team_is_404():
    report = _sample_report()
    report["owner_team"] = "Nonexistent Team"
    resp = client.post("/escalations", json={"report": report, "preview": True})
    assert resp.status_code == 404


def test_audit_empty_by_default():
    resp = client.get("/audit")
    assert resp.status_code == 200
    assert resp.json() == []


def test_bearer_token_required_when_configured(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cr3t")
    resp = client.post(
        "/tools/similar_incidents",
        json={"service": "orders-api", "symptom": "outage"},
    )
    assert resp.status_code == 401

    resp_ok = client.post(
        "/tools/similar_incidents",
        json={"service": "orders-api", "symptom": "outage"},
        headers={"Authorization": "Bearer s3cr3t"},
    )
    assert resp_ok.status_code == 200


def test_bearer_token_not_required_on_healthz(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cr3t")
    resp = client.get("/healthz")
    assert resp.status_code == 200
