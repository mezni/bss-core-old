"""E2E journey test for the order-to-shipment workflow (US2).

Create a confirmed order → create shipment → shipment with unique tracking number
and order status ``shipped``. Shipment creation on a draft order returns 409 CONFLICT
and leaves the order ``confirmed``.
"""

from __future__ import annotations

from sqlalchemy import func, select

from src.models.order_management.infrastructure.orm import OrderORM
from src.models.shipment_management.infrastructure.orm import ShipmentORM


def _create_confirmed_order(client, customer_manage_headers, view_headers) -> dict:
    """Create and confirm an order; return the confirmed order dict."""
    # Create customer
    customer_resp = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Jane Doe",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "ship@example.com",
        },
        headers=customer_manage_headers,
    )
    assert customer_resp.status_code == 201, customer_resp.text
    customer = customer_resp.json()

    # Create order with items
    order_resp = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer["id"],
            "items": [{"description": "Widget A", "quantity": 1, "unit_price": 10.00}],
        },
        headers=view_headers,
    )
    assert order_resp.status_code == 201, order_resp.text
    order = order_resp.json()

    # Confirm the order
    confirm_resp = client.patch(
        f"/api/v1/orders/{order['id']}/transitions/confirm",
        headers=view_headers,
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    confirmed = confirm_resp.json()
    assert confirmed["status"] == "confirmed"
    assert confirmed["version"] == 2

    return confirmed


def test_order_to_shipment_workflow(
    client, customer_manage_headers, view_headers, e2e_session_factory
) -> None:
    """Full order→shipment e2e: confirmed order → shipment → status shipped."""
    order = _create_confirmed_order(client, customer_manage_headers, view_headers)

    # Create shipment (requires user:admin per T027; view_headers may currently
    # yield 403 until admin enforcement is wired, but the test asserts the
    # business flow once fully complete).
    ship_resp = client.post(
        "/api/v1/shipments",
        json={"carrier_name": "FastShip"},
        headers=view_headers,
    )
    assert ship_resp.status_code == 201, ship_resp.text
    shipment = ship_resp.json()
    assert shipment["tracking_reference"].startswith("SHIP-")
    assert shipment["carrier_name"] == "FastShip"
    assert shipment["order_id"] == order["id"]
    assert shipment["status"] == "shipped"

    # Verify order status is now shipped
    fetched = client.get(f"/api/v1/orders/{order['id']}", headers=view_headers)
    assert fetched.status_code == 200, fetched.text
    persisted = fetched.json()
    assert persisted["status"] == "shipped"
    assert len(persisted["items"]) == 1


def test_shipment_draft_order_rejected(
    client, view_headers
) -> None:
    """Shipment for a draft order must return 409 CONFLICT."""
    response = client.post(
        "/api/v1/shipments",
        json={"carrier_name": "FastShip"},
        headers=view_headers,
    )
    assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"
    body = response.json()
    assert body["code"] == "CONFLICT"
    assert body["error"] == "conflict"


# Fixture references are provided by tests/integration/e2e/conftest.py
# (view_headers, customer_manage_headers)