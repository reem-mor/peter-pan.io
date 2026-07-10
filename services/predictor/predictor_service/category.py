"""Deterministic service-name -> category mapping (BUILD_PLAN §3, Predictor row).

Not model output: this is plain, unit-tested string matching that drives the
``TriageReport.category`` field downstream (n8n router node 8). Keep it here
as pure functions so it's directly testable without spinning up the app.
"""

from __future__ import annotations

_DATABASE_HINTS = ("postgres", "db", "database")
_INFRA_HINTS = ("redis", "ingress", "k8s", "node", "cache")


def categorize_service(service_name: str) -> str:
    """service name -> "database" | "infra" | "application" (deterministic)."""
    name = (service_name or "").lower()
    if any(hint in name for hint in _DATABASE_HINTS):
        return "database"
    if any(hint in name for hint in _INFRA_HINTS):
        return "infra"
    return "application"


def resolve_service_name(incident: dict | None, metric_window_ref: str | None) -> str:
    """Best-effort service name for categorization: prefer ``incident.service``,
    fall back to the ``service:metric`` prefix of ``metric_window_ref``, else "".
    """
    if incident and isinstance(incident.get("service"), str) and incident["service"]:
        return incident["service"]
    if metric_window_ref:
        return metric_window_ref.split(":", 1)[0]
    return ""
