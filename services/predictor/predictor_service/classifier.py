"""PyTorch-free classifier stub (Stage A fixture, BUILD_PLAN §3 Predictor row).

Real anomaly *classification* (as opposed to the deterministic EWMA severity
floor in ``ewma.py``) is out of scope for Stage A — training a real model is
an unbounded stretch goal flagged in BUILD_PLAN §6. This module ships a
fixed-weight stub behind the six-class interface the trained classifier will
expose. Explicit metric context selects a class deterministically; otherwise
the window shape selects one of the documented fixture fallback classes.

The result is a fine-grained ``incident_class``. The n8n policy layer, not this
service, maps it to the coarse ``TriageReport.category`` routing bucket.
"""

from __future__ import annotations

import statistics

# Fixed thresholds standing in for a trained model's decision boundary
# (Stage-A fixture; BUILD_PLAN §6 flags real training as out of scope).
_SPIKE_STDEV_RATIO = 0.15  # stdev / max(|mean|, 1) at/above this -> "spike"
_DRIFT_STDEV_RATIO = 0.05  # at/above this (but below spike) -> "drift"

# Fixed confidence per fixture result — documented constants, not learned values.
_FIXED_CONFIDENCE = {
    "cpu_saturation": 0.75,
    "memory_leak": 0.75,
    "db_lock_contention": 0.75,
    "replication_lag": 0.75,
    "error_rate_spike": 0.85,
    "normal": 0.55,
}

_CONTEXT_MARKERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("replication_lag", ("replication lag", "replica lag")),
    (
        "db_lock_contention",
        ("deadlock", "lock wait", "lock contention", "pool exhausted"),
    ),
    ("error_rate_spike", ("error rate", "5xx", "exception rate")),
    ("cpu_saturation", ("cpu saturation", "high cpu", "run queue", "load average")),
    ("memory_leak", ("memory leak", "heap growth", "heap growing", "oom")),
)


def predict(window: list[float], *, context: str = "") -> dict:
    """Return a deterministic six-class fixture prediction."""
    normalized_context = context.lower().replace("_", " ")
    for incident_class, markers in _CONTEXT_MARKERS:
        if any(marker in normalized_context for marker in markers):
            return {
                "incident_class": incident_class,
                "confidence": _FIXED_CONFIDENCE[incident_class],
            }

    if not window:
        return {
            "incident_class": "normal",
            "confidence": _FIXED_CONFIDENCE["normal"],
        }

    mean = statistics.fmean(window)
    stdev = statistics.pstdev(window) if len(window) > 1 else 0.0
    scale = max(abs(mean), 1.0)
    ratio = stdev / scale

    if ratio >= _SPIKE_STDEV_RATIO:
        incident_class = "error_rate_spike"
    elif ratio >= _DRIFT_STDEV_RATIO:
        incident_class = "memory_leak"
    else:
        incident_class = "normal"

    return {
        "incident_class": incident_class,
        "confidence": _FIXED_CONFIDENCE[incident_class],
    }
