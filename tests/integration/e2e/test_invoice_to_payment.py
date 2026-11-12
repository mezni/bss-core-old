"""E2E journey test for the invoice-to-payment workflow (US4)."""

from __future__ import annotations

from sqlalchemy import func, select

from src.models.billing_management.infrastructure.orm import PaymentORM


def _create_customer(client, customer_manage_headers) -> dict:
    response = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Payment Doe",
            "first_name": "Payment",
            "last_name": "Doe",
            "email": "payment@example.com",
        },
        headers=customer_manage_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _confirmed_order(client, customer_manage_headers, view_headers) -> dict:
    customer = _create_customer(client, customer_manage_headers)
    order_resp = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer["id"],
            "items": [{"description": "Widget", "quantity": 1, "unit_price": 42.50}],
        },
        headers=view_headers,
    )
    assert order_resp.status_code == 201, order_resp.text
    order = order_resp.json()
    confirm_resp = client.patch(
        f"/api/v1/orders/{order['id']}/transitions/confirm", headers=view_headers
    )
    assert confirm_resp.status_code == 200, confirm_resp.text
    return confirm_resp.json()


def _pending_invoice(client, customer_manage_headers, view_headers, billing_headers) -> dict:
    order = _confirmed_order(client, customer_manage_headers, view_headers)
    response = client.post(
        "/api/v1/invoices",
        json={"reference_id": order["id"]},
        headers=billing_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def _payment_count(session_factory) -> int:
    with session_factory() as session:
        return session.scalar(select(func.count()).select_from(PaymentORM)) or 0


def test_invoice_to_payment_workflow(
    client,
    customer_manage_headers,
    view_headers,
    billing_headers,
    e2e_session_factory,
) -> None:
    """Pending invoice → payment recorded → invoice paid (terminal)."""
    invoice = _pending_invoice(
        client, customer_manage_headers, view_headers, billing_headers
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice["id"],
            "amount": invoice["total_amount"],
            "payment_method": "card",
        },
        headers=billing_headers,
    )
    assert response.status_code == 201, response.text
    payment = response.json()

    assert payment["id"].startswith("PAY-")
    assert payment["invoice_id"] == invoice["id"]
    assert payment["amount"] == invoice["total_amount"]
    assert payment["status"] == "completed"
    assert payment["transaction_id"]
    assert payment["payment_date"]

    fetched = client.get(f"/api/v1/invoices/{invoice['id']}", headers=view_headers)
    assert fetched.status_code == 200, fetched.text
    updated = fetched.json()
    assert updated["status"] == "paid"
    assert updated["payment_method"] == "card"
    assert updated["payment_date"]
    assert updated["version"] == 2

    assert _payment_count(e2e_session_factory) == 1


def test_payment_on_paid_invoice_rejected(
    client, customer_manage_headers, view_headers, billing_headers
) -> None:
    """A second payment on a paid invoice is rejected and leaves it paid."""
    invoice = _pending_invoice(
        client, customer_manage_headers, view_headers, billing_headers
    )
    payload = {
        "invoice_id": invoice["id"],
        "amount": invoice["total_amount"],
        "payment_method": "card",
    }
    first = client.post("/api/v1/payments", json=payload, headers=billing_headers)
    assert first.status_code == 201, first.text

    second = client.post("/api/v1/payments", json=payload, headers=billing_headers)
    assert second.status_code == 409, second.text
    assert second.json()["code"] == "INVOICE_ALREADY_PAID"

    fetched = client.get(f"/api/v1/invoices/{invoice['id']}", headers=view_headers)
    assert fetched.json()["status"] == "paid"


def test_payment_amount_mismatch_rejected(
    client, customer_manage_headers, view_headers, billing_headers, e2e_session_factory
) -> None:
    """A payment that does not match the invoice total returns 400."""
    invoice = _pending_invoice(
        client, customer_manage_headers, view_headers, billing_headers
    )

    response = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice["id"],
            "amount": invoice["total_amount"] + 1,
            "payment_method": "card",
        },
        headers=billing_headers,
    )
    assert response.status_code == 400, response.text
    assert response.json()["code"] == "PAYMENT_AMOUNT_MISMATCH"

    fetched = client.get(f"/api/v1/invoices/{invoice['id']}", headers=view_headers)
    assert fetched.json()["status"] == "pending"
    assert _payment_count(e2e_session_factory) == 0


def test_payment_for_missing_invoice_returns_404(
    client, billing_headers
) -> None:
    """Paying an unknown invoice returns 404 NOT_FOUND."""
    response = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": "INV-does-not-exist",
            "amount": 10.0,
            "payment_method": "card",
        },
        headers=billing_headers,
    )
    assert response.status_code == 404, response.text
    assert response.json()["code"] == "INVOICE_NOT_FOUND"
