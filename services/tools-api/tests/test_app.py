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


def test_audit_requires_token_when_configured(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cr3t")
    resp = client.get("/audit")
    assert resp.status_code == 401


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


# ---------------------------------------------------------------------------
# Audit endpoint: immutability and query bounds
# ---------------------------------------------------------------------------


def test_audit_log_is_append_only_no_delete_route():
    """There must be no DELETE/PATCH route on /audit (immutable log)."""
    resp_delete = client.delete("/audit")
    assert resp_delete.status_code == 405, (
        "DELETE /audit must not be allowed (audit log is append-only)"
    )


def test_audit_log_is_append_only_no_patch_route():
    resp_patch = client.patch("/audit", json={})
    assert resp_patch.status_code in {405, 422}, (
        "PATCH /audit must not be allowed (audit log is append-only)"
    )


def test_audit_capped_at_50_entries():
    """GET /audit must return at most 50 entries even if more exist."""
    report = _sample_report()
    # Write 60 escalations to the same audit DB.
    for i in range(60):
        report_copy = {**report, "incident_id": f"inc-bulk-{i:04d}"}
        resp = client.post(
            "/escalations", json={"report": report_copy, "preview": True}
        )
        assert resp.status_code == 200

    audit_resp = client.get("/audit")
    assert audit_resp.status_code == 200
    entries = audit_resp.json()
    assert len(entries) <= 50, (
        f"Audit returned {len(entries)} entries; expected ≤50"
    )


def test_audit_entries_are_ordered_newest_first():
    """Audit log must be ordered newest-first (DESC created_at)."""
    ids_created: list[str] = []
    report = _sample_report()
    for i in range(3):
        report_copy = {**report, "incident_id": f"inc-order-{i:02d}"}
        resp = client.post(
            "/escalations", json={"report": report_copy, "preview": True}
        )
        assert resp.status_code == 200
        ids_created.append(resp.json()["escalation_id"])

    audit = client.get("/audit").json()
    audit_ids = [e["escalation_id"] for e in audit]
    # Newest-first means the last created escalation appears first.
    assert audit_ids[0] == ids_created[-1], (
        "Expected audit entries in newest-first order"
    )


def test_audit_dispatched_field_is_always_false():
    """Every audit entry must have dispatched=False (preview-only service)."""
    report = _sample_report()
    resp = client.post("/escalations", json={"report": report, "preview": True})
    assert resp.status_code == 200

    audit = client.get("/audit").json()
    assert audit, "expected at least one audit entry"
    for entry in audit:
        assert entry["dispatched"] is False, (
            f"escalation {entry['escalation_id']} has dispatched=True"
        )


# ---------------------------------------------------------------------------
# Preview/live dispatch: must never make external calls
# ---------------------------------------------------------------------------


def test_escalation_preview_never_calls_notification_dispatch(monkeypatch):
    """POST /escalations preview=True must never invoke notification_dispatch."""
    import tools_api.notification_dispatch as nd

    def _forbidden(*args, **kwargs):
        raise AssertionError(
            "notification_dispatch must not be called for preview escalations"
        )

    # Patch every outbound-capable function in the dispatch module.
    for attr in ("send_sms", "send_email", "send_whatsapp", "dispatch"):
        if hasattr(nd, attr):
            monkeypatch.setattr(nd, attr, _forbidden)

    resp = client.post(
        "/escalations", json={"report": _sample_report(), "preview": True}
    )
    assert resp.status_code == 200
    assert resp.json()["preview"] is True


def test_escalation_preview_true_audit_dispatched_false():
    """Explicit preview=True flag must persist in the audit record as dispatched=False."""
    resp = client.post(
        "/escalations", json={"report": _sample_report(), "preview": True}
    )
    assert resp.status_code == 200
    esc_id = resp.json()["escalation_id"]

    audit = client.get("/audit").json()
    entry = next((e for e in audit if e["escalation_id"] == esc_id), None)
    assert entry is not None
    assert entry["dispatched"] is False
    assert entry["preview_requested"] is True
