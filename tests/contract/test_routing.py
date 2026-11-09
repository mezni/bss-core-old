"""Contract test for API routing structure.

Tests that the FastAPI application has the expected routing structure
and that routes can be added without crossing layer boundaries.
"""

import pytest


def test_health_route_exists():
    """Test that the health check route is registered."""
    from fastapi.testclient import TestClient

    from src.api.health import app as fastapi_app

    client = TestClient(fastapi_app)
    response = client.get("/health")

    assert response.status_code == 200


def test_app_has_routes():
    """Test that the FastAPI application has routes registered."""
    from src.api.health import app as fastapi_app

    routes = [route.path for route in fastapi_app.routes]
    assert len(routes) > 0, "No routes registered on the FastAPI application"
    assert "/health" in routes, "Health check route not found"


def test_routes_follow_pattern():
    """Test that routes follow the expected pattern."""
    from src.api.health import app as fastapi_app

    route_paths = [route.path for route in fastapi_app.routes]
    # Health check should be a GET route
    health_routes = [r for r in route_paths if "/health" in r]
    assert len(health_routes) > 0, "No health check routes found"
