"""Contract-copy identity test (AGENTS.md: "each service vendors an identical
copy checked by a contract test")."""

from __future__ import annotations

from pathlib import Path

import guardrails_service.contracts as vendored_contracts
from pydantic import ValidationError

_CANONICAL = Path(__file__).resolve().parents[3] / "docs" / "contracts" / "contracts.py"


def test_vendored_contracts_is_byte_identical_to_canonical() -> None:
    canonical_bytes = _CANONICAL.read_bytes()
    vendored_path = Path(vendored_contracts.__file__)
    vendored_bytes = vendored_path.read_bytes()
    assert vendored_bytes == canonical_bytes, (
        f"{vendored_path} has drifted from the canonical {_CANONICAL}; "
        "changing a contract requires an ADR (AGENTS.md)."
    )


def test_guardrail_result_is_frozen_and_forbids_extra_fields() -> None:
    assert hasattr(vendored_contracts, "GuardrailResult")
    result = vendored_contracts.GuardrailResult(passed=False, flags=["unsafe"], reason="blocked")
    assert result.model_dump() == {
        "passed": False,
        "flags": ["unsafe"],
        "reason": "blocked",
    }

    try:
        vendored_contracts.GuardrailResult(passed=True, unexpected=True)
    except ValidationError:
        pass
    else:
        raise AssertionError("GuardrailResult must reject extra fields")
