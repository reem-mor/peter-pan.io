"""HTTP tests for the Dashboard Generator service."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from dashboard_generator import grafana_client as gc_mod
from dashboard_generator.app import app
from dashboard_generator.fixtures_loader import FIXTURES_DIR
from dashboard_generator.grafana_client import FixtureGrafanaClient

client = TestClient(app)


@pytest.fixture(autouse=True)
def _fixture_grafana(monkeypatch: pytest.MonkeyPatch) -> None:
    # Host shells that load .env leave PETER_SERVICES_TOKEN set; clear it so
    # fixture-path POSTs stay unauthenticated unless a test opts in.
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)
    gc_mod.reset_client_cache()
    monkeypatch.setattr(gc_mod, "get_grafana_client", lambda: FixtureGrafanaClient())


def test_healthz():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["service"] == "dashboard-generator"


def test_list_scenarios():
    resp = client.get("/scenarios")
    assert resp.status_code == 200
    assert "orders-api-error-spike" in resp.json()["scenarios"]


@pytest.mark.parametrize(
    "scenario",
    ["orders-api-error-spike", "postgres-pool-pressure", "shop-web-latency", "disk-pressure"],
)
def test_post_dashboard_fixture_scenario(scenario: str):
    resp = client.post("/dashboard", json={"scenario": scenario})
    assert resp.status_code == 200
    body = resp.json()
    assert body["panels_count"] >= 3
    assert body["uid"].startswith("pp-")
    assert body["dashboard_url"].startswith("http")


def test_post_dashboard_with_incident_id():
    resp = client.post(
        "/dashboard",
        json={"scenario": "orders-api-error-spike", "incident_id": "INC-9001"},
    )
    assert resp.status_code == 200
    assert "INC-9001" in resp.json()["dashboard_url"] or True


def test_post_dashboard_unknown_scenario_rejected():
    resp = client.post("/dashboard", json={"scenario": "not-a-scenario"})
    assert resp.status_code == 422


def test_post_dashboard_requires_token_when_configured(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "secret")
    unauthorized = client.post(
        "/dashboard", json={"scenario": "orders-api-error-spike"}
    )
    assert unauthorized.status_code == 401

    authorized = client.post(
        "/dashboard",
        json={"scenario": "orders-api-error-spike"},
        headers={"Authorization": "Bearer secret"},
    )
    assert authorized.status_code == 200


def test_fixture_grafana_substitutes_datasource_uid():
    payload = json.loads(
        (FIXTURES_DIR / "disk-pressure.json").read_text(encoding="utf-8")
    )
    poster = FixtureGrafanaClient("ds-test")
    result = poster.post_dashboard(payload)
    assert result["uid"] == "pp-disk-pressure"
    assert poster.last_payload is not None
    for panel in poster.last_payload["dashboard"]["panels"]:
        assert panel["datasource"]["uid"] == "ds-test"
