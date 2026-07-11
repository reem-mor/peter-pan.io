"""Tools API — FastAPI app: owners, deploys, similar incidents, preview-only escalation."""

from __future__ import annotations

import hmac
import os
from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

from tools_api import escalation_service
from tools_api.contracts import TriageReport
from tools_api.data_access import load_service_owners
from tools_api.enrichment_tools import (
    correlate_deployments,
    find_similar_incidents,
    lookup_owner_and_escalation,
    score_business_impact,
)

app = FastAPI(title="Tools API", version="0.1.0")

_bearer_scheme = HTTPBearer(auto_error=False)


def require_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> None:
    """Require ``Authorization: Bearer <token>`` only when PETER_SERVICES_TOKEN is set."""
    expected = os.environ.get("PETER_SERVICES_TOKEN", "").strip()
    if not expected:
        return
    if credentials is None or not hmac.compare_digest(
        credentials.credentials, expected
    ):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class RecentDeploymentsRequest(BaseModel):
    service: str
    environment: str
    alert_time: str = Field(description="ISO-8601 timestamp")
    lookback_hours: int = 6


class ServiceContextRequest(BaseModel):
    service: str
    severity: str = ""
    environment: str = ""
    duration_minutes: int = 60


class SimilarIncidentsRequest(BaseModel):
    service: str
    symptom: str
    environment: str = ""
    limit: int = 5


class EscalationPreviewRequest(BaseModel):
    service: str
    severity: str = ""


class EscalationRequest(BaseModel):
    report: TriageReport
    preview: bool = True


class EscalationResponse(BaseModel):
    escalation_id: str
    preview: bool
    message: str
    escalation_path: list[str]
    service: str
    owner_team: str
    p_level: str
    war_room_required: bool
    compliance_overrides: list[dict[str, Any]]
    subject: str
    created_at: str


def _ok_or_404(result: dict[str, Any]) -> dict[str, Any]:
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "tools-api"}


@app.post("/tools/recent_deployments", dependencies=[Depends(require_bearer_token)])
def recent_deployments(payload: RecentDeploymentsRequest) -> dict[str, Any]:
    result = correlate_deployments(
        service=payload.service,
        environment=payload.environment,
        alert_time=payload.alert_time,
        lookback_hours=payload.lookback_hours,
    )
    return _ok_or_404(result)


@app.post("/tools/service_context", dependencies=[Depends(require_bearer_token)])
def service_context(payload: ServiceContextRequest) -> dict[str, Any]:
    owner = _ok_or_404(
        lookup_owner_and_escalation(
            service=payload.service,
            severity=payload.severity,
            environment=payload.environment,
        )
    )
    impact = score_business_impact(
        service=payload.service,
        environment=payload.environment,
        severity=payload.severity or "P3",
        duration_minutes=payload.duration_minutes,
    )
    if "error" not in impact:
        owner["business_impact"] = impact
    return owner


@app.post("/tools/similar_incidents", dependencies=[Depends(require_bearer_token)])
def similar_incidents(payload: SimilarIncidentsRequest) -> dict[str, Any]:
    result = find_similar_incidents(
        service=payload.service,
        symptom=payload.symptom,
        environment=payload.environment,
        limit=payload.limit,
    )
    return _ok_or_404(result)


@app.post("/tools/escalation_preview", dependencies=[Depends(require_bearer_token)])
def escalation_preview(payload: EscalationPreviewRequest) -> dict[str, Any]:
    owner = _ok_or_404(
        lookup_owner_and_escalation(
            service=payload.service,
            severity=payload.severity,
        )
    )
    return {
        "service": owner["service"],
        "severity": owner["severity"],
        "owner_team": owner["owner_team"],
        "escalation_path": owner["escalation_path"],
        "preview": True,
        "sends_notifications": False,
    }


@app.post(
    "/escalations",
    response_model=EscalationResponse,
    dependencies=[Depends(require_bearer_token)],
)
def post_escalation(payload: EscalationRequest) -> EscalationResponse:
    try:
        result = escalation_service.create_escalation(
            report=payload.report, preview=payload.preview
        )
    except escalation_service.EscalationServiceError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return EscalationResponse(**result)


@app.get("/teams", dependencies=[Depends(require_bearer_token)])
def teams() -> dict[str, list[str]]:
    """Known owning teams — lets Guardrails verify an owner_team without a service slug."""
    names = {
        (row.get("owning_team") or row.get("owner_team") or "").strip()
        for row in load_service_owners()
    }
    return {"teams": sorted(n for n in names if n)}


@app.get("/audit", dependencies=[Depends(require_bearer_token)])
def audit() -> list[dict[str, Any]]:
    return escalation_service.list_audit_entries(limit=50)
