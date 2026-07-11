"""Deterministic EWMA (exponentially weighted moving average) anomaly scorer.

Stage A anomaly-detection floor (BUILD_PLAN §3, Predictive Engine row): pure,
unit-tested arithmetic — no ML, no PyTorch. For each point in the window we
track a running EWMA mean/variance and compute a z-like deviation score
against it; the overall (max) deviation across the window selects a severity
band. This is the "real" half of the Predictor — the classifier in
``classifier.py`` is the documented Stage-A stub.

Deterministic-floor rule (engineering principles): thresholds below are
constants, not model output — nothing here is learned or LLM-proposed.
"""

from __future__ import annotations

import math

# Severity bands over the overall (max abs) deviation score. Checked in
# descending order; the first threshold met wins. Tune only here.
SEVERITY_BANDS: tuple[tuple[float, int], ...] = (
    (6.0, 5),  # >= 6.0 std-devs from the running EWMA mean -> most severe
    (4.0, 4),
    (2.5, 3),
    (1.0, 2),
)
DEFAULT_SEVERITY = 1  # below every threshold -> mild/no anomaly

# Std-dev floor: an absolute floor (avoids literal divide-by-zero) plus a
# floor relative to the running mean's magnitude (avoids z-scores exploding
# to absurd values on windows that were *exactly* flat before a real spike —
# real metric windows always carry some jitter; this keeps the "z-like"
# score meaningful even for synthetic/fixture windows that don't).
MIN_STD_FLOOR = 1e-6
MIN_STD_REL = 0.02  # 2% of |running mean|


def score(window: list[float], alpha: float = 0.3) -> dict:
    """Score a metric window for anomalies.

    Returns ``{"point_scores": [...], "overall_score": float, "severity": int}``.
    ``point_scores[i]`` is the deviation of ``window[i]`` from the running
    EWMA mean *before* that point updates it, normalized by a running EWMA
    std-dev (also pre-update) — classic streaming anomaly scoring.
    """
    if not window:
        return {"point_scores": [], "overall_score": 0.0, "severity": DEFAULT_SEVERITY}

    # Sanitize non-finite values (NaN/±Inf) to 0.0 so the output is always
    # JSON-safe. Non-finite windows carry no meaningful anomaly signal.
    window = [v if math.isfinite(v) else 0.0 for v in window]

    mean = window[0]
    var = 0.0
    point_scores: list[float] = [0.0]  # first point has no history to deviate from

    for value in window[1:]:
        std = max(var**0.5, MIN_STD_REL * abs(mean), MIN_STD_FLOOR)
        deviation = (value - mean) / std
        point_scores.append(deviation)

        # Update running EWMA mean/variance AFTER scoring against prior state.
        diff = value - mean
        mean += alpha * diff
        var = (1 - alpha) * (var + alpha * diff * diff)

    overall_score = max(abs(s) for s in point_scores)
    return {
        "point_scores": point_scores,
        "overall_score": overall_score,
        "severity": severity_band(overall_score),
    }


def severity_band(overall_score: float) -> int:
    """Deterministic overall-score -> 1..5 severity mapping. Public so it's
    directly unit-testable at the thresholds without constructing windows."""
    for threshold, band in SEVERITY_BANDS:
        if overall_score >= threshold:
            return band
    return DEFAULT_SEVERITY
