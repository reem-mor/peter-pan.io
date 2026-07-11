"""Predictor Service — anomaly-detection floor (BUILD_PLAN §3, Predictive
Engine row).

``POST /analyse`` combines the deterministic EWMA severity floor
(``ewma.py``, real) with a fixed-weight classifier stub (``classifier.py``,
Stage-A fixture — real training is out of scope, BUILD_PLAN §6) and a
deterministic service-name -> category mapping (``category.py``). No ML
frameworks; everything here is unit-tested arithmetic per the deterministic-
floor engineering principle.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from .auth import require_bearer_token
from .category import categorize_service, resolve_service_name
from .classifier import predict as classify
from .ewma import score as ewma_score
from .fixtures import fixture_window

SERVICE_NAME = "predictor"

app = FastAPI(title="PETER PAN Predictor Service")


class AnalyseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    incident: dict | None = None
    metric_window_ref: str | None = None
    window: list[float] | None = None


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


@app.post("/analyse", dependencies=[Depends(require_bearer_token)])
async def analyse(payload: AnalyseRequest) -> dict:
    window = (
        payload.window if payload.window else fixture_window(payload.metric_window_ref)
    )

    ewma_result = ewma_score(window)
    classifier_result = classify(window)
    service_name = resolve_service_name(payload.incident, payload.metric_window_ref)
    category = categorize_service(service_name)

    return {
        "category": category,
        "severity": ewma_result["severity"],
        "confidence": classifier_result["confidence"],
        "method": "ewma-floor",
        "scores": {"ewma": ewma_result, "classifier": classifier_result},
    }
