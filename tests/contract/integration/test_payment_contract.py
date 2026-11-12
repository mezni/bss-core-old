"""Contract tests for the payment API entry points (US4)."""

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


def test_create_payment_requires_authentication(client) -> None:
    response = client.post("/api/v1/payments", json=_payload())

    assert response.status_code == 401
    _assert_envelope(response.json())
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_create_payment_requires_billing_permission(client, view_headers) -> None:
    response = client.post("/api/v1/payments", json=_payload(), headers=view_headers)

    assert response.status_code == 403
    _assert_envelope(response.json())
    assert response.json()["code"] == "FORBIDDEN"


def test_billing_role_can_process_payment(
    client, customer_manage_headers, view_headers, billing_headers
) -> None:
    invoice = _pending_invoice(
        client, customer_manage_headers, view_headers, billing_headers
    )
    response = client.post(
        "/api/v1/payments",
        json=_payload(invoice["id"], invoice["total_amount"]),
        headers=billing_headers,
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["invoice_id"] == invoice["id"]
    assert body["amount"] == invoice["total_amount"]
    assert body["status"] == "completed"


def test_payment_error_envelope_shape(
    client, customer_manage_headers, view_headers, billing_headers
) -> None:
    invoice = _pending_invoice(
        client, customer_manage_headers, view_headers, billing_headers
    )
    first = client.post(
        "/api/v1/payments",
        json=_payload(invoice["id"], invoice["total_amount"]),
        headers=billing_headers,
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/api/v1/payments",
        json=_payload(invoice["id"], invoice["total_amount"]),
        headers=billing_headers,
    )
    assert duplicate.status_code == 409
    _assert_envelope(duplicate.json())


def test_get_missing_payment_returns_404(client, view_headers) -> None:
    response = client.get("/api/v1/payments/PAY-missing", headers=view_headers)

    assert response.status_code == 404
    _assert_envelope(response.json())
