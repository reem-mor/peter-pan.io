"""FastAPI app for the Guardrails microservice (BUILD_PLAN §3, GRD row).

Two endpoints, matching the n8n flow's HTTP nodes (``n8n/peter-flow.json``):
``POST /check/input`` (body ``{"signal": <Signal dict>}``) and
``POST /check/output`` (body ``{"report": <TriageReport dict>}``). Both return
``{"pass": bool, "flags": [str], "reason": str}``. Any non-empty flag list means
``pass=false``.
"""

from __future__ import annotations

import hmac
import os
from collections.abc import AsyncIterator
from typing import Any

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from . import rules
from .contracts import Signal, TriageReport
from .owner_check import verify_owner_team
from .policy_engine import NoopPolicyEngine, PolicyEngine

app = FastAPI(title="PETER PAN Guardrails", version="0.1.0")

_policy_engine: PolicyEngine = NoopPolicyEngine()


async def require_auth(authorization: str | None = Header(default=None)) -> None:
    """Bearer-token auth gate — only enforced when PETER_SERVICES_TOKEN is set."""
    expected = os.environ.get("PETER_SERVICES_TOKEN")
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    provided = authorization.removeprefix("Bearer ").strip()
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="Invalid bearer token")


def _build_http_client() -> httpx.AsyncClient:
    headers: dict[str, str] = {}
    token = os.environ.get("PETER_SERVICES_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return httpx.AsyncClient(headers=headers)


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    """Yield the shared outbound httpx client — overridden in tests with a
    MockTransport-backed client so no real network call is ever made."""
    async with _build_http_client() as client:
        yield client


class GuardrailResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    passed: bool = Field(alias="pass")
    flags: list[str] = Field(default_factory=list)
    reason: str = ""


class CheckInputRequest(BaseModel):
    signal: dict[str, Any]


class CheckOutputRequest(BaseModel):
    report: dict[str, Any]
    service: str | None = None
    environment: str | None = "production"


def _validation_reason(exc: ValidationError, label: str) -> str:
    first = exc.errors()[0]
    loc = ".".join(str(part) for part in first["loc"]) or label
    return f"{label} failed schema validation at '{loc}': {first['msg']}"


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/check/input", response_model=GuardrailResponse, response_model_by_alias=True
)
async def check_input(
    payload: CheckInputRequest,
    _auth: None = Depends(require_auth),
) -> GuardrailResponse:
    try:
        signal = Signal.model_validate(payload.signal)
    except ValidationError as exc:
        return GuardrailResponse(
            passed=False,
            flags=["schema_invalid"],
            reason=_validation_reason(exc, "signal"),
        )

    flags: list[str] = []
    reasons: list[str] = []

    if not signal.title.strip():
        flags.append("empty_title")
        reasons.append("Signal title is empty or whitespace-only.")

    for match in rules.scan_text(f"{signal.title}\n{signal.body}"):
        flags.append(match.code)
        reasons.append(match.reason)

    flags.extend(_policy_engine.check_input(signal))

    passed = not flags
    reason = " ".join(reasons) if reasons else "Signal passed all guardrail checks."
    return GuardrailResponse(passed=passed, flags=flags, reason=reason)


@app.post(
    "/check/output", response_model=GuardrailResponse, response_model_by_alias=True
)
async def check_output(
    payload: CheckOutputRequest,
    _auth: None = Depends(require_auth),
    http_client: httpx.AsyncClient = Depends(get_http_client),
) -> GuardrailResponse:
    try:
        report = TriageReport.model_validate(payload.report)
    except ValidationError as exc:
        return GuardrailResponse(
            passed=False,
            flags=["schema_invalid"],
            reason=_validation_reason(exc, "report"),
        )

    flags: list[str] = []
    reasons: list[str] = []

    # citations non-empty is already schema-enforced (min_length=1); this also
    # catches the practically reachable case of citations present but carrying
    # no evidentiary quote text (a report that "cites" nothing in substance) —
    # a known redundancy with the frozen contract, kept as a defense-in-depth floor.
    if not report.citations or not any(c.quote.strip() for c in report.citations):
        flags.append("uncited")
        reasons.append(
            "TriageReport has no citations with evidentiary quotes — uncited claims "
            "are not allowed."
        )

    destructive = rules.find_destructive_steps(report.recommended_steps)
    if destructive:
        flags.append("destructive_step")
        reasons.append(
            "recommended_steps contains a disallowed destructive command: "
            + "; ".join(destructive)
        )

    if not (0.0 <= report.confidence <= 1.0):
        flags.append("confidence_out_of_range")
        reasons.append("confidence must be between 0.0 and 1.0.")

    verified = await verify_owner_team(
        report.owner_team,
        service=payload.service,
        environment=payload.environment,
        client=http_client,
    )
    if not verified:
        flags.append("owner_unverified")
        reasons.append(
            f"owner_team '{report.owner_team}' could not be verified against the Tools "
            "API (fail-closed: unverifiable owners are never treated as valid)."
        )

    flags.extend(_policy_engine.check_output(report))

    passed = not flags
    reason = (
        " ".join(reasons) if reasons else "TriageReport passed all guardrail checks."
    )
    return GuardrailResponse(passed=passed, flags=flags, reason=reason)
