"""PyTorch-free classifier stub (Stage A fixture, BUILD_PLAN §3 Predictor row).

Real anomaly *classification* (as opposed to the deterministic EWMA severity
floor in ``ewma.py``) is out of scope for Stage A — training a real model is
an unbounded stretch goal flagged in BUILD_PLAN §6. This module ships a
fixed-weight stub behind the interface a trained classifier would expose
(``predict(window) -> {"category_hint", "confidence"}``) so callers and
tests don't change shape when a real model lands later.

Note: ``category_hint`` here describes the *shape* of the window (stable /
drift / spike) — it is NOT the infra/database/application routing category.
That mapping is separate, deterministic, and service-name based; see
``category.py``.
"""

from __future__ import annotations

import statistics

# Fixed thresholds standing in for a trained model's decision boundary
# (Stage-A fixture; BUILD_PLAN §6 flags real training as out of scope).
_SPIKE_STDEV_RATIO = 0.15  # stdev / max(|mean|, 1) at/above this -> "spike"
_DRIFT_STDEV_RATIO = 0.05  # at/above this (but below spike) -> "drift"

# Fixed confidence per hint — a documented fixture, not a learned value.
_FIXED_CONFIDENCE = {"stable": 0.55, "drift": 0.70, "spike": 0.85}


def predict(window: list[float]) -> dict:
    """Fixed-weight classifier stub. Returns ``{"category_hint", "confidence"}``."""
    if not window:
        return {"category_hint": "stable", "confidence": _FIXED_CONFIDENCE["stable"]}

    mean = statistics.fmean(window)
    stdev = statistics.pstdev(window) if len(window) > 1 else 0.0
    scale = max(abs(mean), 1.0)
    ratio = stdev / scale

    if ratio >= _SPIKE_STDEV_RATIO:
        hint = "spike"
    elif ratio >= _DRIFT_STDEV_RATIO:
        hint = "drift"
    else:
        hint = "stable"

    return {"category_hint": hint, "confidence": _FIXED_CONFIDENCE[hint]}
