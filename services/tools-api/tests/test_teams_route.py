"""GET /teams — the owner-verification seam consumed by the Guardrails service."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tools_api.app import app

client = TestClient(app)


def test_teams_lists_all_owning_teams() -> None:
    resp = client.get("/teams")
    assert resp.status_code == 200
    teams = resp.json()["teams"]
    assert teams == sorted(teams)
    for team in ("App Platform", "Database Reliability", "Infra SRE"):
        assert team in teams


def test_teams_requires_bearer_when_token_set(monkeypatch) -> None:
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "sekrit")
    assert client.get("/teams").status_code in (401, 403)
    ok = client.get("/teams", headers={"Authorization": "Bearer sekrit"})
    assert ok.status_code == 200
