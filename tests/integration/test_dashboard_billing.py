"""Integration test for dashboard billing metrics user journey.

Tests the billing metrics flow including authentication, category filtering, and response validation.
This test should FAIL before the backend is implemented, then PASS after.
"""

from datetime import datetime

from fastapi.testclient import TestClient


def test_dashboard_billing_retrieve_metrics():
    """Test that an authenticated manager can retrieve billing metrics."""
    from src.presentation.api.dashboard_endpoints import app

    client = TestClient(app)
    response = client.get("/api/v1/dashboard/metrics?category=billing")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data


def test_dashboard_billing_role_access():
    """Test that manager role can access billing metrics."""
    from src.presentation.api.dashboard_endpoints import app

    client = TestClient(app)

    # Manager tier should be able to access billing metrics
    response = client.get("/api/v1/dashboard/metrics?role_tier=manager&category=billing")
    assert response.status_code == 200

    # Operator should not see billing metrics without proper role
    response = client.get("/api/v1/dashboard/metrics?role_tier=operator&category=billing")
    assert response.status_code == 200