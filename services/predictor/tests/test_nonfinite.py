"""Predictor: non-finite (NaN/Inf) metric-window safety (TDD red → green).

The EWMA scorer and the /analyse endpoint must never produce non-finite
floating-point values in their responses (JSON has no NaN/Inf literals and
FastAPI's serializer would raise a 500 if they escaped into the response body).
"""

from __future__ import annotations

import math

import pytest
from fastapi.testclient import TestClient

from predictor_service.app import app
from predictor_service.ewma import score as ewma_score

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)


# ---------------------------------------------------------------------------
# Unit-level: ewma.score() must never propagate non-finite values to output
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "window",
    [
        [float("nan")],
        [1.0, float("nan")],
        [float("inf")],
        [1.0, float("inf")],
        [float("-inf"), 1.0],
        [float("nan"), float("inf")],
    ],
)
def test_ewma_score_nonfinite_input_returns_finite_output(window):
    """Non-finite values in the window must not leak into the scored output."""
    result = ewma_score(window)
    assert math.isfinite(result["overall_score"]), (
        f"overall_score={result['overall_score']!r} is non-finite for window {window}"
    )
    assert all(
        math.isfinite(s) for s in result["point_scores"]
    ), f"point_scores contains non-finite value for window {window}"
    assert isinstance(result["severity"], int)
    assert 1 <= result["severity"] <= 5


# ---------------------------------------------------------------------------
# App-level: /analyse rejects non-finite client input at the schema boundary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("literal", ["NaN", "Infinity", "-Infinity"])
def test_analyse_rejects_nonfinite_window_values(literal):
    response = client.post(
        "/analyse",
        content=f'{{"window":[1.0,{literal}]}}',
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 422
