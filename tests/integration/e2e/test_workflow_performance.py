"""Performance baseline smoke test for the four S07 workflow endpoints (S07-07).

Measurement only: records latency in the assertion message and enforces a
generous ceiling so regressions are visible without making CI flaky.
"""

from __future__ import annotations

import time

import pytest

MAX_SECONDS = 2.0


@pytest.mark.performance
def test_workflow_endpoint_latency_baseline(
    client, customer_manage_headers, view_headers, billing_headers, admin_headers
) -> None:
    timings: dict[str, float] = {}

    started = time.perf_counter()
    customer = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Perf Doe",
            "first_name": "Perf",
            "last_name": "Doe",
            "email": "perf@example.com",
        },
        headers=customer_manage_headers,
    )
    timings["customer"] = time.perf_counter() - started
    assert customer.status_code == 201, customer.text

    started = time.perf_counter()
    order = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer.json()["id"],
            "items": [{"description": "Widget", "quantity": 1, "unit_price": 10.0}],
        },
        headers=view_headers,
    )
    timings["order"] = time.perf_counter() - started
    assert order.status_code == 201, order.text

    started = time.perf_counter()
    confirmed = client.patch(
        f"/api/v1/orders/{order.json()['id']}/transitions/confirm",
        headers=view_headers,
    )
    timings["confirm"] = time.perf_counter() - started
    assert confirmed.status_code == 200, confirmed.text

    started = time.perf_counter()
    shipment = client.post(
        "/api/v1/shipments",
        json={"order_id": confirmed.json()["id"], "carrier_name": "FastShip"},
        headers=admin_headers,
    )
    timings["shipment"] = time.perf_counter() - started
    assert shipment.status_code == 201, shipment.text

    invoice_order = client.post(
        "/api/v1/orders",
        json={
            "customer_id": customer.json()["id"],
            "items": [{"description": "Widget", "quantity": 1, "unit_price": 10.0}],
        },
        headers=view_headers,
    )
    assert invoice_order.status_code == 201, invoice_order.text
    invoice_confirmed = client.patch(
        f"/api/v1/orders/{invoice_order.json()['id']}/transitions/confirm",
        headers=view_headers,
    )
    assert invoice_confirmed.status_code == 200, invoice_confirmed.text

    started = time.perf_counter()
    invoice = client.post(
        "/api/v1/invoices",
        json={"reference_id": invoice_confirmed.json()["id"]},
        headers=billing_headers,
    )
    timings["invoice"] = time.perf_counter() - started
    assert invoice.status_code == 201, invoice.text

    started = time.perf_counter()
    payment = client.post(
        "/api/v1/payments",
        json={
            "invoice_id": invoice.json()["id"],
            "amount": invoice.json()["total_amount"],
            "payment_method": "card",
        },
        headers=billing_headers,
    )
    timings["payment"] = time.perf_counter() - started
    assert payment.status_code == 201, payment.text

    slowest = max(timings.values())
    assert slowest < MAX_SECONDS, timings
