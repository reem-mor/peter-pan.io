"""Validator tests — all committed fixtures must pass."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from dashboard_generator.fixtures_loader import FIXTURES_DIR, KNOWN_SCENARIOS
from dashboard_generator.validator import (
    DashboardValidationError,
    assert_valid_dashboard,
    validate_dashboard_payload,
)


@pytest.mark.parametrize("scenario", sorted(KNOWN_SCENARIOS))
def test_committed_fixtures_validate(scenario: str) -> None:
    payload = json.loads((FIXTURES_DIR / f"{scenario}.json").read_text(encoding="utf-8"))
    assert validate_dashboard_payload(payload) == []


def test_rejects_uncatalogued_metric() -> None:
    payload = json.loads(
        (FIXTURES_DIR / "orders-api-error-spike.json").read_text(encoding="utf-8")
    )
    payload["dashboard"]["panels"][0]["targets"][0]["expr"] = (
        'imaginary_metric_xyz{service="orders-api"}'
    )
    errors = validate_dashboard_payload(payload)
    assert any("uncatalogued metric" in err for err in errors)


def test_rejects_overlapping_panels() -> None:
    payload = {
        "dashboard": {
            "title": "bad",
            "schemaVersion": 39,
            "time": {"from": "now-1h", "to": "now"},
            "uid": "pp-bad",
            "panels": [
                {
                    "id": 1,
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
                    "datasource": {"type": "prometheus", "uid": "$DS_UID"},
                    "targets": [{"refId": "A", "expr": "http_requests_total"}],
                },
                {
                    "id": 2,
                    "type": "stat",
                    "gridPos": {"h": 8, "w": 12, "x": 6, "y": 0},
                    "datasource": {"type": "prometheus", "uid": "$DS_UID"},
                    "targets": [{"refId": "A", "expr": "http_requests_total"}],
                },
            ],
        },
        "folderUid": "peter-pan",
        "overwrite": False,
        "message": "test",
    }
    errors = validate_dashboard_payload(payload)
    assert any("overlap" in err for err in errors)


def test_assert_valid_raises() -> None:
    with pytest.raises(DashboardValidationError):
        assert_valid_dashboard({"dashboard": {}})
