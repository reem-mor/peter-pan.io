"""Validate corpus filename alignment with the demo_questions golden set.

The pre-migration version of this module also validated ``app.data_loader``
example-question/workflow-alert helpers used by the deleted Flask/React UI.
Those helpers have no rag_service equivalent (Stage B ships a Streamlit UI
that doesn't need them) and are dropped rather than reimplemented dead code
from the retired application.
"""

from __future__ import annotations

import json
from pathlib import Path

CORPUS = Path(__file__).resolve().parents[1] / "corpus"
EVAL_PATH = Path(__file__).resolve().parents[3] / "evaluation" / "demo_questions.json"

DEMO_CORPUS_FILES = (
    "orders_api_error_spike.json",
    "deployment_rollback.json",
    "redis_cache_degradation.json",
    "database_connectivity.json",
    "ingress_5xx.json",
)


def test_demo_corpus_files_exist():
    for name in DEMO_CORPUS_FILES:
        assert any(
            path.name == name for path in CORPUS.rglob("*.json")
        ), f"missing demo corpus file: {name}"


def test_evaluation_questions_schema():
    cases = json.loads(EVAL_PATH.read_text(encoding="utf-8"))
    assert isinstance(cases, list)
    ids = [c["id"] for c in cases]
    assert len(ids) == len(set(ids))
    corpus_names = {p.stem for p in CORPUS.rglob("*.json") if p.is_file()}
    corpus_names |= {p.name for p in CORPUS.rglob("*.json") if p.is_file()}
    for case in cases:
        if case.get("expect_validation_error"):
            assert case.get("expected_reason")
            continue
        if case.get("expect_grounded"):
            for fragment in case.get("expected_source_contains", []):
                assert any(
                    fragment in name for name in corpus_names
                ), f"eval id {case['id']}: no corpus file matching {fragment!r}"
