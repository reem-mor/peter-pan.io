"""Simple room classification model (Stage A fixture)."""

import io
import base64
from typing import Optional

from PIL import Image


class ImageAnalyzerModel:
    """Mock room classification model for Stage A."""

    def __init__(self):
        self.room_types = ["Residential", "Commercial"]

    def load_image_from_url(self, image_url: str) -> Optional[Image.Image]:
        """Load image from URL or base64 data URI."""
        try:
            if image_url.startswith("data:"):
                # Base64 data URI
                header, encoded = image_url.split(",", 1)
                img_bytes = base64.b64decode(encoded)
                return Image.open(io.BytesIO(img_bytes)).convert("RGB")
            else:
                # URL — stub: always return a synthetic image in Stage A
                return Image.new("RGB", (224, 224), color=(73, 109, 137))
        except Exception:
            return None

    def analyze(self, image_url: str) -> dict:
        """Analyze image and return room type + condition score (fixture)."""
        image = self.load_image_from_url(image_url)
        if not image:
            return {
                "classification": {
                    "room_type": "Unknown",
                    "confidence": 0.0,
                },
                "condition_score": 3,
                "analysis": "Could not load image.",
            }

        # Stage A fixture: deterministic output based on image size
        room_idx = 0 if image.width < 300 else 1
        condition_score = ((image.width + image.height) % 5) + 1
        room_confidence = 0.75 + (0.2 if room_idx == 0 else 0.15)

        return {
            "classification": {
                "room_type": self.room_types[room_idx],
                "confidence": round(room_confidence, 3),
            },
            "condition_score": condition_score,
            "analysis": f"Classified as {self.room_types[room_idx]} property (confidence: {room_confidence:.1%}). Condition score: {condition_score}/5.",
        }
