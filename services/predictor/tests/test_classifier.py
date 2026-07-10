"""Classifier interface smoke tests (BUILD_PLAN §3, Predictor row).

Stage A fixture (fixed weights, no training) — asserts the interface shape
and that the three documented hint bands are reachable, not model accuracy.
"""

from __future__ import annotations

from predictor_service.classifier import predict


def test_predict_returns_expected_shape():
    result = predict([1.0, 2.0, 3.0])
    assert set(result.keys()) == {"category_hint", "confidence"}
    assert result["category_hint"] in {"stable", "drift", "spike"}
    assert 0.0 <= result["confidence"] <= 1.0


def test_flat_window_is_stable():
    result = predict([10.0] * 8)
    assert result["category_hint"] == "stable"


def test_moderate_variance_window_is_drift():
    # mean=10.0, population stdev≈0.894 -> ratio≈0.089, between the drift and
    # spike thresholds (0.05 / 0.15).
    result = predict([10.0, 11.0, 9.0, 11.0, 9.0])
    assert result["category_hint"] == "drift"


def test_high_variance_window_is_spike():
    result = predict([10.0, 10.0, 10.0, 40.0])
    assert result["category_hint"] == "spike"


def test_empty_window_defaults_to_stable():
    result = predict([])
    assert result["category_hint"] == "stable"
