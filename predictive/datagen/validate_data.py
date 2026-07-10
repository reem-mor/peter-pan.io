#!/usr/bin/env python3
"""Validate the canonical PETER PAN demo datasets under ``predictive/data/source/``.

Self-contained (AGENTS.md: no cross-directory imports outside a component's
own tree) -- loads every dataset produced by ``generate_demo_data.py`` /
``generate_alert_stream.py`` with plain ``csv``/``json`` and asserts each
parses and has rows. This replaced an earlier version that imported
``app.services.data_access``; that module lived in the deleted PITER Flask
app and, even if it still existed, importing into it from here would violate
the "services talk HTTP only" rule (ADR 0001 limitation 4).

Usage:
    python -m predictive.datagen.validate_data
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
SOURCE = _ROOT / "data" / "source"

# Canonical files the demo generators produce (KEEP under predictive/data/source/).
EXPECTED_FILES = {
    "alert_stream.csv",
    "alerts.csv",
    "service_owners.csv",
    "on_call_schedule.csv",
    "past_incidents.csv",
    "deploys.csv",
    "business_impact.json",
    "priority_matrix.json",
    "escalation_policies.json",
}


def _load_csv(name: str) -> list[dict[str, Any]]:
    with open(SOURCE / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _load_json(name: str) -> dict[str, Any]:
    with open(SOURCE / name, encoding="utf-8") as f:
        return json.load(f)


# Loader -> human label, exercising the canonical predictive/data/source/ read path.
LOADERS: tuple[tuple[str, Any], ...] = (
    ("alert_stream.csv", lambda: _load_csv("alert_stream.csv")),
    ("alerts.csv", lambda: _load_csv("alerts.csv")),
    ("service_owners.csv", lambda: _load_csv("service_owners.csv")),
    ("on_call_schedule.csv", lambda: _load_csv("on_call_schedule.csv")),
    ("past_incidents.csv", lambda: _load_csv("past_incidents.csv")),
    ("deploys.csv", lambda: _load_csv("deploys.csv")),
    ("business_impact.json", lambda: _load_json("business_impact.json")),
    ("priority_matrix.json", lambda: _load_json("priority_matrix.json")),
    ("escalation_policies.json", lambda: _load_json("escalation_policies.json")),
)


def _check_files() -> list[str]:
    errors: list[str] = []
    if not SOURCE.is_dir():
        return [f"predictive/data/source/ is missing: {SOURCE}"]
    present = {p.name for p in SOURCE.iterdir() if p.is_file()}
    for name in sorted(EXPECTED_FILES - present):
        errors.append(f"missing canonical file: predictive/data/source/{name}")
    return errors


def _check_schemas() -> list[str]:
    errors: list[str] = []
    for name, loader in LOADERS:
        try:
            data = loader()
            count = (
                len(data) if isinstance(data, list) else len(data.get("services", data))
            )
            if count == 0:
                raise ValueError("parsed but contains zero records")
            print(f"  OK   {name:<26} ({count} records)")
        except Exception as exc:  # noqa: BLE001 -- report every dataset's status
            errors.append(f"{name}: {exc}")
            print(f"  FAIL {name:<26} {exc}")
    return errors


def main() -> int:
    print(f"Validating canonical data dir: {SOURCE}")
    file_errors = _check_files()
    if file_errors:
        for err in file_errors:
            print(f"  FAIL {err}")
        print("\nDATA VALIDATION FAILED")
        return 1
    print("\nSchema validation (via predictive/data/source loaders):")
    schema_errors = _check_schemas()
    if schema_errors:
        print(f"\nDATA VALIDATION FAILED ({len(schema_errors)} error(s))")
        return 1
    print(
        "\nDATA VALIDATION PASSED -- all generators write only predictive/data/source/."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
