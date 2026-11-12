"""E2E journey test for the customer-to-order workflow (US1).

Create a customer, create an order with items, confirm the order —
order ``status="confirmed"`` with correct customer/item associations.
Order without items is rejected with the standardized 400 envelope and no
order is created. Unknown customer yields 404 NOT_FOUND.
"""

from __future__ import annotations

from sqlalchemy import func, select

from src.models.order_management.infrastructure.orm import OrderORM


def _create_customer(client, customer_manage_headers, email: str) -> dict:
    response = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Jane Doe",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": email,
        },
        headers=customer_manage_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _order_count(e2e_session_factory) -> int:
    with e2e_session_factory() as session:
        return session.scalar(select(func.count()).select_from(OrderORM)) or 0


def test_customer_to_order_workflow(
    client, customer_manage_headers, view_headers, e2e_session_factory
) -> None:
    customer = _create_customer(client, customer_manage_headers, "jane@example.com")

    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer["id"],
            "items": [
                {
                    "description": "Widget A",
                    "quantity": 2,
                    "unit_price": 10.50,
                }
            ],
        },
        headers=view_headers,
    )
    assert response.status_code == 201, response.text
    order = response.json()
    assert order["status"] == "draft"
    assert order["customer_id"] == customer["id"]
    assert order["subtotal"] == 21.0
    assert order["tax_amount"] == 2.1
    assert order["total"] == 23.1
    assert len(order["items"]) == 1
    assert order["items"][0]["description"] == "Widget A"
    assert order["items"][0]["line_total"] == 21.0

    confirm = client.patch(
        f"/api/v1/orders/{order['id']}/transitions/confirm",
        headers=view_headers,
    )
    assert confirm.status_code == 200, confirm.text
    confirmed = confirm.json()
    assert confirmed["status"] == "confirmed"
    assert confirmed["version"] == 2
    assert confirmed["customer_id"] == customer["id"]

    fetched = client.get(f"/api/v1/orders/{order['id']}", headers=view_headers)
    assert fetched.status_code == 200, fetched.text
    persisted = fetched.json()
    assert persisted["status"] == "confirmed"
    assert persisted["customer_id"] == customer["id"]
    assert len(persisted["items"]) == 1
    assert persisted["items"][0]["description"] == "Widget A"

    assert _order_count(e2e_session_factory) == 1


def test_order_without_items_rejected(
    client, customer_manage_headers, view_headers, e2e_session_factory
) -> None:
    customer = _create_customer(client, customer_manage_headers, "noitems@example.com")

    response = client.post(
        "/api/v1/orders",
        json={"customer_id": customer["id"], "items": []},
        headers=view_headers,
    )

    assert response.status_code == 400, response.text
    body = response.json()
    assert body["code"] == "VALIDATION_ERROR"
    assert body["error"] == "validation_error"
    assert body["message"]
    assert _order_count(e2e_session_factory) == 0


def test_order_unknown_customer_rejected(
    client, view_headers, e2e_session_factory
) -> None:
    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": "C-does-not-exist",
            "items": [
                {"description": "Widget A", "quantity": 1, "unit_price": 10.00}
            ],
        },
        headers=view_headers,
    )

    assert response.status_code == 404, response.text
    body = response.json()
    assert body["code"] == "ORDER_NOT_FOUND"
    assert body["error"] == "order_not_found"
    assert "C-does-not-exist" in body["message"]
    assert _order_count(e2e_session_factory) == 0
