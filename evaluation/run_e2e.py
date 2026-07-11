#!/usr/bin/env python3
"""Stage A end-to-end harness — golden Signal fixtures through core services.

Usage:
  python evaluation/run_e2e.py --dry-run
  python evaluation/run_e2e.py --entrypoint layer3 --base-url http://localhost
  python evaluation/run_e2e.py --entrypoint n8n --base-url http://localhost

Entrypoints:
  layer3  Direct service-to-service path (guardrails → agent → guardrails).
          Default. Fast; does not require n8n.
  n8n     Full orchestration path. POSTs each golden Signal to the Ingestion
          service, which forwards to n8n. Polls integration-stubs /deliveries
          until a TriageReport arrives, validates it against the canonical
          pydantic contract, checks expected category/p_level, and verifies
          the delivery was routed to the correct team channel.

Asserts zero external API calls by targeting only local compose endpoints.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import httpx

ROOT = Path(__file__).resolve().parent.parent
GOLDEN_PATH = Path(__file__).resolve().parent / "golden_signals.json"
RESULTS_DIR = Path(
    os.environ.get(
        "PETER_EVALUATION_RESULTS_DIR",
        str(Path(__file__).resolve().parent / "results"),
    )
)

# ---------------------------------------------------------------------------
# Canonical contract loader (lazy, cached)
# ---------------------------------------------------------------------------
_TriageReport: type | None = None
_Incident: type | None = None
_Signal: type | None = None
_ValidationError: type = Exception


def _load_contracts() -> None:
    """Import TriageReport and ValidationError from the canonical contracts file.

    Uses importlib so we don't pollute sys.path. model_rebuild() is required
    because pydantic v2 defers resolution of forward references; loading via
    importlib.util breaks the normal module-level resolution, so we trigger it
    explicitly after exec.
    """
    global _TriageReport, _Incident, _Signal, _ValidationError
    if _TriageReport is not None:
        return
    import importlib.util
    from typing import Literal  # noqa: F401 — ensure Literal is in scope for rebuild

    spec = importlib.util.spec_from_file_location(
        "_peter_contracts",
        ROOT / "docs" / "contracts" / "contracts.py",
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules["_peter_contracts"] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    # Rebuild all models so pydantic resolves Literal annotations correctly.
    for attr in ("Signal", "IncidentContext", "Incident", "Citation", "TriageReport"):
        cls = getattr(mod, attr, None)
        if cls is not None and hasattr(cls, "model_rebuild"):
            cls.model_rebuild()
    _TriageReport = mod.TriageReport
    _Incident = mod.Incident
    _Signal = mod.Signal
    from pydantic import ValidationError

    _ValidationError = ValidationError


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _load_golden() -> list[dict[str, Any]]:
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))


def _layer3_source_hash() -> str:
    paths = [
        *ROOT.glob("services/**/*.py"),
        *ROOT.glob("packages/**/*.py"),
        *ROOT.glob("scripts/*.py"),
    ]
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(ROOT).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _validate_cases(cases: list[dict[str, Any]]) -> None:
    _load_contracts()
    seen_ids: set[str] = set()
    for case in cases:
        case_id = str(case.get("id", ""))
        if not case_id or case_id in seen_ids:
            raise ValueError(f"golden case id is missing or duplicated: {case_id!r}")
        seen_ids.add(case_id)
        _Signal.model_validate(case.get("signal"))  # type: ignore[union-attr]
        expected_status = case.get("expected_status", "ok")
        if expected_status not in {"ok", "rejected", "suppressed", "flagged"}:
            raise ValueError(f"{case_id}: unsupported expected_status={expected_status!r}")
        if expected_status == "ok":
            if case.get("expected_category") not in {
                "application",
                "database",
                "infra",
            }:
                raise ValueError(f"{case_id}: expected_category is required")
            if case.get("expected_p_level") not in {"P1", "P2", "P3", "P4"}:
                raise ValueError(f"{case_id}: expected_p_level is required")


def _service_urls(base_url: str) -> dict[str, str]:
    ports = {
        "ingestion": 8001,
        "predictor": 8002,
        "rag": 8003,
        "guardrails": 8004,
        "tools-api": 8005,
        "langgraph-agent": 8006,
    }
    return {name: f"{base_url.rstrip('/')}:{port}" for name, port in ports.items()}


def _stubs_url(base_url: str) -> str:
    return f"{base_url.rstrip('/')}:8020"


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"} if token else {}


def _check_health(
    client: httpx.Client, urls: dict[str, str]
) -> list[str]:
    failures: list[str] = []
    for name, url in urls.items():
        try:
            resp = client.get(f"{url}/healthz", timeout=5.0)
            if resp.status_code != 200:
                failures.append(f"{name} healthz -> {resp.status_code}")
        except httpx.HTTPError as exc:
            failures.append(f"{name} unreachable: {exc}")
    return failures


# ---------------------------------------------------------------------------
# Layer 3 entrypoint (direct service calls — existing behaviour)
# ---------------------------------------------------------------------------


def _incident_from_signal(signal: dict[str, Any]) -> dict[str, Any]:
    priority_map = {"critical": "P1", "warning": "P3", "info": "P4"}
    incident = {
        "id": signal["id"].replace("sig-", "inc-"),
        "created_at": signal["received_at"],
        "status": "triaging",
        "signal_ids": [signal["id"]],
        "service": signal.get("service") or "unknown",
        "environment": signal.get("environment") or "production",
        "p_level": priority_map.get(signal.get("severity_hint") or "", "P3"),
        "started_at": None,
        "symptom": signal.get("body") or signal.get("title"),
        "context": {
            "maintenance_window": False,
            "recent_deploys": [],
            "complaint_count": 0,
            "complaint_samples": [],
        },
    }
    _load_contracts()
    return _Incident.model_validate(incident).model_dump(mode="json")  # type: ignore[union-attr]


def _run_golden_path(
    client: httpx.Client,
    urls: dict[str, str],
    token: str,
    case: dict[str, Any],
) -> dict[str, Any]:
    signal = case["signal"]
    headers = _headers(token)

    input_check = client.post(
        f"{urls['guardrails']}/check/input",
        json={"signal": signal},
        headers=headers,
        timeout=10.0,
    )
    input_check.raise_for_status()
    if not input_check.json().get("passed"):
        return {"id": case["id"], "status": "rejected", "reason": input_check.json()}

    incident = _incident_from_signal(signal)
    agent_response = client.post(
        f"{urls['langgraph-agent']}/agent/run",
        json={"incident": incident, "question": signal.get("title")},
        headers=headers,
        timeout=15.0,
    )
    agent_response.raise_for_status()
    report = agent_response.json()
    contract_error = _validate_report_contract(report)
    if contract_error:
        return {
            "id": case["id"],
            "status": "schema_error",
            "error": contract_error,
        }

    output_check = client.post(
        f"{urls['guardrails']}/check/output",
        json={
            "report": report,
            "service": signal.get("service"),
            "environment": signal.get("environment"),
        },
        headers=headers,
        timeout=10.0,
    )
    output_check.raise_for_status()
    output_verdict = output_check.json()

    ok = (
        report.get("category") == case.get("expected_category")
        and report.get("p_level") == case.get("expected_p_level")
        and len(report.get("citations", [])) >= 1
        and output_verdict.get("passed") is True
    )
    return {
        "id": case["id"],
        "status": "ok" if ok else "mismatch",
        "category": report.get("category"),
        "p_level": report.get("p_level"),
        "guardrail_pass": output_verdict.get("passed"),
    }


def _run_layer3_entrypoint(
    cases: list[dict[str, Any]],
    base_url: str,
    token: str,
    client: httpx.Client,
) -> list[dict[str, Any]]:
    urls = _service_urls(base_url)
    health_failures = _check_health(client, urls)
    if health_failures:
        for failure in health_failures:
            print(f"HEALTH FAIL: {failure}")
        raise SystemExit(1)

    results: list[dict[str, Any]] = []
    for case in cases:
        try:
            result = _run_golden_path(client, urls, token, case)
        except httpx.HTTPError as exc:
            result = {"id": case["id"], "status": "error", "error": str(exc)}
        results.append(result)
        print(result)
    return results


# ---------------------------------------------------------------------------
# n8n entrypoint (full orchestration path)
# ---------------------------------------------------------------------------

_TRIAGE_REQUIRED_KEYS = frozenset(
    {"incident_id", "category", "p_level", "citations", "owner_team", "confidence"}
)

_CATEGORY_CHANNEL: dict[str, str] = {
    "application": "team:application",
    "database": "team:database",
    "infra": "team:infra",
}


def _looks_like_triage_report(obj: Any) -> bool:
    """Heuristic: does this dict have the required TriageReport top-level fields?"""
    return isinstance(obj, dict) and _TRIAGE_REQUIRED_KEYS.issubset(obj.keys())


def _find_triage_delivery(
    deliveries: list[dict[str, Any]],
    expected_category: str | None,
) -> dict[str, Any] | None:
    """Locate the primary TriageReport delivery in integration-stubs /deliveries.

    Preference order:
    1. Expected category team channel (e.g. team:application)
    2. Review-queue channel (flagged reports)
    3. Any channel carrying a TriageReport payload
    """
    expected_channel = _CATEGORY_CHANNEL.get(expected_category or "", "")

    for d in deliveries:
        if expected_channel and d.get("channel") == expected_channel:
            if _looks_like_triage_report(d.get("payload")):
                return d

    for d in deliveries:
        if d.get("channel") == "review":
            # review-queue wraps as {"report": ..., "flags": [...]}
            inner = d.get("payload", {})
            report = inner.get("report", inner)
            if _looks_like_triage_report(report):
                return d

    for d in deliveries:
        if _looks_like_triage_report(d.get("payload")):
            return d
        inner = d.get("payload", {})
        if _looks_like_triage_report(inner.get("report", {})):
            return d

    return None


def _validate_report_contract(report: dict[str, Any]) -> str | None:
    """Validate report against the canonical pydantic TriageReport model.

    Returns None on success, an error description on failure.
    """
    _load_contracts()
    try:
        _TriageReport(**report)  # type: ignore[misc]
        return None
    except _ValidationError as exc:
        return str(exc)


def _validate_n8n_delivery(
    case: dict[str, Any],
    delivery: dict[str, Any],
) -> dict[str, Any]:
    """Validate a TriageReport delivery against case expectations."""
    channel = delivery.get("channel", "")
    payload = delivery.get("payload", {})
    is_review = channel == "review"

    report: dict[str, Any]
    if is_review:
        inner = payload if _looks_like_triage_report(payload) else payload.get("report", payload)
        report = inner
    else:
        report = payload

    contract_error = _validate_report_contract(report)
    if contract_error:
        return {
            "id": case["id"],
            "status": "schema_error",
            "channel": channel,
            "error": contract_error,
        }

    expected_category = case.get("expected_category")
    expected_p_level = case.get("expected_p_level")
    actual_category = report.get("category")
    actual_p_level = report.get("p_level")
    guardrail_flags = report.get("guardrail_flags", [])
    provider = report.get("model_meta", {}).get("provider", "")
    evidence = report.get("model_meta", {}).get("evidence", "")
    is_flagged = len(guardrail_flags) > 0

    # Flagged reports are routed to review-queue — this is a documented branch, not a failure.
    if is_flagged:
        if not is_review:
            return {
                "id": case["id"],
                "status": "mismatch",
                "channel": channel,
                "reason": "flagged report was not delivered to the review queue",
            }
        return {
            "id": case["id"],
            "status": "flagged",
            "channel": channel,
            "flags": guardrail_flags,
            "category": actual_category,
            "p_level": actual_p_level,
            "provider": provider,
            "evidence": evidence,
        }

    # Verify delivery channel matches expected category
    expected_channel = _CATEGORY_CHANNEL.get(expected_category or "", "")
    channel_ok = not expected_channel or channel == expected_channel

    category_ok = (expected_category is None) or (actual_category == expected_category)
    p_level_ok = (expected_p_level is None) or (actual_p_level == expected_p_level)

    if category_ok and p_level_ok and channel_ok:
        return {
            "id": case["id"],
            "status": "ok",
            "channel": channel,
            "category": actual_category,
            "p_level": actual_p_level,
            "provider": provider,
            "evidence": evidence,
        }

    return {
        "id": case["id"],
        "status": "mismatch",
        "channel": channel,
        "expected_category": expected_category,
        "actual_category": actual_category,
        "expected_p_level": expected_p_level,
        "actual_p_level": actual_p_level,
        "channel_ok": channel_ok,
        "provider": provider,
        "evidence": evidence,
    }


def _verify_p1_preview(
    client: httpx.Client,
    tools_base: str,
    headers: dict[str, str],
    incident_id: str,
    timeout: float = 10.0,
    poll_interval: float = 0.5,
) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = client.get(f"{tools_base}/audit", headers=headers, timeout=5.0)
        response.raise_for_status()
        entries = response.json()
        if any(
            entry.get("incident_id") == incident_id
            and entry.get("p_level") == "P1"
            and entry.get("preview_requested") is True
            and entry.get("dispatched") is False
            for entry in entries
        ):
            return True
        time.sleep(poll_interval)
    return False


def _run_signal_via_n8n(
    client: httpx.Client,
    ingestion_url: str,
    stubs_base: str,
    tools_base: str,
    token: str,
    case: dict[str, Any],
    poll_timeout: float,
    poll_interval: float = 1.5,
) -> dict[str, Any]:
    """Post one golden Signal through Ingestion → n8n, then verify delivery."""
    signal = case["signal"]
    headers = _headers(token)

    # Clear previous deliveries so we get a clean slate for this case.
    clear_response = client.delete(
        f"{stubs_base}/deliveries",
        headers=headers,
        timeout=5.0,
    )
    clear_response.raise_for_status()

    # POST to Ingestion — Ingestion validates, normalises, forwards to n8n.
    resp = client.post(
        f"{ingestion_url}/signals",
        json=signal,
        headers=headers,
        timeout=15.0,
    )

    if resp.status_code == 422:
        detail = resp.json()
        expected_status = case.get("expected_status", "ok")
        if expected_status == "rejected":
            return {"id": case["id"], "status": "rejected", "reason": "validation_failed", "detail": detail}
        return {"id": case["id"], "status": "schema_error", "error": "Signal failed ingestion validation", "detail": detail}

    resp.raise_for_status()
    ingestion_data = resp.json()

    if not ingestion_data.get("forwarded", True):
        return {
            "id": case["id"],
            "status": "degraded",
            "reason": ingestion_data.get("reason", "n8n not configured"),
        }

    n8n_response = ingestion_data.get("n8n_response")
    if isinstance(n8n_response, dict) and n8n_response.get("status") in {
        "rejected",
        "suppressed",
    }:
        return {
            "id": case["id"],
            "status": n8n_response["status"],
            "reason": n8n_response.get("reason", ""),
        }

    # Poll integration-stubs until n8n delivers a TriageReport.
    expected_category = case.get("expected_category")
    deadline = time.monotonic() + poll_timeout
    while time.monotonic() < deadline:
        try:
            deliveries_resp = client.get(
                f"{stubs_base}/deliveries",
                headers=headers,
                timeout=5.0,
            )
            deliveries_resp.raise_for_status()
            deliveries = deliveries_resp.json()
        except httpx.HTTPError:
            time.sleep(poll_interval)
            continue

        delivery = _find_triage_delivery(deliveries, expected_category)
        if delivery is not None:
            result = _validate_n8n_delivery(case, delivery)
            if result.get("status") == "ok" and result.get("p_level") == "P1":
                incident_id = (
                    delivery.get("payload", {}).get("incident_id")
                    if isinstance(delivery.get("payload"), dict)
                    else ""
                )
                if not _verify_p1_preview(
                    client, tools_base, headers, str(incident_id or "")
                ):
                    return {
                        **result,
                        "status": "escalation_missing",
                        "reason": "P1 escalation preview audit record was not found",
                    }
                result["p1_preview"] = True
            return result

        time.sleep(poll_interval)

    return {
        "id": case["id"],
        "status": "timeout",
        "reason": f"No TriageReport delivery within {poll_timeout:.0f}s",
    }


def _run_n8n_entrypoint(
    cases: list[dict[str, Any]],
    base_url: str,
    token: str,
    poll_timeout: float,
    client: httpx.Client,
    ingestion_url: str | None = None,
    stubs_base: str | None = None,
    tools_base: str | None = None,
) -> list[dict[str, Any]]:
    ingestion_url = ingestion_url or f"{base_url.rstrip('/')}:8001"
    stubs_base = stubs_base or _stubs_url(base_url)
    tools_base = tools_base or f"{base_url.rstrip('/')}:8005"

    health_targets = {
        "ingestion": ingestion_url,
        "integration-stubs": stubs_base,
    }
    health_failures = _check_health(client, health_targets)
    if health_failures:
        for failure in health_failures:
            print(f"HEALTH FAIL: {failure}")
        raise SystemExit(1)

    results: list[dict[str, Any]] = []
    for case in cases:
        try:
            result = _run_signal_via_n8n(
                client,
                ingestion_url,
                stubs_base,
                tools_base,
                token,
                case,
                poll_timeout=poll_timeout,
            )
        except httpx.HTTPError as exc:
            result = {"id": case["id"], "status": "error", "error": str(exc)}
        results.append(result)
        print(result)

    return results


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main(
    argv: list[str] | None = None,
    _client_factory: Callable[[], httpx.Client] | None = None,
) -> int:
    parser = argparse.ArgumentParser(description="PETER PAN E2E harness")
    parser.add_argument("--dry-run", action="store_true", help="Validate fixtures only, no HTTP")
    parser.add_argument(
        "--entrypoint",
        choices=["layer3", "n8n"],
        default="n8n",
        help="layer3: direct service calls; n8n: full orchestration via Ingestion + n8n",
    )
    parser.add_argument("--base-url", default="http://localhost", help="Compose host base URL")
    parser.add_argument(
        "--ingestion-url",
        default=None,
        help="Override Ingestion URL, for example http://ingestion:8000 inside Compose",
    )
    parser.add_argument(
        "--stubs-url",
        default=None,
        help="Override integration-stubs URL for an internal Compose runner",
    )
    parser.add_argument(
        "--tools-url",
        default=None,
        help="Override Tools API URL for P1 preview audit verification",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("PETER_SERVICES_TOKEN", ""),
        help="PETER_SERVICES_TOKEN if required; defaults to the environment",
    )
    parser.add_argument(
        "--poll-timeout",
        type=float,
        default=60.0,
        help="Seconds to poll integration-stubs for n8n delivery (n8n entrypoint only)",
    )
    args = parser.parse_args(argv)

    cases = _load_golden()
    _validate_cases(cases)
    if args.dry_run:
        print(f"golden_signals: {len(cases)} cases loaded from {GOLDEN_PATH.name}")
        return 0

    factory = _client_factory or httpx.Client
    with factory() as client:
        if args.entrypoint == "n8n":
            results = _run_n8n_entrypoint(
                cases,
                args.base_url,
                args.token,
                args.poll_timeout,
                client,
                ingestion_url=args.ingestion_url,
                stubs_base=args.stubs_url,
                tools_base=args.tools_url,
            )
        else:
            results = _run_layer3_entrypoint(cases, args.base_url, args.token, client)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / "e2e_latest.json"
    evidence = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "entrypoint": args.entrypoint,
        "git_sha": os.environ.get("GITHUB_SHA", ""),
        "golden_signals_sha256": hashlib.sha256(GOLDEN_PATH.read_bytes()).hexdigest(),
        "n8n_flow_sha256": hashlib.sha256(
            (ROOT / "n8n" / "peter-flow.json").read_bytes()
        ).hexdigest(),
        "layer3_source_sha256": _layer3_source_hash(),
        "results": results,
    }
    out.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    failed = [
        result
        for case, result in zip(cases, results, strict=True)
        if result.get("status") != case.get("expected_status", "ok")
    ]
    if failed:
        print(f"E2E failed: {len(failed)} case(s)")
        return 1
    print(f"E2E passed: {len(results)} case(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
