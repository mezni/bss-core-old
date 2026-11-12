"""E2E journey test for the order-to-invoice workflow (US4)."""

from __future__ import annotations

import re

from sqlalchemy import func, select

from src.models.billing_management.infrastructure.orm import InvoiceORM

INVOICE_NUMBER_PATTERN = re.compile(r"^INV-\d{8}-\d{4}$")


def _create_customer(client, customer_manage_headers) -> dict:
    response = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Billing Doe",
            "first_name": "Billing",
            "last_name": "Doe",
            "email": "billing@example.com",
        },
        headers=customer_manage_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _create_order(client, customer_id: str, headers) -> dict:
    response = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [
                {"description": "Widget A", "quantity": 2, "unit_price": 10.00},
                {"description": "Widget B", "quantity": 1, "unit_price": 5.00},
            ],
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _confirm_order(client, order_id: str, headers) -> dict:
    response = client.patch(
        f"/api/v1/orders/{order_id}/transitions/confirm", headers=headers
    )
    assert response.status_code == 200, response.text
    return response.json()


def _confirmed_order(client, customer_manage_headers, view_headers) -> dict:
    customer = _create_customer(client, customer_manage_headers)
    order = _create_order(client, customer["id"], view_headers)
    return _confirm_order(client, order["id"], view_headers)


def _invoice_count(session_factory) -> int:
    with session_factory() as session:
        return session.scalar(select(func.count()).select_from(InvoiceORM)) or 0


def test_order_to_invoice_workflow(
    client, customer_manage_headers, view_headers, billing_headers, e2e_session_factory
) -> None:
    """Confirmed order → pending invoice mirroring items and total."""
    order = _confirmed_order(client, customer_manage_headers, view_headers)

    response = client.post(
        "/api/v1/invoices",
        json={"reference_id": order["id"], "due_days": 30},
        headers=billing_headers,
    )
    assert response.status_code == 201, response.text
    invoice = response.json()

    assert invoice["id"].startswith("INV-")
    assert INVOICE_NUMBER_PATTERN.match(invoice["invoice_number"])
    assert invoice["status"] == "pending"
    assert invoice["reference_id"] == order["id"]
    assert invoice["total_amount"] == order["total"]
    assert len(invoice["items"]) == len(order["items"])
    assert invoice["version"] == 1

    assert _invoice_count(e2e_session_factory) == 1


def test_duplicate_invoice_rejected(
    client, customer_manage_headers, view_headers, billing_headers, e2e_session_factory
) -> None:
    """Generating a second invoice for the same order returns 409 CONFLICT."""
    order = _confirmed_order(client, customer_manage_headers, view_headers)
    first = client.post(
        "/api/v1/invoices",
        json={"reference_id": order["id"]},
        headers=billing_headers,
    )
    assert first.status_code == 201, first.text

    second = client.post(
        "/api/v1/invoices",
        json={"reference_id": order["id"]},
        headers=billing_headers,
    )
    assert second.status_code == 409, second.text
    assert second.json()["code"] == "INVOICE_CONFLICT"
    assert _invoice_count(e2e_session_factory) == 1


def test_invoice_for_draft_order_rejected(
    client, customer_manage_headers, view_headers, billing_headers
) -> None:
    """Invoice generation for a non-confirmed order returns 409 CONFLICT."""
    customer = _create_customer(client, customer_manage_headers)
    order = _create_order(client, customer["id"], view_headers)

    response = client.post(
        "/api/v1/invoices",
        json={"reference_id": order["id"]},
        headers=billing_headers,
    )
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "INVOICE_CONFLICT"


def test_invoice_for_missing_order_returns_404(
    client, billing_headers
) -> None:
    """Invoice generation for an unknown order returns 404 NOT_FOUND."""
    response = client.post(
        "/api/v1/invoices",
        json={"reference_id": "ORD-does-not-exist"},
        headers=billing_headers,
    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "ORDER_NOT_FOUND"
