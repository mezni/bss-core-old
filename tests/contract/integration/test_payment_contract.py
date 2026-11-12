"""Contract tests for the payment API entry points (US4).

These tests verify the payment API entry points (create, get, list).
"""

from __future__ import annotations


def _pending_invoice(client, customer_manage_headers, view_headers, billing_headers) -> dict:
    customer_resp = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Payment Contract Doe",
            "first_name": "Payment",
            "last_name": "Doe",
            "email": "payment-contract@example.com",
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

    invoice_resp = client.post(
        "/api/v1/invoices",
        json={"reference_id": confirm_resp.json()["id"]},
        headers=billing_headers,
    )
    assert invoice_resp.status_code == 201, invoice_resp.text
    return invoice_resp.json()


def _payload(invoice_id: str = "INV-missing", amount: float = 10.0) -> dict:
    return {
        "invoice_id": invoice_id,
        "amount": amount,
        "payment_method": "card",
    }


def _assert_envelope(body: dict) -> None:
    assert set(body) == {"error", "message", "code"}
    assert body["error"] == body["code"].lower()
    assert isinstance(body["message"], str) and body["message"]


# ------------------------------------------------------------------
# T036 – Payment list tests
# ------------------------------------------------------------------
def test_list_payments_requires_authentication(client) -> None:
    """Unauthenticated access to the payment list endpoint returns 401."""
    response = client.get("/api/v1/payments")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "UNAUTHENTICATED"


def test_list_payments_view_access(
    client, view_headers
) -> None:
    """Authenticated access with user:view permission returns 200."""
    response = client.get("/api/v1/payments", headers=view_headers)

    assert response.status_code == 200, response.text
    body = response.json()
    # When there are no payments, the list is empty
    assert body["items"] == []
    assert body["total"] == 0


def test_list_payments_with_invoice_filter(
    client, billing_headers, view_headers
) -> None:
    """List payments filtered by a specific invoice ID.

    A payment must first be created (via the process payment workflow)
    and then the list should return only payments for that invoice.
    """
    # Create a customer and order (simplified)
    customer_resp = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Test",
            "first_name": "Test",
            "last_name": "User",
            "email": "pay-contract@example.com",
        },
        headers=billing_headers,
    )
    assert customer_resp.status_code == 201, customer_resp.text
    customer_id = customer_resp.json()["id"]

    order_resp = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer_id,
            "items": [{"description": "Widget", "quantity": 1, "unit_price": 10.00}],
        },
        headers=view_headers,
    )
    assert order_resp.status_code == 201, order_resp.text

    # Confirm the order
    confirm_resp = client.patch(
        f"/api/v1/orders/{order_resp.json()['id']}/transitions/confirm",
        headers=view_headers,
    )
    assert confirm_resp.status_code == 200, confirm_resp.text

    # Create an invoice
    invoice_resp = client.post(
        "/api/v1/invoices",
        json={"reference_id": confirm_resp.json()["id"]},
        headers=billing_headers,
    )
    assert invoice_resp.status_code == 201, invoice_resp.text
    invoice_id = invoice_resp.json()["id"]

    # Process a payment against the invoice
    payment_resp = client.post(
        "/api/v1/payments",
        json={"invoice_id": invoice_id, "amount": invoice_resp.json()["total_amount"], "payment_method": "card"},
        headers=billing_headers,
    )
    assert payment_resp.status_code == 201, payment_resp.text

    # List payments filtered by invoice_id
    list_resp = client.get(
        "/api/v1/payments",
        params={"invoice_id": invoice_id},
        headers=billing_headers,
    )
    assert list_resp.status_code == 200, list_resp.text
    body = list_resp.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["invoice_id"] == invoice_id


def test_get_missing_payment_returns_404(client, view_headers) -> None:
    response = client.get("/api/v1/payments/PAY-missing", headers=view_headers)

    assert response.status_code == 404
    _assert_envelope(response.json())