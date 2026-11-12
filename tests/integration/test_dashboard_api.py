"""Integration test for dashboard API metric retrieval user journey.

Tests the full dashboard API flow on the consolidated application with a
hermetic dashboard database, including filtering and response validation.
"""

from __future__ import annotations

from datetime import datetime


def test_dashboard_api_retrieve_metrics(dashboard_client):
    """Test that an authenticated operator can retrieve dashboard metrics."""
    response = dashboard_client.get("/api/v1/dashboard/metrics")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data
    assert data["total"] >= 1


def test_dashboard_api_date_range_filtering(dashboard_client):
    """Test dashboard API date range filtering."""
    start = datetime(2020, 1, 1).isoformat()
    end = datetime(2030, 12, 31, 23, 59, 59).isoformat()

    response = dashboard_client.get(
        "/api/v1/dashboard/metrics",
        params={"start_date": start, "end_date": end},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 0


def test_dashboard_api_period_filtering(dashboard_client):
    """Test dashboard API predefined period filtering."""
    for period in ["current_month", "current_quarter", "year_to_date"]:
        response = dashboard_client.get("/api/v1/dashboard/metrics", params={"period": period})
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data


def test_dashboard_api_role_based_access(dashboard_client):
    """Test dashboard API role-based access control."""
    # Test with no role tier (should default to operator)
    response = dashboard_client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 200

    # Test with operator role tier
    response = dashboard_client.get("/api/v1/dashboard/metrics", params={"role_tier": "operator"})
    assert response.status_code == 200

    # Test with manager role tier
    response = dashboard_client.get("/api/v1/dashboard/metrics", params={"role_tier": "manager"})
    assert response.status_code == 200

    # Test with admin role tier
    response = dashboard_client.get("/api/v1/dashboard/metrics", params={"role_tier": "admin"})
    assert response.status_code == 200
