"""Load committed dashboard fixtures and the metrics catalog."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

def _resolve_fixtures_dir() -> Path:
    """Repo-root fixtures (dev), service-tree copy (pytest), or image COPY target."""
    pkg = Path(__file__).resolve().parent
    candidates: list[Path] = [
        pkg.parent.parent / "fixtures" / "dashboards",
        pkg.parent / "fixtures" / "dashboards",
        pkg / "fixtures",
    ]
    resolved = Path(__file__).resolve()
    if len(resolved.parents) > 3:
        candidates.insert(0, resolved.parents[3] / "fixtures" / "dashboards")
    for path in candidates:
        if (path / "metrics_catalog.json").is_file():
            return path
    return candidates[0]


FIXTURES_DIR = _resolve_fixtures_dir()

KNOWN_SCENARIOS = frozenset(
    {
        "orders-api-error-spike",
        "postgres-pool-pressure",
        "shop-web-latency",
        "disk-pressure",
    }
)


def metrics_catalog() -> dict[str, Any]:
    path = FIXTURES_DIR / "metrics_catalog.json"
    return json.loads(path.read_text(encoding="utf-8"))


def allowed_metric_names() -> frozenset[str]:
    catalog = metrics_catalog()
    return frozenset(item["name"] for item in catalog.get("metrics", []))


def load_fixture(scenario: str) -> dict[str, Any]:
    if scenario not in KNOWN_SCENARIOS:
        raise FileNotFoundError(f"unknown scenario: {scenario}")
    path = FIXTURES_DIR / f"{scenario}.json"
    if not path.is_file():
        raise FileNotFoundError(f"fixture missing: {path.name}")
    return json.loads(path.read_text(encoding="utf-8"))
