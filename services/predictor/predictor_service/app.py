"""Predictor Service — anomaly-detection floor (BUILD_PLAN §3, Predictive
Engine row).

``POST /analyse`` combines the deterministic EWMA severity floor
(``ewma.py``, real) with a fixed-weight classifier stub (``classifier.py``,
Stage-A fixture — real training is out of scope, BUILD_PLAN §6) and a
typed six-class ``incident_class`` response. The routing layer maps that class
to ``TriageReport.category`` deterministically. No ML frameworks; everything
here is unit-tested arithmetic per the deterministic-floor principle.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .auth import require_bearer_token
from .category import classification_context
from .classifier import predict as classify
from .ewma import score as ewma_score
from .fixtures import fixture_window

SERVICE_NAME = "predictor"
INCIDENT_CLASSES = frozenset(
    {
        "cpu_saturation",
        "memory_leak",
        "db_lock_contention",
        "replication_lag",
        "error_rate_spike",
        "normal",
    }
)
UNKNOWN_CLASS_CONFIDENCE = 0.2

app = FastAPI(title="PETER PAN Predictor Service")


class AnalyseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    incident: dict | None = None
    metric_window_ref: str | None = None
    window: list[float] | None = None


class AnalyseResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    incident_class: Literal[
        "cpu_saturation",
        "memory_leak",
        "db_lock_contention",
        "replication_lag",
        "error_rate_spike",
        "normal",
    ]
    severity: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0.0, le=1.0)
    method: Literal["ewma-floor"]
    scores: dict[str, Any]


@app.exception_handler(RequestValidationError)
async def request_validation_error(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Return JSON-safe validation errors even when the rejected input is NaN/Inf."""
    detail = [
        {
            key: value
            for key, value in error.items()
            if key not in {"input", "ctx", "url"}
        }
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": detail})


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "service": SERVICE_NAME}


@app.post(
    "/analyse",
    response_model=AnalyseResponse,
    dependencies=[Depends(require_bearer_token)],
)
async def analyse(payload: AnalyseRequest) -> AnalyseResponse:
    window = (
        payload.window if payload.window else fixture_window(payload.metric_window_ref)
    )

    ewma_result = ewma_score(window)
    classifier_result = classify(
        window,
        context=classification_context(payload.incident, payload.metric_window_ref),
    )
    incident_class = classifier_result.get("incident_class")
    confidence = classifier_result.get("confidence", 0.0)
    if incident_class not in INCIDENT_CLASSES:
        incident_class = "normal"
        confidence = min(float(confidence), UNKNOWN_CLASS_CONFIDENCE)
        classifier_result = {
            **classifier_result,
            "incident_class": incident_class,
            "confidence": confidence,
            "fallback": "unknown_class",
        }
    elif incident_class == "normal" and ewma_result["severity"] > 1:
        confidence = min(float(confidence), UNKNOWN_CLASS_CONFIDENCE)
        classifier_result = {
            **classifier_result,
            "confidence": confidence,
            "fallback": "severity_conflict",
        }

    return AnalyseResponse(
        incident_class=incident_class,
        severity=ewma_result["severity"],
        confidence=confidence,
        method="ewma-floor",
        scores={"ewma": ewma_result, "classifier": classifier_result},
    )
