"""FastAPI app for the Image Analyzer microservice (Stage A: ResNet room classification + condition scoring).

Analyzes property images to classify room type (Residential vs. Commercial) and 
score room condition (1-5 scale). Parallel execution path in the n8n flow.
"""

from __future__ import annotations

import hmac
import os

from fastapi import Depends, FastAPI, Header, HTTPException

from image_analyzer_service.models import ImageAnalyzerModel
from image_analyzer_service.schemas import (
    AnalyzeImageRequest,
    AnalyzeImageResponse,
    RoomClassification,
)

SERVICE_NAME = "image-analyzer"

app = FastAPI(title="PETER PAN Image Analyzer Service")

# Singleton model instance
_model: ImageAnalyzerModel | None = None


def get_model() -> ImageAnalyzerModel:
    """Lazy-load model on first request."""
    global _model
    if _model is None:
        _model = ImageAnalyzerModel()
    return _model


async def require_bearer_token(
    authorization: str | None = Header(default=None),
) -> None:
    """Bearer-token auth dependency, enforced only when PETER_SERVICES_TOKEN is set."""
    expected = os.environ.get("PETER_SERVICES_TOKEN")
    if not expected:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing or invalid bearer token")
    provided = authorization.removeprefix("Bearer ").strip()
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=401, detail="missing or invalid bearer token")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": SERVICE_NAME}


@app.post("/analyze", response_model=AnalyzeImageResponse, dependencies=[Depends(require_bearer_token)])
async def analyze_image(
    request: AnalyzeImageRequest,
) -> AnalyzeImageResponse:
    """Analyze a property image for room type and condition."""
    model = get_model()
    result = model.analyze(request.image_url)

    return AnalyzeImageResponse(
        classification=RoomClassification(**result["classification"]),
        condition_score=result["condition_score"],
        analysis=result["analysis"],
    )
