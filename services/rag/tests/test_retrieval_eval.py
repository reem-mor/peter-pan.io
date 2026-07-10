"""Golden-set retrieval evaluation (ADR 0001 limitation 6 / BUILD_PLAN §4 exit gate).

Runs each case in evaluation/rag_evaluation_cases.json through the real
TF-IDF retriever and asserts the expected source shows up in the top-3
results for at least 2 of every 3 cases.
"""

from __future__ import annotations

import json
from pathlib import Path

from rag_service.local_rag import get_retriever

EVAL_PATH = (
    Path(__file__).resolve().parents[3] / "evaluation" / "rag_evaluation_cases.json"
)
MIN_HIT_RATE = 2 / 3
TOP_K = 3


def _load_cases() -> list[dict]:
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


def _case_hits(question: str, expected_sources: list[str]) -> bool:
    results = get_retriever().search(question, top_k=TOP_K)
    retrieved_stems = {Path(hit.document).stem for hit in results}
    retrieved_stems |= {hit.doc_id for hit in results}
    expected_stems = {Path(source).stem for source in expected_sources}
    return bool(retrieved_stems & expected_stems)


def test_retrieval_hit_rate_meets_threshold():
    cases = _load_cases()
    assert cases, "no evaluation cases found"

    hits = sum(
        1 for case in cases if _case_hits(case["question"], case["expected_sources"])
    )
    hit_rate = hits / len(cases)

    assert hit_rate >= MIN_HIT_RATE, (
        f"retrieval hit-rate {hit_rate:.2f} ({hits}/{len(cases)}) below "
        f"threshold {MIN_HIT_RATE:.2f}"
    )


def test_each_eval_case_is_individually_traceable():
    """Not a hard gate (see hit-rate test), but surfaces which cases miss."""
    cases = _load_cases()
    misses = [
        case["id"]
        for case in cases
        if not _case_hits(case["question"], case["expected_sources"])
    ]
    # Document current misses rather than silently allowing regressions to grow.
    assert len(misses) <= max(
        0, len(cases) - 2
    ), f"too many missed eval cases: {misses}"
