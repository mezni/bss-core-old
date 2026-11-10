"""Contract tests for contact and address endpoints."""

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


def add_contact(client, auth_headers, customer_id: str) -> dict:
    response = client.post(
        f"/api/v1/customers/{customer_id}/contacts",
        json={
            "name": "Jane",
            "contact_type": "EMAIL",
            "value": "jane@example.com",
            "is_primary": True,
        },
        headers=auth_headers("customer:manage"),
    )
    assert response.status_code == 201, response.text
    return response.json()


def add_address(client, auth_headers, customer_id: str) -> dict:
    response = client.post(
        f"/api/v1/customers/{customer_id}/addresses",
        json={
            "label": "Billing",
            "line1": "1 Main St",
            "city": "Springfield",
            "region": "IL",
            "postal_code": "62701",
            "country": "US",
            "is_primary": True,
        },
        headers=auth_headers("customer:manage"),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_contact_lifecycle(client, auth_headers) -> None:
    customer = create_customer(client, auth_headers)
    contact = add_contact(client, auth_headers, customer["id"])

    assert contact["customer_id"] == customer["id"]
    assert contact["value"] == "jane@example.com"
    assert contact["is_primary"] is True

    fetched = client.get(
        f"/api/v1/customers/{customer['id']}", headers=auth_headers("customer:view")
    )
    assert fetched.json()["version"] == 2
    assert len(fetched.json()["contacts"]) == 1

    updated = client.patch(
        f"/api/v1/customers/{customer['id']}/contacts/{contact['id']}",
        json={"version": 2, "value": "+1 555 0100", "contact_type": "PHONE"},
        headers=auth_headers("customer:manage"),
    )
    assert updated.status_code == 200
    assert updated.json()["value"] == "+1 555 0100"
    assert updated.json()["contact_type"] == "PHONE"

    removed = client.request(
        "DELETE",
        f"/api/v1/customers/{customer['id']}/contacts/{contact['id']}",
        json={"version": 3},
        headers=auth_headers("customer:manage"),
    )
    assert removed.status_code == 204

    final = client.get(
        f"/api/v1/customers/{customer['id']}", headers=auth_headers("customer:view")
    )
    assert final.json()["contacts"] == []
    assert final.json()["version"] == 4


def test_address_lifecycle(client, auth_headers) -> None:
    customer = create_customer(client, auth_headers)
    address = add_address(client, auth_headers, customer["id"])

    assert address["country"] == "US"
    assert address["is_primary"] is True

    updated = client.patch(
        f"/api/v1/customers/{customer['id']}/addresses/{address['id']}",
        json={"version": 2, "line1": "1 Main Street", "region": "IL"},
        headers=auth_headers("customer:manage"),
    )
    assert updated.status_code == 200
    assert updated.json()["line1"] == "1 Main Street"

    removed = client.request(
        "DELETE",
        f"/api/v1/customers/{customer['id']}/addresses/{address['id']}",
        json={"version": 3},
        headers=auth_headers("customer:manage"),
    )
    assert removed.status_code == 204

    eligibility = client.get(
        f"/api/v1/customers/{customer['id']}/eligibility",
        headers=auth_headers("customer:view"),
    )
    assert eligibility.json()["eligible"] is False
    assert "NO_ADDRESS" in eligibility.json()["reasons"]


def test_duplicate_primary_contact_returns_conflict(client, auth_headers) -> None:
    customer = create_customer(client, auth_headers)
    add_contact(client, auth_headers, customer["id"])

    response = client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        json={
            "name": "Jane",
            "contact_type": "PHONE",
            "value": "+1 555 0100",
            "is_primary": True,
        },
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_PRIMARY_CONTACT"


def test_stale_child_mutation_returns_conflict(client, auth_headers) -> None:
    customer = create_customer(client, auth_headers)
    contact = add_contact(client, auth_headers, customer["id"])

    response = client.patch(
        f"/api/v1/customers/{customer['id']}/contacts/{contact['id']}",
        json={"version": 1, "value": "other@example.com"},
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "STALE_UPDATE"


def test_missing_contact_and_address_return_not_found(client, auth_headers) -> None:
    customer = create_customer(client, auth_headers)

    contact = client.patch(
        f"/api/v1/customers/{customer['id']}/contacts/missing",
        json={"version": 1, "value": "other@example.com"},
        headers=auth_headers("customer:manage"),
    )
    assert contact.status_code == 404
    assert contact.json()["error"]["code"] == "CONTACT_NOT_FOUND"

    address = client.patch(
        f"/api/v1/customers/{customer['id']}/addresses/missing",
        json={"version": 1, "line1": "2 Main St"},
        headers=auth_headers("customer:manage"),
    )
    assert address.status_code == 404
    assert address.json()["error"]["code"] == "ADDRESS_NOT_FOUND"


def test_child_mutations_require_manage_permission(client, auth_headers) -> None:
    customer = create_customer(client, auth_headers)

    response = client.post(
        f"/api/v1/customers/{customer['id']}/contacts",
        json={"name": "Jane", "contact_type": "EMAIL", "value": "jane@example.com"},
        headers=auth_headers("customer:view"),
    )

    assert response.status_code == 403
