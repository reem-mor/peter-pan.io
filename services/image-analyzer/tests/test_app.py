"""Test stubs for image analyzer."""

import pytest
from fastapi.testclient import TestClient

from image_analyzer_service.app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_healthz(client):
    """Health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["service"] == "image-analyzer"


def test_analyze_valid_image(client):
    """Analyze a synthetic image."""
    response = client.post(
        "/analyze",
        json={"image_url": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="},
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "classification" in data
    assert "condition_score" in data
