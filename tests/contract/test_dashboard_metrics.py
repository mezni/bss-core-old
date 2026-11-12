"""Contract test for dashboard metrics endpoint.

Verifies the dashboard metrics contract against the consolidated
application mounted with a hermetic dashboard database.
"""

from __future__ import annotations


def test_dashboard_metrics_endpoint_exists(dashboard_client):
    """Test that the dashboard metrics endpoint exists and responds."""
    response = dashboard_client.get("/api/v1/dashboard/metrics")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_dashboard_metrics_response_format(dashboard_client):
    """Test that dashboard metrics response has expected format."""
    response = dashboard_client.get("/api/v1/dashboard/metrics")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "last_refreshed" in data
    assert "cache_ttl_seconds" in data

    assert data["total"] >= 1
    metric = data["metrics"][0]
    assert "metric_name" in metric
    assert "value" in metric
    assert "unit" in metric
    assert "aggregation_type" in metric
    assert "category" in metric
