"""Contract test for dashboard billing metrics endpoint.

Tests that the dashboard billing metrics endpoint exists and responds correctly.
This test should FAIL before the dashboard API is implemented, then PASS after.
"""

from fastapi.testclient import TestClient


def test_dashboard_billing_endpoint_exists():
    """Test that the dashboard billing metrics endpoint exists and responds."""
    from src.presentation.api.dashboard_endpoints import app

    client = TestClient(app)
    response = client.get("/api/v1/dashboard/metrics?category=billing")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data


def test_dashboard_billing_response_format():
    """Test that dashboard billing metrics response has expected format."""
    from src.presentation.api.dashboard_endpoints import app

    client = TestClient(app)
    response = client.get("/api/v1/dashboard/metrics?category=billing")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "last_refreshed" in data
    assert "cache_ttl_seconds" in data

    if data["metrics"]:
        metric = data["metrics"][0]
        assert "metric_name" in metric
        assert "value" in metric
        assert "unit" in metric
        assert "aggregation_type" in metric
        assert "category" in metric
        assert metric["category"] == "billing"