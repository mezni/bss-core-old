"""Contract test for dashboard billing metrics endpoint.

Verifies the billing-category metrics contract against the consolidated
application mounted with a hermetic dashboard database.
"""

from __future__ import annotations


def test_dashboard_billing_endpoint_exists(dashboard_client):
    """Test that the dashboard billing metrics endpoint exists and responds."""
    response = dashboard_client.get("/api/v1/dashboard/metrics?category=billing")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data


def test_dashboard_billing_response_format(dashboard_client):
    """Test that dashboard billing metrics response has expected format."""
    response = dashboard_client.get("/api/v1/dashboard/metrics?category=billing")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "last_refreshed" in data
    assert "cache_ttl_seconds" in data

    assert data["total"] == 1
    metric = data["metrics"][0]
    assert "metric_name" in metric
    assert "value" in metric
    assert "unit" in metric
    assert "aggregation_type" in metric
    assert "category" in metric
    assert metric["category"] == "billing"
