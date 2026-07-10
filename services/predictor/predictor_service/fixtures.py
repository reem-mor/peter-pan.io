"""Built-in fixture metric windows for ``POST /analyse`` calls that don't
supply a ``window`` directly (BUILD_PLAN §3: "Stage A: fixture windows").

Selection is deterministic: a stable hash of ``metric_window_ref`` (never the
randomized built-in ``hash()``) picks one of a small, fixed set of windows,
so the same ref always yields the same window across processes and runs.
"""

from __future__ import annotations

import hashlib

# A small, fixed set of representative shapes: stable baseline, gentle ramp,
# and a late step-spike. Real Prometheus-backed windows are a later stage.
FIXTURE_WINDOWS: tuple[tuple[float, ...], ...] = (
    (10.0, 10.1, 9.9, 10.2, 10.0, 9.8, 10.1),  # stable baseline
    (10.0, 10.2, 10.4, 10.9, 11.6, 12.8, 15.0),  # gentle ramp/drift
    (5.0, 5.1, 5.0, 5.2, 5.1, 5.0, 30.0),  # sudden late step-spike
)
DEFAULT_FIXTURE_INDEX = 0  # used when no ref is given at all


def fixture_window(metric_window_ref: str | None) -> list[float]:
    """Deterministically map a ref string to one of ``FIXTURE_WINDOWS``."""
    if not metric_window_ref:
        return list(FIXTURE_WINDOWS[DEFAULT_FIXTURE_INDEX])
    digest = hashlib.sha256(metric_window_ref.encode("utf-8")).hexdigest()
    index = int(digest, 16) % len(FIXTURE_WINDOWS)
    return list(FIXTURE_WINDOWS[index])
