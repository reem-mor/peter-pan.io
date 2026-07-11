"""Pydantic models for image analyzer API contracts."""

from pydantic import BaseModel, Field


class AnalyzeImageRequest(BaseModel):
    """Request to analyze an image (base64-encoded or URL)."""
    image_url: str = Field(..., description="URL or base64 data:// URI of the image")
    

class RoomClassification(BaseModel):
    """Room type classification with confidence score."""
    room_type: str = Field(..., description="Residential or Commercial")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")


class AnalyzeImageResponse(BaseModel):
    """Response from image analysis."""
    classification: RoomClassification
    condition_score: int = Field(..., ge=1, le=5, description="Room condition score (1-5)")
    analysis: str = Field(default="", description="Human-readable analysis")
    citations: list[dict] = Field(default_factory=list, description="Analysis citations")
