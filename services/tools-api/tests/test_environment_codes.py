"""Environment code normalization and validation."""

from __future__ import annotations

import pytest

from tools_api.environment_codes import normalize_environment, validate_environment


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("production", "production"),
        ("PRODUCTION", "production"),
        ("staging", "staging"),
        ("STAGING", "staging"),
        ("prod", "production"),
        ("PROD", "production"),
        ("stg", "staging"),
        ("STG", "staging"),
    ],
)
def test_normalize_environment(raw: str, expected: str):
    assert normalize_environment(raw) == expected


def test_validate_accepts_canonical_codes():
    for env in ("production", "staging"):
        canonical, err = validate_environment(env)
        assert err is None
        assert canonical == env


def test_validate_accepts_aliases():
    canonical, err = validate_environment("prod")
    assert err is None
    assert canonical == "production"
    canonical, err = validate_environment("stg")
    assert err is None
    assert canonical == "staging"


def test_validate_rejects_unknown_environment():
    canonical, err = validate_environment("mars-colony")
    assert canonical is None
    assert err is not None
    assert "Unknown environment" in err
    assert "production" in err
