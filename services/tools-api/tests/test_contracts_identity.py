"""Contract-copy identity test (BUILD_PLAN.md §1).

``tools_api/contracts.py`` must be byte-identical to the canonical
``docs/contracts/contracts.py``. Changing either requires an ADR.
"""

from __future__ import annotations

from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_SERVICE_ROOT = _THIS_FILE.parents[1]  # services/tools-api/
_REPO_ROOT = _THIS_FILE.parents[3]  # repo root

_VENDORED = _SERVICE_ROOT / "tools_api" / "contracts.py"
_CANONICAL = _REPO_ROOT / "docs" / "contracts" / "contracts.py"


def test_vendored_contracts_match_canonical_byte_for_byte():
    assert _CANONICAL.is_file(), f"Canonical contracts file not found: {_CANONICAL}"
    assert _VENDORED.is_file(), f"Vendored contracts file not found: {_VENDORED}"
    assert _VENDORED.read_bytes() == _CANONICAL.read_bytes()
