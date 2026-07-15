"""Trained-checkpoint serving path (``torch_classifier.py`` + app wiring).

Skipped wholesale when torch is not installed — the service then degrades to
the fixed-weight stub, which keeps its own suite. The committed artifact
``predictor_service/artifacts/predictor.pth`` is part of the deployment unit,
so these tests treat its absence as a failure, not a skip.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

torch = pytest.importorskip("torch")

from predictor_service import torch_classifier  # noqa: E402
from predictor_service.app import app  # noqa: E402

client = TestClient(app)

ARTIFACTS = Path(torch_classifier.DEFAULT_MODEL_PATH).parent


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)
    monkeypatch.delenv("PETER_PREDICTOR_ENGINE", raising=False)
    monkeypatch.delenv("PETER_PREDICTOR_MODEL_PATH", raising=False)


def test_committed_artifacts_exist():
    assert (ARTIFACTS / "predictor.pth").is_file()
    metrics = json.loads((ARTIFACTS / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["test_accuracy"] > 0.75
    assert set(metrics["per_class"]) == set(torch_classifier.CLASS_ORDER)
    assert metrics["confusion_matrix"]["class_order"] == list(
        torch_classifier.CLASS_ORDER
    )
    assert 0.0 < metrics["confidence_threshold"] < 1.0


def test_load_classifier_returns_model_with_checkpoint_threshold():
    model = torch_classifier.load_classifier()
    assert model is not None
    metrics = json.loads((ARTIFACTS / "metrics.json").read_text(encoding="utf-8"))
    assert model.threshold == metrics["confidence_threshold"]


def test_predict_returns_frozen_class_and_bounded_confidence():
    model = torch_classifier.load_classifier()
    result = model.predict([5.0, 5.1, 5.0, 5.2, 5.1, 5.0, 30.0])
    assert result["incident_class"] in torch_classifier.CLASS_ORDER
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["engine"] == "torch"
    assert isinstance(result["below_threshold"], bool)


def test_engine_env_stub_disables_torch(monkeypatch):
    monkeypatch.setenv("PETER_PREDICTOR_ENGINE", "stub")
    assert torch_classifier.load_classifier() is None


def test_missing_checkpoint_degrades_to_none(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "PETER_PREDICTOR_MODEL_PATH", str(tmp_path / "missing.pth")
    )
    assert torch_classifier.load_classifier() is None


def test_corrupt_checkpoint_degrades_to_none(monkeypatch, tmp_path):
    corrupt = tmp_path / "corrupt.pth"
    corrupt.write_bytes(b"not a checkpoint")
    monkeypatch.setenv("PETER_PREDICTOR_MODEL_PATH", str(corrupt))
    assert torch_classifier.load_classifier() is None


def test_analyse_uses_torch_engine_without_context():
    response = client.post(
        "/analyse", json={"window": [5.0, 5.1, 5.0, 5.2, 5.1, 5.0, 30.0]}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["scores"]["classifier"]["engine"] == "torch"
    assert body["incident_class"] in torch_classifier.CLASS_ORDER


def test_analyse_context_marker_beats_torch_model():
    response = client.post(
        "/analyse",
        json={
            "incident": {"symptom": "postgres replication lag increasing"},
            "window": [5.0, 5.1, 5.0, 5.2, 5.1, 5.0, 30.0],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["incident_class"] == "replication_lag"
    assert body["scores"]["classifier"]["engine"] == "context"


def test_analyse_below_threshold_surfaces_uncertain_fallback(monkeypatch):
    model = torch_classifier.load_classifier()
    assert model is not None

    class LowConfidenceModel:
        threshold = model.threshold

        def predict(self, window):
            return {
                "incident_class": "error_rate_spike",
                "confidence": 0.31,
                "engine": "torch",
                "below_threshold": True,
            }

    monkeypatch.setattr(
        "predictor_service.app.load_classifier", lambda: LowConfidenceModel()
    )
    response = client.post("/analyse", json={"window": [1.0, 2.0, 3.0]})
    assert response.status_code == 200
    body = response.json()
    # Frozen six-class enum: uncertainty is the fallback marker, never a class.
    assert body["incident_class"] == "error_rate_spike"
    assert body["confidence"] == 0.31
    assert body["scores"]["classifier"]["fallback"] == "uncertain"
