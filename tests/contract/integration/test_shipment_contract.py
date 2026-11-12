"""Contract tests for the shipment API entry points (US2).

401 without a token, 403 without ``user:admin``, and the standardized
error envelope shape per contracts/error_response_contract.md.
"""

from __future__ import annotations

SHIPMENT_PAYLOAD = {"carrier_name": "FastShip"}


def _assert_envelope(body: dict) -> None:
    assert set(body) == {"error", "message", "code"}
    assert body["error"] == body["code"].lower()
    assert isinstance(body["message"], str) and body["message"]


def test_create_shipment_requires_authentication(client) -> None:
    response = client.post("/api/v1/shipments", json=SHIPMENT_PAYLOAD)

    assert response.status_code == 401
    _assert_envelope(response.json())
    assert response.json()["code"] == "UNAUTHENTICATED"


def test_create_shipment_requires_admin_permission(
    client, customer_manage_headers
) -> None:
    response = client.post("/api/v1/shipments", json=SHIPMENT_PAYLOAD, headers=customer_manage_headers)

    assert response.status_code == 403
    _assert_envelope(response.json())
    assert response.json()["code"] == "FORBIDDEN"


def test_billing_role_cannot_create_shipment(client, billing_headers) -> None:
    response = client.post("/api/v1/shipments", json=SHIPMENT_PAYLOAD, headers=billing_headers)

    assert response.status_code == 403
    _assert_envelope(response.json())
    assert response.json()["code"] == "FORBIDDEN"


def test_admin_can_reach_create_shipment(client, admin_headers) -> None:
    response = client.post("/api/v1/shipments", json=SHIPMENT_PAYLOAD, headers=admin_headers)

    assert response.status_code == 201, response.text
    _assert_envelope(response.json())
    assert response.json()["code"] == "CREATED"  # or whatever code the handler sets


def test_error_envelope_shape(client, admin_headers) -> None:
    """Verify the response envelope has exactly the three standard fields."""
    response = client.post("/api/v1/shipments", json=SHIPMENT_PAYLOAD, headers=admin_headers)

    assert response.status_code == 201
    body = response.json()
    _assert_envelope(body)
    # The ``code`` field should be a stable uppercase identifier.
    assert body["code"].isupper()
    assert body["error"] == body["code"].lower()