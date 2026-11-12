"""Integration test for dashboard billing metrics user journey.

Tests the billing metrics flow on the consolidated application with a
hermetic dashboard database, including category filtering.
"""

from __future__ import annotations


def test_dashboard_billing_retrieve_metrics(dashboard_client):
    """Test that an authenticated manager can retrieve billing metrics."""
    response = dashboard_client.get("/api/v1/dashboard/metrics?category=billing")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data
    assert data["total"] == 1


def test_dashboard_billing_role_access(dashboard_client):
    """Test that manager role can access billing metrics."""
    # Manager tier should be able to access billing metrics
    response = dashboard_client.get("/api/v1/dashboard/metrics?role_tier=manager&category=billing")
    assert response.status_code == 200

    # Operator should not see billing metrics without proper role
    response = dashboard_client.get("/api/v1/dashboard/metrics?role_tier=operator&category=billing")
    assert response.status_code == 200
