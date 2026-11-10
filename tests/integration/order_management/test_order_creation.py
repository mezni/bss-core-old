"""Integration test for order creation - User Story 1."""

import json
import pytest
from fastapi.testclient import TestClient


def test_create_order_success():
    """Test creating an order with valid customer and item."""
    from src.api.health import app

    client = TestClient(app)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": "1",
            "items": [
                {
                    "description": "Widget A",
                    "quantity": 2,
                    "unit_price": 10.50,
                }
            ],
        },
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = json.loads(response.text)
    assert data["status"] == "draft", f"Expected draft status, got {data['status']}"
    assert data["subtotal"] == 21.0, f"Expected subtotal 21.0, got {data['subtotal']}"
    assert data["tax_amount"] == 2.1, f"Expected tax_amount 2.1, got {data['tax_amount']}"  # 10% fixed rate
    assert data["total"] == 23.1, f"Expected total 23.1, got {data['total']}"  # subtotal + tax
    assert len(data["items"]) == 1
    assert data["items"][0]["line_total"] == 21.0


def test_create_order_no_items():
    """Test creating an order without items returns 422."""
    from src.api.health import app

    client = TestClient(app)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": "1",
            "items": [],
        },
    )

    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"


def test_create_order_with_valid_customer():
    """Test creating an order with a valid customer."""
    from src.api.health import app

    client = TestClient(app)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": "1",
            "items": [
                {
                    "description": "Widget A",
                    "quantity": 1,
                    "unit_price": 5.00,
                }
            ],
        },
    )

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

    data = json.loads(response.text)
    assert data["status"] == "draft"
    assert data["subtotal"] == 5.0
    assert data["tax_amount"] == 0.5  # 10% of 5.0
    assert data["total"] == 5.5  # subtotal + tax
    assert len(data["items"]) == 1