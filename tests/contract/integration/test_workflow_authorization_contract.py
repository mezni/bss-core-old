"""Authorization matrix contract for the four S07 workflows.

Asserts the full permission matrix from
``specs/008-integration-mvp/contracts/authorization_contract.md`` plus the
401 behavior for missing/invalid bearer tokens. Granted permissions may
still fail business validation; they must simply not be rejected with
401/403.
"""

from __future__ import annotations

import pytest

WORKFLOWS = {
    "customer_to_order": (
        "/api/v1/orders",
        {
            "customer_id": "CUS-missing",
            "items": [{"description": "Widget", "quantity": 1, "unit_price": 10.0}],
        },
    ),
    "order_to_shipment": (
        "/api/v1/shipments",
        {"order_id": "ORD-missing", "carrier_name": "FastShip"},
    ),
    "order_to_invoice": (
        "/api/v1/invoices",
        {"reference_id": "ORD-missing"},
    ),
    "invoice_to_payment": (
        "/api/v1/payments",
        {
            "invoice_id": "INV-missing",
            "amount": 10.0,
            "payment_method": "card",
        },
    ),
}

MATRIX = {
    "user:view": {
        "customer_to_order": True,
        "order_to_shipment": False,
        "order_to_invoice": False,
        "invoice_to_payment": False,
    },
    "user:billing": {
        "customer_to_order": False,
        "order_to_shipment": False,
        "order_to_invoice": True,
        "invoice_to_payment": True,
    },
    "user:admin": {
        "customer_to_order": True,
        "order_to_shipment": True,
        "order_to_invoice": True,
        "invoice_to_payment": True,
    },
}


@pytest.mark.parametrize("permission", MATRIX)
@pytest.mark.parametrize("workflow", WORKFLOWS)
def test_permission_matrix(workflow, permission, client, auth_headers) -> None:
    path, payload = WORKFLOWS[workflow]
    response = client.post(path, json=payload, headers=auth_headers(permission))

    if MATRIX[permission][workflow]:
        assert response.status_code not in (401, 403), response.text
    else:
        assert response.status_code == 403, response.text
        body = response.json()
        assert body["code"] == "FORBIDDEN"
        assert set(body) == {"error", "message", "code"}


@pytest.mark.parametrize("workflow", WORKFLOWS)
def test_missing_token_is_unauthenticated(workflow, client) -> None:
    path, payload = WORKFLOWS[workflow]
    response = client.post(path, json=payload)

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "UNAUTHENTICATED"
    assert set(body) == {"error", "message", "code"}


@pytest.mark.parametrize("workflow", WORKFLOWS)
def test_invalid_token_is_unauthenticated(workflow, client) -> None:
    path, payload = WORKFLOWS[workflow]
    response = client.post(
        path, json=payload, headers={"Authorization": "Bearer not-a-jwt"}
    )

    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_denied_invoice_request_creates_no_records(
    client, view_headers, integration_session_factory
) -> None:
    """A 403 leaves the invoice table untouched."""
    from sqlalchemy import func, select

    from src.models.billing_management.infrastructure.orm import InvoiceORM

    path, payload = WORKFLOWS["order_to_invoice"]
    response = client.post(path, json=payload, headers=view_headers)
    assert response.status_code == 403

    with integration_session_factory() as session:
        count = session.scalar(select(func.count()).select_from(InvoiceORM)) or 0
    assert count == 0


def test_denied_payment_request_creates_no_records(
    client, view_headers, integration_session_factory
) -> None:
    """A 403 leaves the payment table untouched."""
    from sqlalchemy import func, select

    from src.models.billing_management.infrastructure.orm import PaymentORM

    path, payload = WORKFLOWS["invoice_to_payment"]
    response = client.post(path, json=payload, headers=view_headers)
    assert response.status_code == 403

    with integration_session_factory() as session:
        count = session.scalar(select(func.count()).select_from(PaymentORM)) or 0
    assert count == 0
