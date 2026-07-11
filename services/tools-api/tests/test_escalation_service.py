"""Tests for the preview-first escalation service (no Lambda, no dispatch)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tools_api.contracts import Citation, TriageReport
from tools_api.escalation_service import (
    EscalationServiceError,
    build_escalation_preview,
    create_escalation,
    list_audit_entries,
    mask_recipient,
    record_audit_entry,
    resolve_demo_recipients,
)


def _report(**overrides) -> TriageReport:
    fields = {
        "incident_id": "inc-orders-api-p1-0001",
        "category": "application",
        "p_level": "P1",
        "summary": "orders-api error rate 100% following a bad deploy.",
        "probable_cause": "Connection pool exhaustion from a retry storm after DEP-20260615-002.",
        "citations": [
            Citation(
                source_id="deployment_rollback.json",
                source_type="runbook",
                quote="Roll back and validate.",
            ),
        ],
        "owner_team": "App Platform",
        "escalation_path": [],
        "recommended_steps": [
            "Roll back the deploy",
            "Validate downstream payment calls",
        ],
        "confidence": 0.9,
        "guardrail_flags": [],
        "generated_at": datetime.now(timezone.utc),
        "model_meta": {"provider": "fixture", "model": "test"},
    }
    fields.update(overrides)
    return TriageReport(**fields)


def test_mask_recipient_short_and_long():
    assert mask_recipient("") == ""
    assert mask_recipient("ab") == "**"
    assert mask_recipient("oncall@example.com") == "on***om"


def test_resolve_demo_recipients_from_env(monkeypatch):
    monkeypatch.setenv("PETER_ESCALATION_EMAIL", "a@example.com, b@example.com")
    recipients = resolve_demo_recipients("email")
    assert recipients == ["a@example.com", "b@example.com"]


def test_resolve_demo_recipients_empty_when_unset(monkeypatch):
    monkeypatch.delenv("PETER_ESCALATION_EMAIL", raising=False)
    monkeypatch.delenv("PETER_DEMO_EMAIL_RECIPIENT", raising=False)
    assert resolve_demo_recipients("email") == []


def test_build_escalation_preview_never_dispatches():
    report = _report()
    result = build_escalation_preview(report=report)
    assert result["preview"] is True
    assert result["escalation_id"].startswith("ESC-")
    assert result["owner_team"] == "App Platform"
    assert result["service"] in {"shop-web", "orders-api", "payments-api"}
    assert result["war_room_required"] is True
    assert result["escalation_path"]
    # No dispatch channel/recipient ever appears in the result — preview only.
    assert "dispatched" not in result
    assert "recipient" not in result


def test_build_escalation_preview_uses_report_escalation_path_when_present():
    report = _report(escalation_path=["On-call human", "Secondary human"])
    result = build_escalation_preview(report=report)
    assert result["escalation_path"] == ["On-call human", "Secondary human"]


def test_build_escalation_preview_unknown_team_raises():
    report = _report(owner_team="Nonexistent Team")
    with pytest.raises(EscalationServiceError):
        build_escalation_preview(report=report)


def test_create_escalation_and_audit_round_trip(tmp_path):
    db_path = tmp_path / "audit.sqlite"
    report = _report()
    result = create_escalation(report=report, preview=True, db_path=db_path)

    entries = list_audit_entries(db_path=db_path)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["escalation_id"] == result["escalation_id"]
    assert entry["dispatched"] is False
    assert entry["preview_requested"] is True
    assert entry["escalation_path"] == result["escalation_path"]


def test_list_audit_entries_orders_newest_first(tmp_path):
    db_path = tmp_path / "audit.sqlite"
    for i in range(3):
        record_audit_entry(
            {
                "escalation_id": f"ESC-TEST-{i}",
                "incident_id": f"inc-{i}",
                "service": "orders-api",
                "owner_team": "App Platform",
                "p_level": "P2",
                "preview_requested": True,
                "message": "test",
                "escalation_path": ["Primary App Platform On-Call"],
                "created_at": f"2026-06-15T10:0{i}:00+00:00",
            },
            db_path=db_path,
        )
    entries = list_audit_entries(db_path=db_path)
    assert [e["escalation_id"] for e in entries] == [
        "ESC-TEST-2",
        "ESC-TEST-1",
        "ESC-TEST-0",
    ]


def test_list_audit_entries_respects_limit(tmp_path):
    db_path = tmp_path / "audit.sqlite"
    for i in range(5):
        record_audit_entry(
            {
                "escalation_id": f"ESC-LIMIT-{i}",
                "incident_id": f"inc-{i}",
                "service": "orders-api",
                "owner_team": "App Platform",
                "p_level": "P3",
                "preview_requested": True,
                "message": "test",
                "escalation_path": [],
                "created_at": f"2026-06-15T11:0{i}:00+00:00",
            },
            db_path=db_path,
        )
    entries = list_audit_entries(limit=2, db_path=db_path)
    assert len(entries) == 2
