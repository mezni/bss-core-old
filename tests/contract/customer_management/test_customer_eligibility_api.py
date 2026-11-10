"""Contract tests for the customer eligibility endpoint."""

from __future__ import annotations


def create_customer(client, auth_headers) -> dict:
    response = client.post(
        "/api/v1/customers",
        json={
            "customer_type": "INDIVIDUAL",
            "display_name": "Jane Doe",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
        },
        headers=auth_headers("customer:manage"),
    )
    assert response.status_code == 201, response.text
    return response.json()


def add_contact(client, auth_headers, customer_id: str) -> None:
    response = client.post(
        f"/api/v1/customers/{customer_id}/contacts",
        json={
            "name": "Jane",
            "contact_type": "EMAIL",
            "value": "jane@example.com",
        },
        headers=auth_headers("customer:manage"),
    )
    assert response.status_code == 201, response.text


def add_address(client, auth_headers, customer_id: str) -> None:
    response = client.post(
        f"/api/v1/customers/{customer_id}/addresses",
        json={
            "line1": "1 Main St",
            "city": "Springfield",
            "postal_code": "62701",
            "country": "US",
        },
        headers=auth_headers("customer:manage"),
    )
    assert response.status_code == 201, response.text


def eligibility(client, auth_headers, customer_id: str) -> dict:
    response = client.get(
        f"/api/v1/customers/{customer_id}/eligibility",
        headers=auth_headers("customer:view"),
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_eligibility_transitions(client, auth_headers) -> None:
    customer = create_customer(client, auth_headers)

    initial = eligibility(client, auth_headers, customer["id"])
    assert initial["eligible"] is False
    assert initial["reasons"] == ["NO_CONTACT", "NO_ADDRESS"]

    add_contact(client, auth_headers, customer["id"])
    no_address = eligibility(client, auth_headers, customer["id"])
    assert no_address["reasons"] == ["NO_ADDRESS"]

    add_address(client, auth_headers, customer["id"])
    eligible = eligibility(client, auth_headers, customer["id"])
    assert eligible["eligible"] is True
    assert eligible["reasons"] == []

    client.post(
        f"/api/v1/customers/{customer['id']}/deactivate",
        headers=auth_headers("customer:manage"),
    )
    inactive = eligibility(client, auth_headers, customer["id"])
    assert inactive["eligible"] is False
    assert inactive["reasons"] == ["INACTIVE"]

    client.post(
        f"/api/v1/customers/{customer['id']}/reactivate",
        headers=auth_headers("customer:manage"),
    )
    restored = eligibility(client, auth_headers, customer["id"])
    assert restored["eligible"] is True


def test_eligibility_for_missing_customer_returns_not_found(client, auth_headers) -> None:
    response = client.get(
        "/api/v1/customers/missing/eligibility",
        headers=auth_headers("customer:view"),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "CUSTOMER_NOT_FOUND"


def test_eligibility_requires_view_permission(client, auth_headers) -> None:
    customer = create_customer(client, auth_headers)

    response = client.get(
        f"/api/v1/customers/{customer['id']}/eligibility",
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 403
