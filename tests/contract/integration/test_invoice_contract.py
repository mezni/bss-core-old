"""Contract tests for the invoice API entry points (US4)."""

from __future__ import annotations


def _confirmed_order(client, customer_manage_headers, view_headers) -> dict:
    customer_resp = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Invoice Contract Doe",
            "first_name": "Invoice",
            "last_name": "Doe",
            "email": "invoice-contract@example.com",
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


def _payload(reference_id: str = "ORD-missing") -> dict:
    return {"reference_id": reference_id, "due_days": 30}


def _assert_envelope(body: dict) -> None:
    assert set(body) == {"error", "message", "code"}
    assert body["error"] == body["code"].lower()
    assert isinstance(body["message"], str) and body["message"]


def test_create_invoice_requires_authentication(client) -> None:
    response = client.post("/api/v1/invoices", json=_payload())

    assert response.status_code == 401
    _assert_envelope(response.json())
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_create_invoice_requires_billing_permission(client, view_headers) -> None:
    response = client.post("/api/v1/invoices", json=_payload(), headers=view_headers)

    assert response.status_code == 403
    _assert_envelope(response.json())
    assert response.json()["code"] == "FORBIDDEN"


def test_billing_role_can_create_invoice(
    client, customer_manage_headers, view_headers, billing_headers
) -> None:
    order = _confirmed_order(client, customer_manage_headers, view_headers)
    response = client.post(
        "/api/v1/invoices", json=_payload(order["id"]), headers=billing_headers
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "pending"
    assert body["reference_id"] == order["id"]
    assert body["invoice_number"].startswith("INV-")


def test_list_invoices_requires_view_permission(client, billing_headers) -> None:
    response = client.get("/api/v1/invoices", headers=billing_headers)

    assert response.status_code == 403
    _assert_envelope(response.json())


def test_list_invoices_returns_pagination(
    client, customer_manage_headers, view_headers, billing_headers
) -> None:
    order = _confirmed_order(client, customer_manage_headers, view_headers)
    created = client.post(
        "/api/v1/invoices", json=_payload(order["id"]), headers=billing_headers
    )
    assert created.status_code == 201, created.text

    response = client.get("/api/v1/invoices?page=1&page_size=20", headers=view_headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["total"] == 1
    assert len(body["items"]) == 1


def test_get_missing_invoice_returns_404(client, view_headers) -> None:
    response = client.get("/api/v1/invoices/INV-missing", headers=view_headers)

    assert response.status_code == 404
    _assert_envelope(response.json())
    assert response.json()["code"] == "INVOICE_NOT_FOUND"


def test_invoice_error_envelope_shape(
    client, customer_manage_headers, view_headers, billing_headers
) -> None:
    order = _confirmed_order(client, customer_manage_headers, view_headers)
    first = client.post(
        "/api/v1/invoices", json=_payload(order["id"]), headers=billing_headers
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/api/v1/invoices", json=_payload(order["id"]), headers=billing_headers
    )
    assert duplicate.status_code == 409
    _assert_envelope(duplicate.json())
