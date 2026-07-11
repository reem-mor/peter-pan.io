"""Unit tests for evaluation/run_e2e.py.

Strategy: inject an httpx.Client backed by MockTransport so no real HTTP
occurs. Tests cover dry-run, layer3, n8n-success, mismatch/failure, delivery
verification, and schema-error branches.

httpx.MockTransport takes a WSGI-style handler ``handler(request) -> Response``.
Each test builds a minimal handler for the calls it expects.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from unittest.mock import patch

import httpx
import pytest
from pydantic import ValidationError

import run_e2e


# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

NOW_ISO = datetime.now(timezone.utc).isoformat()

_GOLDEN_CASE_APP = {
    "id": "test-orders-api",
    "signal": {
        "id": "sig-golden0001",
        "source": "grafana",
        "kind": "alert",
        "received_at": "2026-07-10T12:00:00Z",
        "title": "orders-api 5xx spike",
        "body": "Error rate above 5%",
        "service": "orders-api",
        "environment": "production",
        "severity_hint": "warning",
        "labels": {},
        "raw": {},
    },
    "expected_category": "application",
    "expected_p_level": "P3",
}

_GOLDEN_CASE_DB = {
    "id": "test-postgres-pool",
    "signal": {
        "id": "sig-golden0002",
        "source": "webui",
        "kind": "manual",
        "received_at": "2026-07-10T12:05:00Z",
        "title": "postgres connection pool exhausted",
        "body": "Active connections at max",
        "service": "postgres-primary",
        "environment": "production",
        "severity_hint": "critical",
        "labels": {},
        "raw": {},
    },
    "expected_category": "database",
    "expected_p_level": "P1",
}

_VALID_TRIAGE_REPORT_APP: dict[str, Any] = {
    "incident_id": "inc-golden0001",
    "category": "application",
    "p_level": "P3",
    "summary": "Orders API 5xx spike after deploy",
    "probable_cause": "Bad deploy introduced a regression in the error handler",
    "citations": [{"source_id": "rb-001", "source_type": "runbook", "quote": "Rollback the deploy"}],
    "owner_team": "checkout",
    "escalation_path": ["on-call-engineer"],
    "recommended_steps": ["Check deploy pipeline"],
    "confidence": 0.88,
    "guardrail_flags": [],
    "generated_at": NOW_ISO,
    "model_meta": {"provider": "mock-openai-compatible", "stage": "A"},
}

_VALID_TRIAGE_REPORT_DB: dict[str, Any] = {
    "incident_id": "inc-golden0002",
    "category": "database",
    "p_level": "P1",
    "summary": "Postgres connection pool exhausted",
    "probable_cause": "Connection leak caused by long-running transactions",
    "citations": [{"source_id": "rb-002", "source_type": "runbook", "quote": "Restart connection pooler"}],
    "owner_team": "platform-db",
    "escalation_path": ["dba-on-call"],
    "recommended_steps": ["Check pg_stat_activity"],
    "confidence": 0.92,
    "guardrail_flags": [],
    "generated_at": NOW_ISO,
    "model_meta": {"provider": "mock-openai-compatible", "stage": "A"},
}


# ---------------------------------------------------------------------------
# MockTransport helpers
# ---------------------------------------------------------------------------


def _json_resp(data: Any, status: int = 200) -> httpx.Response:
    return httpx.Response(status, json=data)


def _make_transport(routes: dict[tuple[str, str], Any]) -> httpx.MockTransport:
    """Build a MockTransport from ``{(METHOD, url_prefix): response_or_callable}``."""

    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        method = request.method
        for (m, prefix), value in routes.items():
            if m == method and url.startswith(prefix):
                if callable(value):
                    return value(request)
                return value
        return httpx.Response(404, json={"error": f"unmatched mock: {method} {url}"})

    return httpx.MockTransport(handler)


def _client_factory(transport: httpx.MockTransport):
    def _make():
        return httpx.Client(transport=transport)

    return _make


# ---------------------------------------------------------------------------
# 1. Dry-run — no HTTP at all
# ---------------------------------------------------------------------------


def test_dry_run(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "GOLDEN_PATH", run_e2e.GOLDEN_PATH)  # real file
    result = run_e2e.main(["--dry-run"])
    assert result == 0


# ---------------------------------------------------------------------------
# 2. Layer 3 — all services healthy, golden path ok
# ---------------------------------------------------------------------------


def test_layer3_golden_ok(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_APP])

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8002/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8003/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8004/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8005/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8006/healthz"): _json_resp({"status": "ok"}),
        ("POST", "http://localhost:8004/check/input"): _json_resp({"pass": True}),
        ("POST", "http://localhost:8006/agent/run"): _json_resp(_VALID_TRIAGE_REPORT_APP),
        ("POST", "http://localhost:8004/check/output"): _json_resp({"pass": True}),
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "layer3", "--base-url", "http://localhost"],
        _client_factory=_client_factory(transport),
    )
    assert result == 0


# ---------------------------------------------------------------------------
# 3. Layer 3 — health failure → exit 1
# ---------------------------------------------------------------------------


def test_layer3_health_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_APP])

    def _unreachable(request):
        raise httpx.ConnectError("refused")

    routes: dict[tuple[str, str], Any] = {
        ("GET", "http://localhost:"): _unreachable,
    }
    transport = _make_transport(routes)
    with pytest.raises(SystemExit) as exc_info:
        run_e2e.main(
            ["--entrypoint", "layer3"],
            _client_factory=_client_factory(transport),
        )
    assert exc_info.value.code == 1


# ---------------------------------------------------------------------------
# 4. Layer 3 — category mismatch → mismatch status, exit 1
# ---------------------------------------------------------------------------


def test_layer3_category_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_APP])

    wrong_report = dict(_VALID_TRIAGE_REPORT_APP, category="infra", citations=[])

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8002/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8003/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8004/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8005/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8006/healthz"): _json_resp({"status": "ok"}),
        ("POST", "http://localhost:8004/check/input"): _json_resp({"pass": True}),
        ("POST", "http://localhost:8006/agent/run"): _json_resp(wrong_report),
        ("POST", "http://localhost:8004/check/output"): _json_resp({"pass": True}),
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "layer3"],
        _client_factory=_client_factory(transport),
    )
    assert result == 1  # mismatch → failure


# ---------------------------------------------------------------------------
# 5. Layer 3 — guardrails rejects signal → "rejected" status, still passes
# ---------------------------------------------------------------------------


def test_layer3_guardrail_rejection(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(
        run_e2e,
        "_load_golden",
        lambda: [{**_GOLDEN_CASE_APP, "expected_status": "rejected"}],
    )

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8002/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8003/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8004/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8005/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8006/healthz"): _json_resp({"status": "ok"}),
        ("POST", "http://localhost:8004/check/input"): _json_resp(
            {"pass": False, "reason": "owner mismatch"}
        ),
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "layer3"],
        _client_factory=_client_factory(transport),
    )
    assert result == 0  # rejected is a documented outcome, not a test failure


# ---------------------------------------------------------------------------
# 6. n8n — success path (ingestion forwards, stubs deliver correct report)
# ---------------------------------------------------------------------------


def test_n8n_success(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_APP])

    deliveries_store: list[dict] = []

    def _stubs_deliveries(req):
        return _json_resp(deliveries_store)

    def _stubs_delete(req):
        deliveries_store.clear()
        return _json_resp({"cleared": 0})

    call_count = {"signals": 0}

    def _ingestion_signals(req):
        # Simulate n8n processing by immediately populating deliveries
        call_count["signals"] += 1
        deliveries_store.append({
            "channel": "team:application",
            "payload": _VALID_TRIAGE_REPORT_APP,
        })
        return _json_resp(
            {"forwarded": True, "signal_id": "sig-golden0001", "n8n_status": 200},
            status=202,
        )

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8020/healthz"): _json_resp({"status": "ok"}),
        ("DELETE", "http://localhost:8020/deliveries"): _stubs_delete,
        ("POST", "http://localhost:8001/signals"): _ingestion_signals,
        ("GET", "http://localhost:8020/deliveries"): _stubs_deliveries,
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "n8n", "--poll-timeout", "5"],
        _client_factory=_client_factory(transport),
    )
    assert result == 0
    assert call_count["signals"] == 1


def test_n8n_accepts_internal_service_url_overrides(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_APP])

    routes = {
        ("GET", "http://ingestion:8000/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://integration-stubs:8000/healthz"): _json_resp(
            {"status": "ok"}
        ),
        ("DELETE", "http://integration-stubs:8000/deliveries"): _json_resp(
            {"cleared": 0}
        ),
        ("POST", "http://ingestion:8000/signals"): _json_resp(
            {"forwarded": True, "signal_id": "sig-golden0001", "n8n_status": 200},
            status=202,
        ),
        ("GET", "http://integration-stubs:8000/deliveries"): _json_resp(
            [{"channel": "team:application", "payload": _VALID_TRIAGE_REPORT_APP}]
        ),
    }

    result = run_e2e.main(
        [
            "--entrypoint",
            "n8n",
            "--ingestion-url",
            "http://ingestion:8000",
            "--stubs-url",
            "http://integration-stubs:8000",
            "--poll-timeout",
            "5",
        ],
        _client_factory=_client_factory(_make_transport(routes)),
    )

    assert result == 0


# ---------------------------------------------------------------------------
# 7. n8n — delivery has wrong category → mismatch, exit 1
# ---------------------------------------------------------------------------


def test_n8n_category_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_APP])

    wrong_report = dict(_VALID_TRIAGE_REPORT_APP, category="infra", p_level="P4")

    def _ingestion_signals(req):
        return _json_resp(
            {"forwarded": True, "signal_id": "sig-golden0001", "n8n_status": 200},
            status=202,
        )

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8020/healthz"): _json_resp({"status": "ok"}),
        ("DELETE", "http://localhost:8020/deliveries"): _json_resp({"cleared": 0}),
        ("POST", "http://localhost:8001/signals"): _ingestion_signals,
        ("GET", "http://localhost:8020/deliveries"): _json_resp([
            {"channel": "team:infra", "payload": wrong_report}
        ]),
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "n8n", "--poll-timeout", "5"],
        _client_factory=_client_factory(transport),
    )
    assert result == 1


# ---------------------------------------------------------------------------
# 8. n8n — flagged report → review-queue delivery, accepted as "flagged"
# ---------------------------------------------------------------------------


def test_n8n_flagged_branch(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(
        run_e2e,
        "_load_golden",
        lambda: [{**_GOLDEN_CASE_APP, "expected_status": "flagged"}],
    )

    flagged_report = dict(_VALID_TRIAGE_REPORT_APP, guardrail_flags=["owner_mismatch"])

    def _ingestion_signals(req):
        return _json_resp(
            {"forwarded": True, "signal_id": "sig-golden0001", "n8n_status": 200},
            status=202,
        )

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8020/healthz"): _json_resp({"status": "ok"}),
        ("DELETE", "http://localhost:8020/deliveries"): _json_resp({"cleared": 0}),
        ("POST", "http://localhost:8001/signals"): _ingestion_signals,
        ("GET", "http://localhost:8020/deliveries"): _json_resp([
            {"channel": "review", "payload": {"report": flagged_report, "flags": ["owner_mismatch"]}}
        ]),
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "n8n", "--poll-timeout", "5"],
        _client_factory=_client_factory(transport),
    )
    # "flagged" is a documented branch — harness passes
    assert result == 0


# ---------------------------------------------------------------------------
# 9. Invalid frozen Signal is rejected before any HTTP call
# ---------------------------------------------------------------------------


def test_n8n_signal_validation_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    bad_case = dict(_GOLDEN_CASE_APP)
    bad_case = {**bad_case, "signal": {**bad_case["signal"], "id": "bad-id"}}
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [bad_case])

    with pytest.raises(ValidationError):
        run_e2e.main(
            ["--entrypoint", "n8n", "--poll-timeout", "5"],
            _client_factory=lambda: (_ for _ in ()).throw(
                AssertionError("HTTP client must not be created")
            ),
        )


# ---------------------------------------------------------------------------
# 10. n8n — delivery timeout → timeout status, exit 1
# ---------------------------------------------------------------------------


def test_n8n_delivery_timeout(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_APP])
    # Suppress sleep to keep the test fast
    monkeypatch.setattr(run_e2e.time, "sleep", lambda _: None)
    monkeypatch.setattr(run_e2e.time, "monotonic", _fast_monotonic())

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8020/healthz"): _json_resp({"status": "ok"}),
        ("DELETE", "http://localhost:8020/deliveries"): _json_resp({"cleared": 0}),
        ("POST", "http://localhost:8001/signals"): _json_resp(
            {"forwarded": True, "signal_id": "sig-golden0001", "n8n_status": 200},
            status=202,
        ),
        # Deliveries endpoint always returns empty → simulates n8n never delivering
        ("GET", "http://localhost:8020/deliveries"): _json_resp([]),
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "n8n", "--poll-timeout", "0.001"],
        _client_factory=_client_factory(transport),
    )
    assert result == 1  # timeout → failure


# ---------------------------------------------------------------------------
# 11. n8n — delivery verification: DB case routed to team:database channel
# ---------------------------------------------------------------------------


def test_n8n_db_delivery_channel(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_DB])

    def _ingestion_signals(req):
        return _json_resp(
            {"forwarded": True, "signal_id": "sig-golden0002", "n8n_status": 200},
            status=202,
        )

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8020/healthz"): _json_resp({"status": "ok"}),
        ("DELETE", "http://localhost:8020/deliveries"): _json_resp({"cleared": 0}),
        ("POST", "http://localhost:8001/signals"): _ingestion_signals,
        ("GET", "http://localhost:8020/deliveries"): _json_resp([
            {"channel": "team:database", "payload": _VALID_TRIAGE_REPORT_DB}
        ]),
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "n8n", "--poll-timeout", "5"],
        _client_factory=_client_factory(transport),
    )
    assert result == 0


# ---------------------------------------------------------------------------
# 12. n8n — wrong delivery channel mismatch (report delivered to wrong team)
# ---------------------------------------------------------------------------


def test_n8n_wrong_delivery_channel(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_APP])

    # Report has correct category but was delivered to wrong team channel
    report_wrong_channel = dict(_VALID_TRIAGE_REPORT_APP)

    def _ingestion_signals(req):
        return _json_resp(
            {"forwarded": True, "signal_id": "sig-golden0001", "n8n_status": 200},
            status=202,
        )

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8020/healthz"): _json_resp({"status": "ok"}),
        ("DELETE", "http://localhost:8020/deliveries"): _json_resp({"cleared": 0}),
        ("POST", "http://localhost:8001/signals"): _ingestion_signals,
        # Delivered to database team instead of application team
        ("GET", "http://localhost:8020/deliveries"): _json_resp([
            {"channel": "team:database", "payload": report_wrong_channel}
        ]),
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "n8n", "--poll-timeout", "5"],
        _client_factory=_client_factory(transport),
    )
    assert result == 1  # wrong channel → mismatch → failure


# ---------------------------------------------------------------------------
# 13. n8n — n8n not configured (degraded), not a failure if expected
# ---------------------------------------------------------------------------


def test_n8n_degraded_forwarding(tmp_path, monkeypatch):
    monkeypatch.setattr(run_e2e, "RESULTS_DIR", tmp_path / "results")
    monkeypatch.setattr(run_e2e, "_load_golden", lambda: [_GOLDEN_CASE_APP])

    routes = {
        ("GET", "http://localhost:8001/healthz"): _json_resp({"status": "ok"}),
        ("GET", "http://localhost:8020/healthz"): _json_resp({"status": "ok"}),
        ("DELETE", "http://localhost:8020/deliveries"): _json_resp({"cleared": 0}),
        ("POST", "http://localhost:8001/signals"): _json_resp(
            {"forwarded": False, "reason": "n8n webhook not configured"},
            status=202,
        ),
    }
    transport = _make_transport(routes)
    result = run_e2e.main(
        ["--entrypoint", "n8n", "--poll-timeout", "5"],
        _client_factory=_client_factory(transport),
    )
    # degraded is an error in CI (n8n is required for the n8n entrypoint)
    assert result == 1


# ---------------------------------------------------------------------------
# 14. Unit: _find_triage_delivery helpers
# ---------------------------------------------------------------------------


def test_find_triage_delivery_category_match():
    deliveries = [
        {"channel": "team:application", "payload": _VALID_TRIAGE_REPORT_APP},
        {"channel": "team:database", "payload": _VALID_TRIAGE_REPORT_DB},
    ]
    result = run_e2e._find_triage_delivery(deliveries, "application")
    assert result is not None
    assert result["channel"] == "team:application"


def test_find_triage_delivery_review_queue():
    flagged_report = dict(_VALID_TRIAGE_REPORT_APP, guardrail_flags=["test_flag"])
    deliveries = [
        {"channel": "review", "payload": {"report": flagged_report, "flags": ["test_flag"]}},
    ]
    result = run_e2e._find_triage_delivery(deliveries, "application")
    assert result is not None
    assert result["channel"] == "review"


def test_find_triage_delivery_empty():
    result = run_e2e._find_triage_delivery([], "application")
    assert result is None


def test_find_triage_delivery_no_triage_fields():
    deliveries = [{"channel": "slack", "payload": {"text": "hello"}}]
    result = run_e2e._find_triage_delivery(deliveries, "application")
    assert result is None


# ---------------------------------------------------------------------------
# 15. Unit: _validate_report_contract
# ---------------------------------------------------------------------------


def test_validate_report_contract_valid():
    error = run_e2e._validate_report_contract(_VALID_TRIAGE_REPORT_APP)
    assert error is None


def test_validate_report_contract_missing_field():
    incomplete = {k: v for k, v in _VALID_TRIAGE_REPORT_APP.items() if k != "citations"}
    error = run_e2e._validate_report_contract(incomplete)
    assert error is not None
    assert "citations" in error.lower() or "field required" in error.lower() or "missing" in error.lower()


def test_validate_report_contract_bad_category():
    bad = dict(_VALID_TRIAGE_REPORT_APP, category="unknown_cat")
    error = run_e2e._validate_report_contract(bad)
    assert error is not None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fast_monotonic():
    """Returns a monotonic counter that advances by 1 on each call."""
    calls = [0.0]

    def _fn():
        calls[0] += 100.0  # each call jumps 100s → immediately past any timeout
        return calls[0]

    return _fn
