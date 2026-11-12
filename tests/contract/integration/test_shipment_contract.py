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


def _create_shipment(
    client, customer_manage_headers, view_headers, admin_headers
) -> dict:
    order = _confirmed_order(client, customer_manage_headers, view_headers)
    response = client.post(
        "/api/v1/shipments",
        json=_payload(order["id"]),
        headers=admin_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_update_shipment_requires_authentication(client) -> None:
    response = client.patch(
        "/api/v1/shipments/SHIP-missing", json={"version": 1, "status": "in-transit"}
    )

    assert response.status_code == 401
    _assert_envelope(response.json())
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_update_shipment_requires_admin_permission(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    shipment = _create_shipment(
        client, customer_manage_headers, view_headers, admin_headers
    )

    response = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": 1, "status": "in-transit"},
        headers=customer_manage_headers,
    )

    assert response.status_code == 403
    _assert_envelope(response.json())
    assert response.json()["code"] == "FORBIDDEN"


def test_update_carrier_while_pending(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    shipment = _create_shipment(
        client, customer_manage_headers, view_headers, admin_headers
    )

    response = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": shipment["version"], "carrier_name": "SlowShip"},
        headers=admin_headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["carrier_name"] == "SlowShip"
    assert body["status"] == "pending"
    assert body["version"] == shipment["version"] + 1


def test_update_shipment_rejects_stale_version(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    shipment = _create_shipment(
        client, customer_manage_headers, view_headers, admin_headers
    )

    response = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": shipment["version"] + 1, "status": "in-transit"},
        headers=admin_headers,
    )

    assert response.status_code == 409, response.text
    body = response.json()
    assert body["code"] == "STALE_UPDATE"
    assert f"expected_version={shipment['version'] + 1}" in body["message"]
    assert f"current_version={shipment['version']}" in body["message"]


def test_update_shipment_rejects_invalid_transition(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    shipment = _create_shipment(
        client, customer_manage_headers, view_headers, admin_headers
    )

    response = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": shipment["version"], "status": "delivered"},
        headers=admin_headers,
    )

    assert response.status_code == 409, response.text
    assert response.json()["code"] == "INVALID_TRANSITION"


def test_delivery_confirmation_sets_delivered_at(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    shipment = _create_shipment(
        client, customer_manage_headers, view_headers, admin_headers
    )

    in_transit = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": shipment["version"], "status": "in-transit"},
        headers=admin_headers,
    )
    assert in_transit.status_code == 200, in_transit.text
    assert in_transit.json()["status"] == "in-transit"
    assert in_transit.json()["delivered_at"] is None

    delivered = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": in_transit.json()["version"], "status": "delivered"},
        headers=admin_headers,
    )
    assert delivered.status_code == 200, delivered.text
    body = delivered.json()
    assert body["status"] == "delivered"
    assert body["delivered_at"] is not None
    assert body["version"] == in_transit.json()["version"] + 1


def test_delivered_shipment_cannot_be_modified(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    shipment = _create_shipment(
        client, customer_manage_headers, view_headers, admin_headers
    )
    in_transit = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": shipment["version"], "status": "in-transit"},
        headers=admin_headers,
    )
    delivered = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": in_transit.json()["version"], "status": "delivered"},
        headers=admin_headers,
    )
    assert delivered.status_code == 200, delivered.text

    response = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": delivered.json()["version"], "carrier_name": "LateShip"},
        headers=admin_headers,
    )

    assert response.status_code == 409, response.text
    assert response.json()["code"] == "INVALID_TRANSITION"


def test_update_shipment_not_found(
    client, admin_headers
) -> None:
    response = client.patch(
        "/api/v1/shipments/SHIP-missing",
        json={"version": 1, "status": "in-transit"},
        headers=admin_headers,
    )

    assert response.status_code == 404, response.text
    assert response.json()["code"] == "SHIPMENT_NOT_FOUND"


def test_update_shipment_requires_a_change(
    client, customer_manage_headers, view_headers, admin_headers
) -> None:
    shipment = _create_shipment(
        client, customer_manage_headers, view_headers, admin_headers
    )

    response = client.patch(
        f"/api/v1/shipments/{shipment['id']}",
        json={"version": shipment["version"]},
        headers=admin_headers,
    )

    assert response.status_code == 400, response.text
    assert response.json()["code"] == "VALIDATION_ERROR"
