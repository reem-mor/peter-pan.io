"""Integration tests for structured incident analysis (data/ + runbooks manifest)."""

from __future__ import annotations

import pytest

from tools_api.incident_analysis import analyze_incident, compose_triage_sections


@pytest.fixture
def storm_alert() -> dict:
    return {
        "service": "orders-api",
        "environment": "production",
        "severity": "P1",
        "symptom": "CRITICAL: orders-api error rate 100% following deploy",
        "alert_time": "2026-06-15T10:02:55Z",
        "error_rate_pct": 100,
        "affected_users": 18500,
        "duration_minutes": 45,
    }


def test_priority_raises_p3_to_p2_on_revenue():
    from tools_api.incident_analysis import _classify_priority

    alert = {"severity": "P3", "error_rate_pct": 1.0, "service": "orders-api"}
    impact = {"cost_per_minute": 2000, "regulatory_exposure": []}
    priority = _classify_priority(alert=alert, impact=impact, source_dir=None)
    assert priority["priority"] == "P2"


def test_orders_api_production_p1_full_flow(storm_alert: dict):
    analysis = analyze_incident(storm_alert)
    assert "error" not in analysis

    owner = analysis["owner"]
    assert owner["owner_team"] == "App Platform"

    deploys = analysis["deployments"]
    assert deploys.get("likely_deploy_correlation") is True
    assert any(d["service"] == "orders-api" for d in deploys.get("deployments", []))

    impact = analysis["impact"]
    assert impact.get("cost_per_minute") == pytest.approx(6200, rel=0.01)
    assert impact.get("active_users") == pytest.approx(18500, rel=0.01)
    regulatory = " ".join(impact.get("regulatory_exposure", [])).upper()
    assert "SOC2" in regulatory

    priority = analysis["priority"]
    assert priority["priority"] == "P1"
    assert priority.get("rationale")

    escalation = analysis["escalation"]
    assert escalation.get("war_room_required") is True
    overrides = escalation.get("compliance_overrides") or []
    assert any(o.get("compliance_tag") == "SOC2" for o in overrides)

    similar = analysis["similar_incidents"].get("similar_incidents", [])
    assert any(inc.get("incident_id") == "INC-20251104-001" for inc in similar)

    kb = analysis["knowledge_base"]
    assert kb.get("found") is True
    assert kb.get("runbook_file") == "deployment_rollback.json"

    sections = compose_triage_sections(analysis)
    structured = sections.get("structured_sections") or {}
    assert structured.get("triage_plan")

    sources = analysis.get("sources", [])
    assert any("deployment_rollback.json" in str(s) for s in sources)
