"""Export the frozen contracts as JSON Schema for n8n's Structured Output Parser.

Usage:  python docs/contracts/export_json_schema.py
Writes: docs/contracts/schema/<model>.schema.json (one per top-level contract).

Regenerate after any (ADR-approved) contract change; the n8n flow's parser node
must always carry the current ``triage_report.schema.json``.
"""
from __future__ import annotations

import json
from pathlib import Path

from contracts import GuardrailResult, Incident, IncidentContext, Signal, TriageReport

HERE = Path(__file__).resolve().parent
OUT = HERE / "schema"

MODELS = {
    "signal": Signal,
    "incident_context": IncidentContext,
    "incident": Incident,
    "guardrail_result": GuardrailResult,
    "triage_report": TriageReport,
}


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, model in MODELS.items():
        schema = model.model_json_schema()
        path = OUT / f"{name}.schema.json"
        path.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {path.relative_to(HERE.parent.parent)}")


if __name__ == "__main__":
    main()
