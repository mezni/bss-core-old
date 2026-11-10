"""Contract tests for type-specific customer behavior."""

from __future__ import annotations


def individual_payload(email: str = "jane@example.com") -> dict:
    return {
        "customer_type": "INDIVIDUAL",
        "display_name": "Jane Doe",
        "first_name": "Jane",
        "last_name": "Doe",
        "email": email,
    }


def business_payload(registration: str = "US-123456") -> dict:
    return {
        "customer_type": "BUSINESS",
        "display_name": "Acme",
        "legal_name": "Acme Corporation",
        "registration_number": registration,
    }


def create(client, auth_headers, payload: dict) -> dict:
    response = client.post(
        "/api/v1/customers",
        json=payload,
        headers=auth_headers("customer:manage"),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_individual_missing_required_fields_is_unprocessable(client, auth_headers) -> None:
    response = client.post(
        "/api/v1/customers",
        json={"customer_type": "INDIVIDUAL", "display_name": "Jane"},
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNPROCESSABLE_ENTITY"


def test_business_missing_required_fields_is_unprocessable(client, auth_headers) -> None:
    response = client.post(
        "/api/v1/customers",
        json={"customer_type": "BUSINESS", "display_name": "Acme"},
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNPROCESSABLE_ENTITY"


def test_business_registration_must_be_unique(client, auth_headers) -> None:
    create(client, auth_headers, business_payload())

    response = client.post(
        "/api/v1/customers",
        json=business_payload("us-123456"),
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_CUSTOMER"


def test_business_may_reuse_an_individual_email(client, auth_headers) -> None:
    create(client, auth_headers, individual_payload())
    payload = business_payload()
    payload["email"] = "jane@example.com"

    business = create(client, auth_headers, payload)

    assert business["email"] == "jane@example.com"
    assert business["customer_type"] == "BUSINESS"


def test_change_individual_to_business(client, auth_headers) -> None:
    customer = create(client, auth_headers, individual_payload())

    response = client.patch(
        f"/api/v1/customers/{customer['id']}",
        json={
            "version": 1,
            "customer_type": "BUSINESS",
            "legal_name": "Jane Consulting LLC",
            "registration_number": "US-999999",
        },
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["customer_type"] == "BUSINESS"
    assert body["legal_name"] == "Jane Consulting LLC"
    assert body["registration_number"] == "US-999999"
    assert body["first_name"] is None
    assert body["last_name"] is None


def test_change_individual_to_business_requires_fields(client, auth_headers) -> None:
    customer = create(client, auth_headers, individual_payload())

    response = client.patch(
        f"/api/v1/customers/{customer['id']}",
        json={"version": 1, "customer_type": "BUSINESS"},
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNPROCESSABLE_ENTITY"


def test_change_business_to_individual(client, auth_headers) -> None:
    customer = create(client, auth_headers, business_payload())

    response = client.patch(
        f"/api/v1/customers/{customer['id']}",
        json={
            "version": 1,
            "customer_type": "INDIVIDUAL",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
        },
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["customer_type"] == "INDIVIDUAL"
    assert body["first_name"] == "John"
    assert body["legal_name"] is None
    assert body["registration_number"] is None


def test_type_change_respects_type_scoped_uniqueness(client, auth_headers) -> None:
    create(client, auth_headers, business_payload("US-111111"))
    customer = create(client, auth_headers, individual_payload())

    response = client.patch(
        f"/api/v1/customers/{customer['id']}",
        json={
            "version": 1,
            "customer_type": "BUSINESS",
            "legal_name": "Duplicate Registration",
            "registration_number": "US-111111",
        },
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_CUSTOMER"
