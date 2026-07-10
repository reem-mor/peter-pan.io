"""Domain errors for the RAG service.

Replaces the deleted ``app.errors.BedrockError`` (ADR 0001 limitation 3):
this service no longer calls Bedrock directly, so the error type is
retrieval/validation-specific rather than provider-specific.
"""

from __future__ import annotations


class QueryValidationError(Exception):
    """Raised when an incoming /query question fails validation.

    Carries a ``code`` so the HTTP layer can map it to a stable, user-safe
    error reason without parsing the message text.
    """

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
