"""Classifier interface smoke tests (BUILD_PLAN §3, Predictor row).

Stage A fixture (fixed weights, no training) — asserts the six-class interface
and the deterministic fallback bands, not model accuracy.
"""

from __future__ import annotations

import pytest

from predictor_service.classifier import predict


def test_predict_returns_expected_shape():
    result = predict([1.0, 2.0, 3.0])
    assert set(result.keys()) == {"incident_class", "confidence"}
    assert result["incident_class"] in {
        "cpu_saturation",
        "memory_leak",
        "db_lock_contention",
        "replication_lag",
        "error_rate_spike",
        "normal",
    }
    assert 0.0 <= result["confidence"] <= 1.0


def test_flat_window_is_normal():
    result = predict([10.0] * 8)
    assert result["incident_class"] == "normal"


def test_moderate_variance_window_uses_memory_leak_fixture_class():
    # mean=10.0, population stdev≈0.894 -> ratio≈0.089, between the drift and
    # spike thresholds (0.05 / 0.15).
    result = predict([10.0, 11.0, 9.0, 11.0, 9.0])
    assert result["incident_class"] == "memory_leak"


def test_high_variance_window_uses_error_rate_fixture_class():
    result = predict([10.0, 10.0, 10.0, 40.0])
    assert result["incident_class"] == "error_rate_spike"


def test_empty_window_defaults_to_normal():
    result = predict([])
    assert result["incident_class"] == "normal"


@pytest.mark.parametrize(
    ("context", "expected"),
    [
        ("CPU saturation and run queue growth", "cpu_saturation"),
        ("heap memory leak after deploy", "memory_leak"),
        ("database deadlock and lock waits", "db_lock_contention"),
        ("postgres replication lag increasing", "replication_lag"),
        ("HTTP 5xx error rate spike", "error_rate_spike"),
        ("checkout p95 latency 8.4s against a 1.2s baseline", "error_rate_spike"),
    ],
)
def test_explicit_metric_context_selects_incident_class(context, expected):
    result = predict([10.0] * 8, context=context)
    assert result["incident_class"] == expected
