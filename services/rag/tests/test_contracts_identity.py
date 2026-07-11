"""Assert rag_service/contracts.py is byte-identical to the canonical copy.

BUILD_PLAN §1: contracts are frozen and vendored into each service; changing
one requires an ADR. This test is the enforcement mechanism.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL = REPO_ROOT / "docs" / "contracts" / "contracts.py"
VENDORED = Path(__file__).resolve().parents[1] / "rag_service" / "contracts.py"


def test_contracts_are_byte_identical_to_canonical_copy():
    assert CANONICAL.is_file(), f"canonical contracts file missing: {CANONICAL}"
    assert VENDORED.is_file(), f"vendored contracts file missing: {VENDORED}"
    assert VENDORED.read_bytes() == CANONICAL.read_bytes()
