"""Grafana client tests (fixture mode — no network)."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from dashboard_generator import grafana_client as gc_mod
from dashboard_generator.fixtures_loader import FIXTURES_DIR
from dashboard_generator.grafana_client import (
    FixtureGrafanaClient,
    GrafanaClient,
    _fetch_prometheus_uid,
    get_grafana_client,
    reset_client_cache,
)


def test_fixture_client_posts_valid_dashboard():
    payload = json.loads(
        (FIXTURES_DIR / "postgres-pool-pressure.json").read_text(encoding="utf-8")
    )
    client = FixtureGrafanaClient("ds-1")
    result = client.post_dashboard(payload)
    assert result["uid"] == "pp-postgres-pool"
    assert client.last_payload is not None
    assert client.last_payload["dashboard"]["panels"][0]["datasource"]["uid"] == "ds-1"


def test_grafana_client_substitute_and_post(monkeypatch):
    payload = json.loads(
        (FIXTURES_DIR / "disk-pressure.json").read_text(encoding="utf-8")
    )

    class _Response:
        status_code = 200

        @staticmethod
        def json() -> dict:
            return {"url": "/d/pp-disk-pressure", "uid": "pp-disk-pressure"}

        text = ""

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def post(self, url, headers=None, json=None):
            assert headers["Authorization"] == "Bearer test-token"
            assert json["dashboard"]["panels"][0]["datasource"]["uid"] == "prom-uid"
            return _Response()

    monkeypatch.setattr(httpx, "Client", _Client)
    client = GrafanaClient("http://grafana:3000", "test-token", "prom-uid")
    result = client.post_dashboard(payload)
    assert result["uid"] == "pp-disk-pressure"


def test_fetch_prometheus_uid_picks_first_prometheus(monkeypatch):
    class _Response:
        status_code = 200

        @staticmethod
        def json():
            return [
                {"type": "loki", "uid": "loki-1"},
                {"type": "prometheus", "uid": "prom-42"},
            ]

        text = ""

    class _Client:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def get(self, url, headers=None):
            return _Response()

    monkeypatch.setattr(httpx, "Client", _Client)
    assert _fetch_prometheus_uid("http://localhost:3000", "token") == "prom-42"


def test_get_grafana_client_uses_fixture_when_token_unset(monkeypatch):
    reset_client_cache()
    monkeypatch.delenv("GRAFANA_API_TOKEN", raising=False)
    client = get_grafana_client()
    assert isinstance(client, FixtureGrafanaClient)


def test_get_grafana_client_caches_instance(monkeypatch):
    reset_client_cache()
    monkeypatch.delenv("GRAFANA_API_TOKEN", raising=False)
    assert get_grafana_client() is get_grafana_client()
