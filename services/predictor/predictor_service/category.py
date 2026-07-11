"""Build deterministic context for the Stage-A incident-class fixture.

The trained T1 predictor will classify the metric window directly. Until then,
the fixed classifier may use explicit metric names or incident symptoms to
select one of the six declared classes. Routing-category policy lives in n8n.
"""

from __future__ import annotations

def classification_context(
    incident: dict | None,
    metric_window_ref: str | None,
) -> str:
    """Join only explicit classification hints; never infer from service ownership."""
    parts = [metric_window_ref or ""]
    if incident:
        parts.extend(
            value
            for key in ("symptom", "title", "body")
            if isinstance((value := incident.get(key)), str)
        )
    return " ".join(part for part in parts if part)
