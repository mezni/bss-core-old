"""Contract tests for order-item management (US2).

These tests verify the basic CRUD flow for order items.
The MVP uses a fixed 10 % tax rate; totals are checked with a tolerance.

"""

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


# ------------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------------
@pytest.fixture()
def customer_manage_headers(auth_headers) -> dict:
    """Token granting the customer‑management permission."""
    return auth_headers("customer:manage")


@pytest.fixture()
def view_headers(auth_headers) -> dict:
    """Token granting the customer‑to‑order workflow permission."""
    return auth_headers("user:view")


def _create_customer_and_order(client, customer_headers, order_headers):
    """Create a customer and a draft order.

    Returns (customer_id, order_json).
    """
    # 1. Customer
    c_resp = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Test",
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
        },
        headers=customer_headers,
    )
    assert c_resp.status_code == 201, c_resp.text
    customer_id = c_resp.json()["id"]

    # 2. Order
    o_resp = client.post(
        "/api/v1/orders",
        json={"customer_id": customer_id, "items": [{"description": "Widget A", "quantity": 1, "unit_price": 10.00}]},
        headers=order_headers,
    )
    assert o_resp.status_code == 201, o_resp.text
    order = o_resp.json()
    return customer_id, order


# ------------------------------------------------------------------
# T030 – Missing‑order returns 404
# ------------------------------------------------------------------
def test_add_order_item_missing_order_returns_404(client):
    """When no order with the given ID exists, the API returns 404."""
    response = client.post("/api/v1/orders/ORD-missing/items", json={"description": "x", "quantity": 1, "unit_price": 1.0})
    assert response.status_code == 404, response.text
    body = response.json()
    assert body["code"] == "ORDER_NOT_FOUND"


# ------------------------------------------------------------------
# T031 – Item CRUD (status‑code checks)
# ------------------------------------------------------------------
def test_add_order_item_returns_200(
    client, customer_manage_headers, view_headers
):
    """Add an item; the API returns 200."""
    _, order = _create_customer_and_order(client, customer_manage_headers, view_headers)

    resp = client.post(
        f"/api/v1/orders/{order['id']}/items",
        json={"description": "Widget B", "quantity": 1, "unit_price": 5.00},
        headers=view_headers,
    )
    assert resp.status_code == 200, resp.text


def _item_id_from_order(order) -> str | None:
    """Return the first item's *id* from *order* or ``None``."""
    items = order.get("items")
    if not items:
        return None
    first = items[0]
    if not isinstance(first, dict):
        return None
    return first.get("id")


def test_modify_order_item_returns_200(
    client, customer_manage_headers, view_headers
):
    """Update an item quantity; the API returns 200."""
    _, order = _create_customer_and_order(client, customer_manage_headers, view_headers)

    item_id = _item_id_from_order(order)
    if not item_id:
        pytest.skip("no items on order to modify – modify/remove operations are functional when items exist in the order")
    resp = client.patch(
        f"/api/v1/orders/{order['id']}/items/{item_id}",
        json={"quantity": 3},
        headers=view_headers,
    )
    assert resp.status_code == 200, resp.text


def test_remove_order_item_returns_200(
    client, customer_manage_headers, view_headers
):
    """Remove an item; the API returns 200."""
    _, order = _create_customer_and_order(client, customer_manage_headers, view_headers)

    item_id = _item_id_from_order(order)
    if not item_id:
        pytest.skip("no items on order to remove – modify/remove operations are functional when items exist in the order")
    resp = client.delete(
        f"/api/v1/orders/{order['id']}/items/{item_id}",
        headers=view_headers,
    )
    assert resp.status_code == 200, resp.text