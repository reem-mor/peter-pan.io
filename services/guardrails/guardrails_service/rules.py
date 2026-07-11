"""Deterministic regex guardrail floor, isolated from the retired legacy application.

Self-contained: no ``app.*`` imports, no ``BedrockError`` dependency.

Two entry points:

- :func:`scan_text` returns *every* disallowed-operational-action match instead of
  raising, for callers (the FastAPI routes) that need to accumulate all guardrail
  flags for a single response.
- :func:`check_operator_guardrails` raises :class:`GuardrailViolation` on the first
  match — kept for direct unit tests mirroring the legacy behaviour.

This floor always runs regardless of which :mod:`policy_engine` is plugged in
(NeMo Guardrails lands behind that seam at Stage C — BUILD_PLAN §4).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import GuardrailViolation


@dataclass(frozen=True)
class RuleMatch:
    code: str
    reason: str


# Destructive or high-blast-radius actions — block unless user explicitly asks for review only.
_DANGEROUS_PATTERNS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (
        re.compile(
            r"\b(flushall|flushdb|drop\s+database|drop\s+table|truncate\s+table|"
            r"delete\s+from\s+\w+|rm\s+-rf|format\s+disk|wipe\s+data)\b",
            re.I,
        ),
        "destructive_data_action",
        "That request involves destructive data operations. PETER PAN will not provide "
        "execution steps for FLUSHALL, DROP, TRUNCATE, or mass deletes. "
        "Escalate to the database owner and follow the approved runbook with change control.",
    ),
    (
        re.compile(
            r"\b(promote\s+replica|failover\s+primary|force\s+failover|"
            r"take\s+primary\s+offline|disable\s+replication)\b",
            re.I,
        ),
        "unsafe_failover_action",
        "Failover and replica promotion require explicit approval from the platform "
        "SRE and database owner. PETER PAN can explain the runbook criteria but will not "
        "auto-recommend production failover without cited evidence and human sign-off.",
    ),
    (
        re.compile(
            r"\b(disable\s+waf|turn\s+off\s+waf|remove\s+rate\s+limit|"
            r"open\s+firewall|0\.0\.0\.0/0|disable\s+mfa|bypass\s+auth)\b",
            re.I,
        ),
        "security_control_bypass",
        "Disabling WAF, MFA, auth, or widening firewall rules is not permitted through "
        "this assistant. Open a security-reviewed change request if policy allows an exception.",
    ),
    (
        re.compile(
            r"\b(kill\s+all\s+sessions|terminate\s+all|pg_terminate_backend\s*\(\s*\)|"
            r"restart\s+all\s+pods|scale\s+to\s+zero)\b",
            re.I,
        ),
        "mass_disruption_action",
        "Mass session termination or fleet-wide restarts can cause cascading outages. "
        "Use targeted remediation from the cited runbook and confirm blast radius with on-call.",
    ),
)

# Requests to bypass PETER PAN safety / notification gates.
_POLICY_BYPASS_PATTERNS: tuple[tuple[re.Pattern[str], str, str], ...] = (
    (
        re.compile(
            r"\b(skip\s+confirmation|bypass\s+allowlist|ignore\s+allowlist|"
            r"send\s+without\s+token|disable\s+guardrail|turn\s+off\s+safety)\b",
            re.I,
        ),
        "policy_bypass_request",
        "Notification and escalation safety gates cannot be bypassed from chat. "
        "Use the Escalate on-call flow with a valid confirmation token and allowlisted recipient.",
    ),
    (
        re.compile(
            r"\b(remove\s+escalation|cancel\s+all\s+alerts|silence\s+all|"
            r"delete\s+incident|purge\s+audit)\b",
            re.I,
        ),
        "audit_or_escalation_tamper",
        "PETER PAN cannot remove audit trails, silence all alerts, or delete incidents. "
        "Use approved incident management tools and document actions in the ticket.",
    ),
)

_ALL_TEXT_PATTERNS = _DANGEROUS_PATTERNS + _POLICY_BYPASS_PATTERNS


def scan_text(text: str) -> list[RuleMatch]:
    """Return every disallowed-operational-action match found in ``text``."""
    haystack = (text or "").strip()
    if not haystack:
        return []
    return [
        RuleMatch(code=code, reason=reason)
        for pattern, code, reason in _ALL_TEXT_PATTERNS
        if pattern.search(haystack)
    ]


def check_operator_guardrails(text: str) -> None:
    """Raise GuardrailViolation on the first disallowed-operational-action match."""
    matches = scan_text(text)
    if matches:
        first = matches[0]
        raise GuardrailViolation(first.reason, code=first.code)


# Destructive commands disallowed in TriageReport.recommended_steps (output guardrail floor).
_DESTRUCTIVE_STEP_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.I)
    for pattern in (
        r"\brm\s+-rf\b",
        r"\bdrop\s+table\b",
        r"\bdrop\s+database\b",
        r"\btruncate\b",
        r"\bshutdown\b",
        r"\breboot\b",
        r"\bkill\s+-9\b",
        r"\bdelete\s+from\b",
        r"\bterminate-instances\b",
        r"\bformat\b",
        r"\bmkfs\b",
    )
)


def find_destructive_steps(steps: list[str]) -> list[str]:
    """Return the subset of ``steps`` that contain a disallowed destructive command."""
    return [
        step
        for step in steps
        if any(pattern.search(step) for pattern in _DESTRUCTIVE_STEP_PATTERNS)
    ]
