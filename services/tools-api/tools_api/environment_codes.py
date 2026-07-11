"""Canonical environment codes and optional aliases for demo datasets and tools."""

from __future__ import annotations

CANONICAL_ENVIRONMENTS: frozenset[str] = frozenset({"production", "staging"})

_ENV_ALIASES: dict[str, str] = {
    "PROD": "production",
    "PRD": "production",
    "LIVE": "production",
    "STAGE": "staging",
    "STG": "staging",
    "TEST": "staging",
}


def normalize_environment(raw: str | None) -> str:
    """Return canonical environment code; pass through unknown values lowercased."""
    token = (raw or "").strip()
    if not token:
        return ""
    lowered = token.lower()
    if lowered in CANONICAL_ENVIRONMENTS:
        return lowered
    return _ENV_ALIASES.get(token.upper(), lowered)


def validate_environment(raw: str | None) -> tuple[str | None, str | None]:
    """Validate and normalize an environment code.

    Returns ``(canonical, None)`` on success or ``(None, error_message)`` on failure.
    """
    token = (raw or "").strip()
    if not token:
        return None, "environment is required"
    canonical = normalize_environment(token)
    if canonical not in CANONICAL_ENVIRONMENTS:
        allowed = ", ".join(sorted(CANONICAL_ENVIRONMENTS))
        return None, (
            f"Unknown environment '{token}'. "
            f"Use one of: {allowed} (aliases: PROD, STAGING, STG)."
        )
    return canonical, None
