"""Contract tests for order-item management (US2)."""

from __future__ import annotations

import pytest

from src.models.order_management.domain.entities import Order, OrderItem
from src.models.order_management.domain.value_objects import OrderStatus


ORDER_PAYLOAD = {
    "customer_id": "C-1",
    "items": [{"description": "Widget A", "quantity": 1, "unit_price": 10.00}],
}


def _assert_envelope(body: dict) -> None:
    assert set(body) == {"error", "message", "code"}
    assert body["error"] == body["code"].lower()
    assert isinstance(body["message"], str) and body["message"]


def _create_customer_and_order(client, headers) -> tuple:
    """Helper: create a customer and a draft order, return (customer, order)."""
    customer_resp = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Test",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        },
        headers=headers,
    )
    assert customer_resp.status_code == 201, customer_resp.text
    customer_id = customer_resp.json()["id"]

    order_resp = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"description": "Widget A", "quantity": 1, "unit_price": 10.00}],
        },
        headers=headers,
    )
    assert order_resp.status_code == 201, order_resp.text
    order = order_resp.json()
    return customer_id, order


# ------------------------------------------------------------------
# T030 – Contract test: unauthenticated item add must return 401
# ------------------------------------------------------------------
def test_add_order_item_requires_authentication(client) -> None:
    response = client.post("/api/v1/orders/ORD-missing/items", json={"description": "x", "quantity": 1, "unit_price": 1.0})

    assert response.status_code == 401
    _assert_envelope(response.json())
    assert response.json()["code"] == "UNAUTHENTICATED"


# ------------------------------------------------------------------
# T031 – Integration tests for item modify/remove and total recalc
# ------------------------------------------------------------------
def _create_order_with_items(client, view_headers) -> dict:
    """Create a customer and a draft order using view_headers."""
    _, order = _create_customer_and_order(client, view_headers)
    return order


def test_add_order_item_success(
    client, view_headers
) -> None:
    """Add an item to a draft order; verify total recalculation."""
    order = _create_order_with_items(client, view_headers)

    resp = client.post(
        f"/api/v1/orders/{order['id']}/items",
        json={"description": "Widget B", "quantity": 1, "unit_price": 5.00},
        headers=view_headers,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["items"][1]["description"] == "Widget B"
    assert body["items"][1]["quantity"] == 1
    assert body["items"][1]["unit_price"] == "5.00"
    assert body["total"] == "15.00"


def test_modify_order_item_quantity(
    client, view_headers
) -> None:
    """Update an item quantity and verify total recalc."""
    order = _create_order_with_items(client, view_headers)

    assert order["total"] == "10.00"

    resp = client.patch(
        f"/api/v1/orders/{order['id']}/items/{order['items'][0]['item_id']}",
        json={"quantity": 3},
        headers=view_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["items"][0]["quantity"] == 3
    assert body["total"] == "30.00"


def test_remove_order_item(
    client, view_headers
) -> None:
    """Remove an item and verify total becomes 0."""
    order = _create_order_with_items(client, view_headers)

    item_id = order["items"][0]["item_id"]
    resp = client.delete(
        f"/api/v1/orders/{order['id']}/items/{item_id}",
        headers=view_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["items"]) == 0
    assert body["total"] == "0.00"


def test_item_lifecycle_total_recalc(
    client, view_headers
) -> None:
    """Full add → modify → remove lifecycle, verify total at each step."""
    order = _create_order_with_items(client, view_headers)

    # Add a second item
    client.post(
        f"/api/v1/orders/{order['id']}/items",
        json={"description": "Widget B", "quantity": 1, "unit_price": 5.00},
        headers=view_headers,
    )
    assert len(order["items"]) == 2
    assert order["total"] == "15.00"

    # Modify first item quantity to 2
    item_id = order["items"][0]["item_id"]
    client.patch(
        f"/api/v1/orders/{order['id']}/items/{item_id}",
        json={"quantity": 2},
        headers=view_headers,
    )
    assert order["items"][0]["quantity"] == 2
    assert order["total"] == "25.00"

    # Remove the second item
    client.delete(
        f"/api/v1/orders/{order['id']}/items/{order['items'][1]['item_id']}",
        headers=view_headers,
    )
    assert len(order["items"]) == 1
    assert order["total"] == "20.00"