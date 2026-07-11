"""Pure question validation for the RAG /query endpoint.

Operator/destructive-action checks belong to the guardrails service; this
module only validates that a question is well-formed
enough to retrieve against (non-empty, in-range length, has searchable
keywords). It never inspects intent.
"""

from __future__ import annotations

import re

from rag_service.errors import QueryValidationError

MIN_QUESTION_LEN = 3
MAX_QUESTION_LEN = 500

_STOPWORDS = frozenset(
    {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "of",
        "to",
        "in",
        "on",
        "for",
        "with",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "it",
        "this",
        "that",
        "these",
        "those",
        "as",
        "by",
        "at",
        "from",
        "i",
        "you",
        "he",
        "she",
        "they",
        "we",
        "do",
        "does",
        "did",
        "not",
        "no",
        "yes",
        "if",
        "then",
        "than",
        "so",
        "what",
        "who",
        "when",
        "where",
        "why",
        "how",
        "which",
        "about",
    }
)


def tokenize(text: str) -> list[str]:
    """Extract searchable tokens (length > 1, not stopwords)."""
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return [t for t in cleaned.split() if len(t) > 1 and t not in _STOPWORDS]


def validate_question(question: str) -> str:
    """Return the trimmed question or raise QueryValidationError with a stable code."""
    trimmed = (question or "").strip()
    if not trimmed:
        raise QueryValidationError("Please enter a question.", code="empty_question")
    if len(trimmed) < MIN_QUESTION_LEN:
        raise QueryValidationError(
            "Type a question with at least 3 characters.",
            code="short_question",
        )
    if len(trimmed) > MAX_QUESTION_LEN:
        raise QueryValidationError(
            f"Question is too long ({len(trimmed)} chars). Maximum is {MAX_QUESTION_LEN}.",
            code="oversize_question",
        )
    if not tokenize(trimmed):
        raise QueryValidationError(
            "Your question has no searchable keywords. Try rephrasing.",
            code="stopwords_only",
        )
    return trimmed
