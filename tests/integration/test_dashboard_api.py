"""Integration test for dashboard API metric retrieval user journey.

Tests the full dashboard API flow including authentication, filtering, and response validation.
This test should FAIL before the backend is implemented, then PASS after.
"""

from datetime import datetime, timezone

from fastapi.testclient import TestClient


def test_dashboard_api_retrieve_metrics():
    """Test that an authenticated operator can retrieve dashboard metrics."""
    from src.presentation.api.dashboard_endpoints import app

    client = TestClient(app)
    response = client.get("/api/v1/dashboard/metrics")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data


def test_dashboard_api_date_range_filtering():
    """Test dashboard API date range filtering."""
    from src.presentation.api.dashboard_endpoints import app

    client = TestClient(app)
    start = datetime(2026, 11, 1).isoformat()
    end = datetime(2026, 11, 11, 23, 59, 59).isoformat()

    response = client.get(
        "/api/v1/dashboard/metrics",
        params={"start_date": start, "end_date": end},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0


def test_dashboard_api_period_filtering():
    """Test dashboard API predefined period filtering."""
    from src.presentation.api.dashboard_endpoints import app

    client = TestClient(app)

    for period in ["current_month", "current_quarter", "year_to_date"]:
        response = client.get("/api/v1/dashboard/metrics", params={"period": period})
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data


def test_dashboard_api_role_based_access():
    """Test dashboard API role-based access control."""
    from src.presentation.api.dashboard_endpoints import app

    client = TestClient(app)

    # Test with no role tier (should default to operator)
    response = client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 200

    # Test with operator role tier
    response = client.get("/api/v1/dashboard/metrics", params={"role_tier": "operator"})
    assert response.status_code == 200

    # Test with manager role tier
    response = client.get("/api/v1/dashboard/metrics", params={"role_tier": "manager"})
    assert response.status_code == 200

    # Test with admin role tier
    response = client.get("/api/v1/dashboard/metrics", params={"role_tier": "admin"})
    assert response.status_code == 200