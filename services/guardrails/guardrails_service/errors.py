"""Guardrail-specific exceptions.

This service is self-contained and never imports the retired application's
provider-specific errors.
"""

from __future__ import annotations


class GuardrailViolation(Exception):
    """Raised when a deterministic regex/policy check rejects a request or response.

    Carries a stable ``code`` (used as a guardrail flag in API responses) and a
    human-readable ``reason`` message.
    """

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code
        self.reason = message
