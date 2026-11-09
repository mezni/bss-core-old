"""Contract test for backend health check endpoint.

Tests that the FastAPI backend health check endpoint exists and responds correctly.
This test should FAIL before the backend is implemented (T012), then PASS after.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_check_endpoint_exists():
    """Test that the health check endpoint exists and responds."""
    from src.api.health import app as fastapi_app

    client = TestClient(fastapi_app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok" or data.get("status") == "healthy"


def test_health_check_response_format():
    """Test that health check response has expected format."""
    from src.api.health import app as fastapi_app

    client = TestClient(fastapi_app)
    response = client.get("/health")

    assert response.status_code == 200
    assert "status" in response.json()
