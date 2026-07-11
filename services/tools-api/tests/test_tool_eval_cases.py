"""Tool evaluation golden-set against HTTP routes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tools_api.app import app

EVAL_PATH = Path(__file__).resolve().parents[3] / "evaluation" / "tool_evaluation_cases.json"
client = TestClient(app)


@pytest.fixture(autouse=True)
def _isolated_audit_db(tmp_path, monkeypatch):
    monkeypatch.setenv("TOOLS_AUDIT_DB", str(tmp_path / "audit.sqlite"))
    monkeypatch.delenv("PETER_SERVICES_TOKEN", raising=False)


def test_tool_evaluation_cases_match_routes():
    cases = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    for case in cases:
        response = client.post(case["route"], json=case["arguments"])
        assert response.status_code == 200, case["id"]
