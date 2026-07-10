"""Unit tests for enrichment tools against the canonical data/ demo scenarios."""

from __future__ import annotations

from pathlib import Path

from tools_api.enrichment_tools import (
    correlate_deployments,
    enrich_triage_demo,
    find_similar_incidents,
    lookup_owner,
    score_business_impact,
)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

DEMO = {
    "service": "payments-api",
    "environment": "production",
    "severity": "P2",
    "symptom": "payment authorization latency and timeout errors",
    "alert_time": "2026-06-15T10:40:00Z",
}


def test_correlate_deployments_demo():
    result = correlate_deployments(
        service=DEMO["service"],
        environment=DEMO["environment"],
        alert_time=DEMO["alert_time"],
    )
    assert "error" not in result
    assert result["environment"] == "production"
    assert "deployments" in result


def test_lookup_owner_demo():
    result = lookup_owner(service=DEMO["service"], environment=DEMO["environment"])
    assert result["owner_team"] == "App Platform"
    assert "App Platform" in result["escalation_path"] or result["escalation_path"]


def test_score_business_impact_demo():
    result = score_business_impact(
        service=DEMO["service"],
        environment=DEMO["environment"],
        severity=DEMO["severity"],
    )
    assert result["revenue_impact_usd_per_hour"] > 0
    assert "regulatory_flag" in result


def test_find_similar_incidents_demo():
    result = find_similar_incidents(
        service="orders-api", symptom="100% error rate outage"
    )
    assert result["count"] >= 1


def test_enrich_triage_demo_bundle():
    bundle = enrich_triage_demo()
    assert bundle["correlate_deployments"]["likely_deploy_correlation"] is True
    assert bundle["lookup_owner"]["owner_team"] == "App Platform"
    assert bundle["score_business_impact"]["tier"] == 0
    assert bundle["find_similar_incidents"]["count"] >= 1


STORM = {
    "service": "orders-api",
    "environment": "production",
    "severity": "P1",
    "symptom": "CRITICAL: orders-api error rate 100% following deploy",
    "alert_time": "2026-06-15T10:02:55Z",
}


def test_orders_api_storm_enrichment():
    owner = lookup_owner(
        service=STORM["service"],
        environment=STORM["environment"],
        data_dir=DATA_DIR,
    )
    assert "error" not in owner
    assert owner["owner_team"] == "App Platform"

    deploys = correlate_deployments(
        service=STORM["service"],
        environment=STORM["environment"],
        alert_time=STORM["alert_time"],
        data_dir=DATA_DIR,
    )
    assert "error" not in deploys
    assert deploys["likely_deploy_correlation"] is True

    impact = score_business_impact(
        service=STORM["service"],
        environment=STORM["environment"],
        severity=STORM["severity"],
        alert=STORM,
        data_dir=DATA_DIR,
    )
    assert impact["sla_risk"] == "critical"
    assert impact["revenue_impact_usd_per_hour"] == 372000

    similar = find_similar_incidents(
        service=STORM["service"],
        symptom=STORM["symptom"],
        environment=STORM["environment"],
        data_dir=DATA_DIR,
    )
    assert similar["count"] >= 1
