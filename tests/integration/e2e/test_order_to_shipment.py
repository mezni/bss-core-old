"""E2E journey test for the order-to-shipment workflow (US2).

Create a confirmed order → create shipment → shipment with unique tracking number
and order status ``shipped``. Shipment creation on a draft order returns 409 CONFLICT
and leaves the order unchanged. Failure in the shipment branch leaves the order
``confirmed``.
"""

from __future__ import annotations

from sqlalchemy import func, select

from src.models.shipment_management.infrastructure.orm import ShipmentORM


def _create_customer(client, customer_manage_headers) -> dict:
    """Create a customer and return it."""
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
    return customer_resp.json()


def _create_draft_order(client, customer_id, headers) -> dict:
    """Create a draft order with a single item."""
    order_resp = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"description": "Widget A", "quantity": 1, "unit_price": 10.00}],
        },
        headers=headers,
    )
    assert order_resp.status_code == 201, order_resp.text
    return order_resp.json()


def _create_confirmed_order(client, customer_manage_headers, view_headers) -> dict:
    """Create and confirm an order; return the confirmed order dict."""
    customer = _create_customer(client, customer_manage_headers)
    order = _create_draft_order(client, customer["id"], view_headers)

    confirm_resp = client.patch(
        f"/api/v1/orders/{order['id']}/transitions/confirm",
        headers=view_headers,
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    confirmed = confirm_resp.json()
    assert confirmed["status"] == "confirmed"
    assert confirmed["version"] == 2
    return confirmed


def _shipment_count(session_factory) -> int:
    """Count shipment rows in the test database."""
    with session_factory() as session:
        return session.scalar(select(func.count()).select_from(ShipmentORM)) or 0


def test_order_to_shipment_workflow(
    client, customer_manage_headers, view_headers, admin_headers, e2e_session_factory
) -> None:
    """Full order→shipment e2e: confirmed order → shipment → status shipped."""
    order = _create_confirmed_order(client, customer_manage_headers, view_headers)

    ship_resp = client.post(
        "/api/v1/shipments",
        json={"order_id": order["id"], "carrier_name": "FastShip"},
        headers=admin_headers,
    )
    assert ship_resp.status_code == 201, ship_resp.text
    shipment = ship_resp.json()
    assert shipment["tracking_reference"].startswith("SHIP-")
    assert shipment["carrier_name"] == "FastShip"
    assert shipment["order_id"] == order["id"]
    assert shipment["status"] == "pending"

    # Verify order status is now shipped
    fetched = client.get(f"/api/v1/orders/{order['id']}", headers=view_headers)
    assert fetched.status_code == 200, fetched.text
    persisted = fetched.json()
    assert persisted["status"] == "shipped"
    assert len(persisted["items"]) == 1

    assert _shipment_count(e2e_session_factory) == 1


def test_shipment_draft_order_rejected(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    """Shipment for a draft order must return 409 CONFLICT."""
    customer = _create_customer(client, customer_manage_headers)
    draft_order = _create_draft_order(client, customer["id"], view_headers)
    assert draft_order["status"] == "draft"

    ship_resp = client.post(
        "/api/v1/shipments",
        json={"order_id": draft_order["id"], "carrier_name": "FastShip"},
        headers=admin_headers,
    )
    assert ship_resp.status_code == 409, ship_resp.text
    body = ship_resp.json()
    assert body["code"] == "ORDER_NOT_CONFIRMED"
    assert body["error"] == "order_not_confirmed"


def test_shipment_failure_preserves_order(
    client,
    customer_manage_headers,
    view_headers,
    admin_headers,
    e2e_session_factory,
) -> None:
    """A shipment creation failure leaves the order ``confirmed`` (T028)."""
    order = _create_confirmed_order(client, customer_manage_headers, view_headers)
    before = _shipment_count(e2e_session_factory)

    # A blank carrier name passes schema validation but fails domain validation,
    # exercising the failure branch after the order precondition check.
    ship_resp = client.post(
        "/api/v1/shipments",
        json={"order_id": order["id"], "carrier_name": "   "},
        headers=admin_headers,
    )
    assert ship_resp.status_code == 400, ship_resp.text

    fetched = client.get(f"/api/v1/orders/{order['id']}", headers=view_headers)
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["status"] == "confirmed"
    assert _shipment_count(e2e_session_factory) == before


def test_shipment_lifecycle_pending_to_delivered(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    """Shipment lifecycle: pending → in-transit → delivered with versions."""
    order = _create_confirmed_order(client, customer_manage_headers, view_headers)
    created = client.post(
        "/api/v1/shipments",
        json={"order_id": order["id"], "carrier_name": "FastShip"},
        headers=admin_headers,
    )
    assert created.status_code == 201, created.text
    shipment = created.json()
    assert shipment["status"] == "pending"
    assert shipment["delivered_at"] is None

    in_transit = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": shipment["version"], "status": "in-transit"},
        headers=admin_headers,
    )
    assert in_transit.status_code == 200, in_transit.text
    assert in_transit.json()["status"] == "in-transit"
    assert in_transit.json()["version"] == shipment["version"] + 1

    delivered = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": in_transit.json()["version"], "status": "delivered"},
        headers=admin_headers,
    )
    assert delivered.status_code == 200, delivered.text
    assert delivered.json()["status"] == "delivered"
    assert delivered.json()["delivered_at"] is not None
    assert delivered.json()["version"] == in_transit.json()["version"] + 1

    replayed = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": delivered.json()["version"], "status": "in-transit"},
        headers=admin_headers,
    )
    assert replayed.status_code == 409, replayed.text
    assert replayed.json()["code"] == "INVALID_TRANSITION"
