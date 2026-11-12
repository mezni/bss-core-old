"""Contract tests for order workflow entry points (US1).

401 without a token, 403 without ``user:view``, and the standardized
error envelope shape per contracts/error_response_contract.md.
"""

from __future__ import annotations

ORDER_PAYLOAD = {
    "customer_id": "C-1",
    "items": [{"description": "Widget A", "quantity": 1, "unit_price": 10.00}],
}


def _assert_envelope(body: dict) -> None:
    assert set(body) == {"error", "message", "code"}
    assert body["error"] == body["code"].lower()
    assert isinstance(body["message"], str) and body["message"]


def test_create_order_requires_authentication(client) -> None:
    response = client.post("/api/v1/orders", json=ORDER_PAYLOAD)

    assert response.status_code == 401
    _assert_envelope(response.json())
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_create_order_requires_view_permission(
    client, customer_manage_headers
) -> None:
    response = client.post("/api/v1/orders", json=ORDER_PAYLOAD, headers=customer_manage_headers)

    assert response.status_code == 403
    _assert_envelope(response.json())
    assert response.json()["code"] == "FORBIDDEN"
    assert "user:view" in response.json()["message"]


def test_billing_role_cannot_create_order(client, billing_headers) -> None:
    response = client.post("/api/v1/orders", json=ORDER_PAYLOAD, headers=billing_headers)

    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


def test_admin_can_reach_create_order(client, admin_headers) -> None:
    response = client.post("/api/v1/orders", json=ORDER_PAYLOAD, headers=admin_headers)

    assert response.status_code == 404  # unknown customer, but authorized
    _assert_envelope(response.json())


def test_confirm_order_requires_authentication(client) -> None:
    response = client.patch("/api/v1/orders/ORD-1/transitions/confirm")

    assert response.status_code == 401
    _assert_envelope(response.json())
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_confirm_order_requires_view_permission(
    client, customer_manage_headers
) -> None:
    response = client.patch(
        "/api/v1/orders/ORD-1/transitions/confirm",
        headers=customer_manage_headers,
    )

    assert response.status_code == 403
    _assert_envelope(response.json())
    assert response.json()["code"] == "FORBIDDEN"
    assert "user:view" in response.json()["message"]


def test_create_order_success_response_contract(
    client, customer_manage_headers, view_headers
) -> None:
    customer = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Jane Doe",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "contract-order@example.com",
        },
        headers=customer_manage_headers,
    )
    assert customer.status_code == 201, customer.text

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer.json()["id"],
            "items": [
                {"description": "Widget A", "quantity": 2, "unit_price": 10.50},
                {"description": "Widget B", "quantity": 1, "unit_price": 5.25},
            ],
        },
        headers=view_headers,
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["status"] == "draft"
    assert data["customer_id"] == customer.json()["id"]
    assert data["subtotal"] == 26.25
    assert data["tax_amount"] == 2.62
    assert data["total"] == 28.87
    assert data["version"] == 1
    assert len(data["items"]) == 2
    assert data["items"][0]["line_total"] == 21.0
    assert data["items"][1]["line_total"] == 5.25
    assert "created_at" in data
    assert "updated_at" in data
