"""Golden signal fixture schema checks."""

from __future__ import annotations

import json
from pathlib import Path

EVAL_PATH = Path(__file__).resolve().parents[3] / "evaluation" / "golden_signals.json"


def test_golden_signals_schema():
    cases = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    assert len(cases) >= 3
    for case in cases:
        signal = case["signal"]
        assert signal["id"].startswith("sig-")
