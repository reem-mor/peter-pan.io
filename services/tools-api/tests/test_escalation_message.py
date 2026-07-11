"""Tests for escalation message formatting."""

from __future__ import annotations

from tools_api.escalation_message import (
    enrich_escalation_context,
    format_escalation_messages,
)


def test_format_escalation_email_includes_on_call_and_war_room():
    ctx = {
        "incident_id": "ALT-DEMO-P1-001",
        "severity": "P1",
        "service": "orders-api",
        "environment": "production",
        "incident_title": "Order intake failure after deployment",
        "on_call_name": "Primary App Platform On-Call",
        "owner_team": "App Platform",
        "slack_channel": "#app-platform",
        "war_room_channel": "#war-room",
        "business_impact": "Complete order intake outage; revenue and fulfillment exposure.",
        "support_complaints": "47 CS tickets (+35% vs baseline).",
        "top_error": "order_submit_failed +280%",
        "recent_deployment": "v4.3.0 (27m ago)",
        "recommended_actions": [
            "Rollback orders-api canary",
            "Validate downstream payment calls",
        ],
        "runbook_count": 5,
        "runbook_name": "deployment_rollback.json",
    }
    formatted = format_escalation_messages(ctx, channel="email")
    body = formatted["body"]
    assert "Hey Primary App Platform On-Call" in body
    assert "#war-room" in body
    assert "order_submit_failed +280%" in body
    assert "Business impact" in body or "BUSINESS IMPACT" in body
    assert formatted["html_body"]
    assert "Order intake failure after deployment" in formatted["subject"]


def test_format_escalation_sms_is_concise():
    ctx = {
        "incident_id": "INC-1",
        "severity": "P1",
        "service": "orders-api",
        "incident_title": "100% error rate",
        "on_call_name": "Primary App Platform On-Call",
        "business_impact": "$372k/hr exposure",
        "top_error": "HTTP 5xx spike",
        "war_room_channel": "#war-room",
    }
    sms = format_escalation_messages(ctx, channel="sms")["body"]
    assert "Primary App Platform On-Call" in sms
    assert "war-room" in sms
    assert "@" not in sms
    assert len(sms) <= 160


def test_enrich_escalation_context_fills_owner_from_catalog():
    ctx = enrich_escalation_context(
        {"incident_title": "P1 orders-api outage"},
        incident_id="ALT-1",
        service="orders-api",
        severity="P1",
    )
    assert ctx["on_call_name"]
    assert ctx["owner_team"]
    assert ctx.get("business_impact")
