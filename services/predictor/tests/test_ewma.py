"""EWMA known-series table (BUILD_PLAN §3, Predictor row): flat series -> low
severity; step spike -> high severity; exact expected bands.

The std-dev floor is 2% of the running mean (``ewma.MIN_STD_REL``). Because
the first four points in each series below are identical, the running mean
stays at 10.0 and variance stays at 0.0 through them, so at the 5th point the
std used is exactly ``0.02 * 10.0 == 0.2`` — chosen so the deviation at the
spike works out to clean round numbers for each severity band boundary.
"""

from __future__ import annotations

import pytest

from predictor_service.ewma import score, severity_band


def test_flat_series_is_severity_one_with_zero_score():
    result = score([10.0, 10.0, 10.0, 10.0, 10.0, 10.0], alpha=0.3)
    assert result["overall_score"] == 0.0
    assert result["severity"] == 1
    assert result["point_scores"] == [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


@pytest.mark.parametrize(
    "window, expected_deviation, expected_severity",
    [
        ([10.0, 10.0, 10.0, 10.0, 10.3], 1.5, 2),  # 0.3 / 0.2
        ([10.0, 10.0, 10.0, 10.0, 10.6], 3.0, 3),  # 0.6 / 0.2
        ([10.0, 10.0, 10.0, 10.0, 10.9], 4.5, 4),  # 0.9 / 0.2
        ([10.0, 10.0, 10.0, 10.0, 11.3], 6.5, 5),  # 1.3 / 0.2
    ],
    ids=["mild_drift", "moderate_step", "high_step", "severe_step_spike"],
)
def test_step_spike_known_series_hits_expected_band(
    window, expected_deviation, expected_severity
):
    result = score(window, alpha=0.3)
    assert result["overall_score"] == pytest.approx(expected_deviation, rel=1e-6)
    assert result["severity"] == expected_severity


def test_severity_band_thresholds_are_exact_and_monotonic():
    assert severity_band(0.0) == 1
    assert severity_band(0.999) == 1
    assert severity_band(1.0) == 2
    assert severity_band(2.499) == 2
    assert severity_band(2.5) == 3
    assert severity_band(3.999) == 3
    assert severity_band(4.0) == 4
    assert severity_band(5.999) == 4
    assert severity_band(6.0) == 5
    assert severity_band(1000.0) == 5


def test_empty_window_is_safe():
    result = score([], alpha=0.3)
    assert result == {"point_scores": [], "overall_score": 0.0, "severity": 1}


def test_single_point_window_is_safe():
    result = score([42.0], alpha=0.3)
    assert result["point_scores"] == [0.0]
    assert result["overall_score"] == 0.0
    assert result["severity"] == 1


def test_point_scores_length_matches_window_length():
    window = [1.0, 2.0, 3.0, 4.0, 5.0]
    result = score(window)
    assert len(result["point_scores"]) == len(window)
