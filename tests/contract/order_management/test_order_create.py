"""Contract test for POST /api/v1/orders - Create Order."""

import json
from fastapi.testclient import TestClient

from src.api.health import app


def test_create_order_contract():
    """Test POST /api/v1/orders request/response schema."""
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
    assert "id" in data, "Response must include order id"
    assert "status" in data, "Response must include status"
    assert "subtotal" in data, "Response must include subtotal"
    assert "tax_amount" in data, "Response must include tax_amount"
    assert "total" in data, "Response must include total"
    assert "customer_id" in data, "Response must include customer_id"
    assert "created_at" in data, "Response must include created_at"
    assert "updated_at" in data, "Response must include updated_at"
    assert "items" in data, "Response must include items"

    # Validate status
    assert data["status"] == "draft", f"Expected draft status, got {data['status']}"

    # Validate subtotal: 2 × 10.50 = 21.0
    assert data["subtotal"] == 21.0, f"Expected subtotal 21.0, got {data['subtotal']}"

    # Validate tax (10% fixed rate for S03 MVP): 21.0 × 0.10 = 2.1
    assert data["tax_amount"] == 2.1, f"Expected tax_amount 2.1, got {data['tax_amount']}"

    # Validate total: subtotal + tax = 21.0 + 2.1 = 23.1
    assert data["total"] == 23.1, f"Expected total 23.1, got {data['total']}"

    # Validate items
    assert len(data["items"]) == 1, "Expected 1 item"
    item = data["items"][0]
    assert item["description"] == "Widget A"
    assert item["quantity"] == 2
    assert item["unit_price"] == 10.50
    assert item["line_total"] == 21.0, f"Expected line_total 21.0, got {item['line_total']}"


def test_create_order_no_items_contract():
    """Test POST /api/v1/orders with no items returns 422 (validation error)."""
    client = TestClient(app)

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": "1",
            "items": [],
        },
    )

    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"


def test_create_order_missing_customer_contract():
    """Test POST /api/v1/orders without customer_id returns 422 (validation error)."""
    client = TestClient(app)

    response = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {
                    "description": "Widget A",
                    "quantity": 1,
                    "unit_price": 10.00,
                }
            ],
        },
    )

    assert response.status_code == 422, f"Expected 422, got {response.status_code}: {response.text}"