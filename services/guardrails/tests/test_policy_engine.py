"""NoopPolicyEngine is a documented no-op seam for the Stage C NeMo Guardrails swap."""

from __future__ import annotations

from datetime import datetime, timezone

from guardrails_service.contracts import Signal, TriageReport
from guardrails_service.policy_engine import NoopPolicyEngine


def test_noop_policy_engine_never_adds_flags() -> None:
    engine = NoopPolicyEngine()
    signal = Signal(
        id="sig-abc12345",
        source="grafana",
        kind="alert",
        received_at=datetime.now(timezone.utc),
        title="P1 latency spike",
    )
    report = TriageReport(
        incident_id="inc-abc12345",
        category="infra",
        p_level="P2",
        summary="s",
        probable_cause="c",
        citations=[{"source_id": "x", "source_type": "runbook", "quote": "q"}],
        owner_team="orders-platform",
        confidence=0.5,
        generated_at=datetime.now(timezone.utc),
    )
    assert engine.check_input(signal) == []
    assert engine.check_output(report) == []
