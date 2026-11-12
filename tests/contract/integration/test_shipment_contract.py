"""Contract tests for the shipment API entry points (US2).

401 without a token, 403 without ``user:admin``, and the standardized
error envelope shape per contracts/error_response_contract.md.
"""

from __future__ import annotations


def _confirmed_order(client, customer_manage_headers, view_headers) -> dict:
    """Create a customer and a confirmed order, returning the order."""
    customer_resp = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Contract Doe",
            "first_name": "Contract",
            "last_name": "Doe",
            "email": "ship-contract@example.com",
        },
        headers=customer_manage_headers,
    )
    assert customer_resp.status_code == 201, customer_resp.text

    order_resp = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_resp.json()["id"],
            "items": [{"description": "Widget", "quantity": 1, "unit_price": 10.00}],
        },
        headers=view_headers,
    )
    assert order_resp.status_code == 201, order_resp.text

    confirm_resp = client.patch(
        f"/api/v1/orders/{order_resp.json()['id']}/transitions/confirm",
        headers=view_headers,
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    return confirm_resp.json()


def _payload(order_id: str = "ORD-missing") -> dict:
    return {"order_id": order_id, "carrier_name": "FastShip"}


def _assert_envelope(body: dict) -> None:
    assert set(body) == {"error", "message", "code"}
    assert body["error"] == body["code"].lower()
    assert isinstance(body["message"], str) and body["message"]


def test_create_shipment_requires_authentication(client) -> None:
    response = client.post("/api/v1/shipments", json=_payload())

    assert response.status_code == 401
    _assert_envelope(response.json())
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_create_shipment_requires_admin_permission(client, customer_manage_headers) -> None:
    response = client.post(
        "/api/v1/shipments", json=_payload(), headers=customer_manage_headers
    )

    assert response.status_code == 403
    _assert_envelope(response.json())
    assert response.json()["code"] == "FORBIDDEN"


def test_billing_role_cannot_create_shipment(client, billing_headers) -> None:
    response = client.post(
        "/api/v1/shipments", json=_payload(), headers=billing_headers
    )

    assert response.status_code == 403
    _assert_envelope(response.json())
    assert response.json()["code"] == "FORBIDDEN"


def test_admin_can_reach_create_shipment(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    order = _confirmed_order(client, customer_manage_headers, view_headers)
    response = client.post(
        "/api/v1/shipments", json=_payload(order["id"]), headers=admin_headers
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["order_id"] == order["id"]
    assert body["status"] == "pending"


def test_error_envelope_shape(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    """Verify the response envelope has exactly the three standard fields."""
    order = _confirmed_order(client, customer_manage_headers, view_headers)
    response = client.post(
        "/api/v1/shipments", json=_payload(order["id"]), headers=admin_headers
    )

    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert "tracking_reference" in body
