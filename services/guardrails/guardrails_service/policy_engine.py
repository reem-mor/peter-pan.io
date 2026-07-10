"""Pluggable policy-engine seam (BUILD_PLAN §3, GRD row: "NeMo stubbed behind same
interface").

Stage A ships only :class:`NoopPolicyEngine`. Stage C swaps in a NeMo
Guardrails-backed implementation behind the same :class:`PolicyEngine` protocol —
no route or caller code changes. The deterministic regex floor in :mod:`rules`
always runs regardless of which engine is plugged in here; the policy engine is
strictly additive.
"""

from __future__ import annotations

from typing import Protocol

from .contracts import Signal, TriageReport


class PolicyEngine(Protocol):
    """Additional policy checks layered on top of the deterministic regex floor."""

    def check_input(self, signal: Signal) -> list[str]:
        """Return extra flags for an inbound Signal. Empty list = no concerns raised."""
        ...

    def check_output(self, report: TriageReport) -> list[str]:
        """Return extra flags for an outbound TriageReport. Empty list = no concerns raised."""
        ...


class NoopPolicyEngine:
    """Stage A default — contributes no additional flags beyond the regex floor."""

    def check_input(self, signal: Signal) -> list[str]:
        return []

    def check_output(self, report: TriageReport) -> list[str]:
        return []
