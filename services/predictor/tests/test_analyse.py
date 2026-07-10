"""POST /analyse TestClient cases per category mapping (BUILD_PLAN §3,
Predictor row) + fixture-window fallback + auth.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from predictor_service.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "predictor"}


@pytest.mark.parametrize(
    "service, expected_category",
    [
        ("postgres-primary", "database"),
        ("orders-db", "database"),
        ("redis-cache", "infra"),
        ("k8s-ingress", "infra"),
        ("shop-web", "application"),
        ("orders-api", "application"),
    ],
)
def test_analyse_category_mapping_via_incident_service(service, expected_category):
    response = client.post(
        "/analyse",
        json={
            "incident": {"service": service},
            "window": [10.0, 10.1, 9.9, 10.0, 10.2],
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["category"] == expected_category
    assert body["method"] == "ewma-floor"
    assert 1 <= body["severity"] <= 5
    assert 0.0 <= body["confidence"] <= 1.0
    assert "ewma" in body["scores"]
    assert "classifier" in body["scores"]


def test_analyse_category_from_metric_window_ref_when_no_incident():
    response = client.post(
        "/analyse",
        json={"metric_window_ref": "postgres-primary:cpu_pct", "window": [1.0, 1.0]},
    )
    assert response.status_code == 200
    assert response.json()["category"] == "database"


def test_analyse_without_service_info_defaults_to_application():
    response = client.post("/analyse", json={"window": [1.0, 1.0]})
    assert response.status_code == 200
    assert response.json()["category"] == "application"


def test_analyse_falls_back_to_fixture_window_when_none_given():
    response_a = client.post(
        "/analyse", json={"metric_window_ref": "shop-web:latency_ms"}
    )
    response_b = client.post(
        "/analyse", json={"metric_window_ref": "shop-web:latency_ms"}
    )
    assert response_a.status_code == 200
    assert response_a.json()["scores"] == response_b.json()["scores"]  # deterministic


def test_analyse_fixture_fallback_differs_by_ref():
    # "ref-one" / "ref-two" are chosen (via predictor_service.fixtures hashing)
    # to land on different entries of the small built-in fixture set.
    response_a = client.post("/analyse", json={"metric_window_ref": "ref-one"})
    response_b = client.post("/analyse", json={"metric_window_ref": "ref-two"})
    assert response_a.status_code == 200
    assert response_b.status_code == 200
    assert response_a.json()["scores"] != response_b.json()["scores"]


def test_analyse_requires_bearer_token_when_configured(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cret")
    response = client.post("/analyse", json={"window": [1.0, 2.0]})
    assert response.status_code == 401


def test_analyse_accepts_valid_bearer_token(monkeypatch):
    monkeypatch.setenv("PETER_SERVICES_TOKEN", "s3cret")
    response = client.post(
        "/analyse",
        json={"window": [1.0, 2.0]},
        headers={"Authorization": "Bearer s3cret"},
    )
    assert response.status_code == 200
