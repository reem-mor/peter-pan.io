"""Validate Grafana dashboard JSON before any POST (grafana-dashboard-json skill)."""

from __future__ import annotations

import re
from typing import Any

from dashboard_generator.fixtures_loader import allowed_metric_names

ALLOWED_PANEL_TYPES = frozenset({"timeseries", "stat", "gauge", "table"})
GRID_WIDTH = 24
MAX_PANELS = 6
UID_PREFIX = "pp-"
METRIC_BEFORE_LABELS = re.compile(r"([a-zA-Z_:][a-zA-Z0-9_:]*)\{")
METRIC_BEFORE_RANGE = re.compile(r"([a-zA-Z_:][a-zA-Z0-9_:]*)\[")


class DashboardValidationError(ValueError):
    """Raised when dashboard JSON fails structural or policy checks."""


HISTOGRAM_SUFFIXES = ("_bucket", "_sum")


def _metric_allowed(name: str, allowed: frozenset[str]) -> bool:
    if name in allowed:
        return True
    for suffix in HISTOGRAM_SUFFIXES:
        if name.endswith(suffix) and name[: -len(suffix)] in allowed:
            return True
    return False


def _extract_metric_tokens(expr: str) -> set[str]:
    names = set(METRIC_BEFORE_LABELS.findall(expr))
    names.update(METRIC_BEFORE_RANGE.findall(expr))
    return names


def _panel_rect(panel: dict[str, Any]) -> tuple[int, int, int, int]:
    pos = panel.get("gridPos") or {}
    return (
        int(pos.get("x", 0)),
        int(pos.get("y", 0)),
        int(pos.get("w", 0)),
        int(pos.get("h", 0)),
    )


def _rects_overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def validate_dashboard_payload(payload: dict[str, Any]) -> list[str]:
    """Return a list of validation errors (empty = valid)."""
    errors: list[str] = []
    for key in ("dashboard", "folderUid", "overwrite", "message"):
        if key not in payload:
            errors.append(f"missing top-level key: {key}")

    dashboard = payload.get("dashboard")
    if not isinstance(dashboard, dict):
        errors.append("dashboard must be an object")
        return errors

    for key in ("title", "panels", "schemaVersion", "time"):
        if key not in dashboard:
            errors.append(f"dashboard missing key: {key}")

    uid = dashboard.get("uid")
    if uid is not None and not str(uid).startswith(UID_PREFIX):
        errors.append(f"dashboard uid must start with {UID_PREFIX!r}")

    panels = dashboard.get("panels")
    if not isinstance(panels, list):
        errors.append("dashboard.panels must be a list")
        return errors

    if len(panels) > MAX_PANELS:
        errors.append(f"too many panels ({len(panels)} > {MAX_PANELS})")

    allowed = allowed_metric_names()
    panel_ids: set[int] = set()
    rects: list[tuple[int, int, int, int]] = []

    for index, panel in enumerate(panels):
        if not isinstance(panel, dict):
            errors.append(f"panel {index} must be an object")
            continue
        panel_type = panel.get("type")
        if panel_type not in ALLOWED_PANEL_TYPES:
            errors.append(f"panel {index}: disallowed type {panel_type!r}")

        panel_id = panel.get("id")
        if not isinstance(panel_id, int):
            errors.append(f"panel {index}: id must be an integer")
        elif panel_id in panel_ids:
            errors.append(f"panel {index}: duplicate id {panel_id}")
        else:
            panel_ids.add(panel_id)

        rect = _panel_rect(panel)
        x, y, w, h = rect
        if x + w > GRID_WIDTH:
            errors.append(f"panel {index}: exceeds grid width ({x}+{w} > {GRID_WIDTH})")
        rects.append(rect)

        ds = panel.get("datasource")
        if not isinstance(ds, dict) or not ds.get("uid"):
            errors.append(f"panel {index}: datasource.uid required")

        for target in panel.get("targets") or []:
            expr = str(target.get("expr", ""))
            for metric in _extract_metric_tokens(expr):
                if not _metric_allowed(metric, allowed):
                    errors.append(f"panel {index}: uncatalogued metric {metric!r}")

    for i, rect_a in enumerate(rects):
        for j, rect_b in enumerate(rects[i + 1 :], start=i + 1):
            if _rects_overlap(rect_a, rect_b):
                errors.append(f"panels {i} and {j} overlap")

    return errors


def assert_valid_dashboard(payload: dict[str, Any]) -> None:
    errors = validate_dashboard_payload(payload)
    if errors:
        raise DashboardValidationError("; ".join(errors))
