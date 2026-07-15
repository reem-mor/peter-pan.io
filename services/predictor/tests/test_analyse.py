"""POST /analyse tests for the typed six-class response (BUILD_PLAN §3,
Predictor row), fixture-window fallback, and auth.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from predictor_service.app import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)


@pytest.fixture()
def _stub_engine(monkeypatch):
    """Pin the fixed-weight stub for tests asserting stub-specific
    window-shape behaviour (the torch checkpoint would answer otherwise)."""
    monkeypatch.setenv("PETER_PREDICTOR_ENGINE", "stub")


def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "predictor"}


@pytest.mark.parametrize(
    ("symptom", "expected_incident_class"),
    [
        ("CPU saturation and run queue growth", "cpu_saturation"),
        ("memory leak with monotonic heap growth", "memory_leak"),
        ("database deadlock and lock waits", "db_lock_contention"),
        ("postgres replication lag increasing", "replication_lag"),
        ("HTTP 5xx error rate spike", "error_rate_spike"),
    ],
)
def test_analyse_returns_fine_grained_incident_class(
    symptom, expected_incident_class
):
    response = client.post(
        "/analyse",
        json={
            "incident": {"service": "orders-api", "symptom": symptom},
            "window": [10.0, 10.0, 10.0, 10.0],
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["incident_class"] == expected_incident_class
    assert "category" not in body
    assert body["method"] == "ewma-floor"
    assert 1 <= body["severity"] <= 5
    assert 0.0 <= body["confidence"] <= 1.0
    assert "ewma" in body["scores"]
    assert "classifier" in body["scores"]


def test_analyse_incident_class_from_metric_window_ref_when_no_incident():
    response = client.post(
        "/analyse",
        json={
            "metric_window_ref": "postgres-primary:replication_lag",
            "window": [1.0, 1.0],
        },
    )
    assert response.status_code == 200
    assert response.json()["incident_class"] == "replication_lag"


def test_analyse_flat_window_without_context_defaults_to_normal():
    response = client.post("/analyse", json={"window": [1.0, 1.0, 1.0]})
    assert response.status_code == 200
    assert response.json()["incident_class"] == "normal"


def test_analyse_openapi_response_model_uses_incident_class_enum():
    schema = client.get("/openapi.json").json()
    response_schema = schema["components"]["schemas"]["AnalyseResponse"]
    incident_class = response_schema["properties"]["incident_class"]

    assert set(incident_class["enum"]) == {
        "cpu_saturation",
        "memory_leak",
        "db_lock_contention",
        "replication_lag",
        "error_rate_spike",
        "normal",
    }
    assert "category" not in response_schema["properties"]


def test_analyse_rejects_unknown_model_class_to_normal_low_confidence(
    monkeypatch, _stub_engine
):
    monkeypatch.setattr(
        "predictor_service.app.classify",
        lambda _window, *, context: {
            "incident_class": "invented_class",
            "confidence": 0.99,
        },
    )

    response = client.post("/analyse", json={"window": [1.0, 2.0]})

    assert response.status_code == 200
    assert response.json()["incident_class"] == "normal"
    assert response.json()["confidence"] <= 0.2
    assert response.json()["scores"]["classifier"]["fallback"] == "unknown_class"


def test_analyse_marks_normal_class_with_anomalous_ewma_as_conflict(_stub_engine):
    response = client.post(
        "/analyse",
        json={"window": [10.0] * 9 + [11.3]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["incident_class"] == "normal"
    assert body["severity"] == 5
    assert body["confidence"] <= 0.2
    assert body["scores"]["classifier"]["fallback"] == "severity_conflict"


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
