"""Contract-copy identity test (BUILD_PLAN §1 / §2).

Contracts are frozen at Stage A start; every service vendors an identical
copy of ``docs/contracts/contracts.py``. This test asserts this service's
copy hasn't drifted, byte-for-byte, from the canonical file.
"""

from __future__ import annotations

from pathlib import Path

_SERVICE_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _SERVICE_DIR.parents[1]

_VENDORED = _SERVICE_DIR / "ingestion_service" / "contracts.py"
_CANONICAL = _REPO_ROOT / "docs" / "contracts" / "contracts.py"


def test_vendored_contracts_are_byte_identical_to_canonical():
    vendored = _VENDORED.read_bytes()
    canonical = _CANONICAL.read_bytes()
    assert vendored == canonical, (
        f"{_VENDORED} has drifted from canonical {_CANONICAL}. "
        "Contracts are frozen (BUILD_PLAN.md §1) — changing one requires an ADR; "
        "re-vendor the canonical copy instead of hand-editing this file."
    )
