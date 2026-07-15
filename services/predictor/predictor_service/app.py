"""Predictor Service — anomaly-detection floor (BUILD_PLAN §3, Predictive
Engine row).

``POST /analyse`` combines the deterministic EWMA severity floor
(``ewma.py``, real) with a three-tier classifier and a typed six-class
``incident_class`` response. Tiers, in order:

1. explicit context markers (``classifier.match_context``) — deterministic
   evidence beats window inference;
2. the trained PyTorch checkpoint (``torch_classifier``, produced by
   ``train.py``) — softmax max below its confidence threshold keeps the argmax
   class but surfaces the ``uncertain`` fallback (the six-class enum is frozen;
   there is no seventh class);
3. the fixed-weight stub (``classifier.py``) when torch or the artifact is
   unavailable — the fixture-first demo path never depends on the model.

The routing layer maps the class to ``TriageReport.category`` deterministically;
severity always comes from the EWMA floor, never the model.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .auth import require_bearer_token
from .category import classification_context
from .classifier import match_context, predict as classify
from .ewma import score as ewma_score
from .fixtures import fixture_window
from .torch_classifier import load_classifier

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


def _run_classifier(window: list[float], context: str) -> dict[str, Any]:
    """Tiered classification: context markers -> trained model -> stub."""
    if match_context(context):
        return {**classify(window, context=context), "engine": "context"}
    torch_model = load_classifier()
    if torch_model is not None:
        return torch_model.predict(window)
    return {**classify(window, context=context), "engine": "stub"}


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
    classifier_result = _run_classifier(
        window,
        classification_context(payload.incident, payload.metric_window_ref),
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
    elif classifier_result.get("below_threshold"):
        # Locked decision: never a 7th class — surface uncertainty as a
        # fallback marker + sub-threshold confidence for the review branch.
        classifier_result = {**classifier_result, "fallback": "uncertain"}

    return AnalyseResponse(
        incident_class=incident_class,
        severity=ewma_result["severity"],
        confidence=confidence,
        method="ewma-floor",
        scores={"ewma": ewma_result, "classifier": classifier_result},
    )
