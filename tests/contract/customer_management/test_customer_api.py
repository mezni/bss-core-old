"""Contract tests for customer lifecycle endpoints."""

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


def create_customer(client, auth_headers, payload=None):
    response = client.post(
        "/api/v1/customers",
        json=payload or individual_payload(),
        headers=auth_headers("customer:manage"),
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_and_get_customer(client, auth_headers) -> None:
    created = create_customer(client, auth_headers)

    assert created["status"] == "ACTIVE"
    assert created["version"] == 1
    assert created["eligible"] is False
    assert created["email"] == "jane@example.com"
    assert created["contacts"] == []
    assert created["addresses"] == []

    response = client.get(
        f"/api/v1/customers/{created['id']}", headers=auth_headers("customer:view")
    )
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_patch_increments_version(client, auth_headers) -> None:
    created = create_customer(client, auth_headers)

    response = client.patch(
        f"/api/v1/customers/{created['id']}",
        json={"version": 1, "display_name": "Jane A. Doe"},
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 200
    assert response.json()["display_name"] == "Jane A. Doe"
    assert response.json()["version"] == 2


def test_stale_patch_returns_conflict(client, auth_headers) -> None:
    created = create_customer(client, auth_headers)
    first = client.patch(
        f"/api/v1/customers/{created['id']}",
        json={"version": 1, "display_name": "First"},
        headers=auth_headers("customer:manage"),
    )
    assert first.status_code == 200

    stale = client.patch(
        f"/api/v1/customers/{created['id']}",
        json={"version": 1, "display_name": "Stale"},
        headers=auth_headers("customer:manage"),
    )

    assert stale.status_code == 409
    body = stale.json()
    assert body["code"] == "STALE_UPDATE"
    assert body["error"] == "stale_update"
    assert "current_version=2" in body["message"]


def test_deactivate_and_reactivate(client, auth_headers) -> None:
    created = create_customer(client, auth_headers)
    client.post(
        f"/api/v1/customers/{created['id']}/contacts",
        json={
            "name": "Jane",
            "contact_type": "EMAIL",
            "value": "jane@example.com",
            "is_primary": True,
        },
        headers=auth_headers("customer:manage"),
    )

    inactive = client.post(
        f"/api/v1/customers/{created['id']}/deactivate",
        headers=auth_headers("customer:manage"),
    )
    assert inactive.status_code == 200
    assert inactive.json()["status"] == "INACTIVE"
    assert len(inactive.json()["contacts"]) == 1

    active = client.post(
        f"/api/v1/customers/{created['id']}/reactivate",
        headers=auth_headers("customer:manage"),
    )
    assert active.status_code == 200
    assert active.json()["status"] == "ACTIVE"
    assert active.json()["version"] > inactive.json()["version"]


def test_duplicate_individual_email_returns_conflict(client, auth_headers) -> None:
    create_customer(client, auth_headers)

    response = client.post(
        "/api/v1/customers",
        json=individual_payload("JANE@example.com"),
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 409
    assert response.json()["code"] == "DUPLICATE_CUSTOMER"


def test_business_may_share_individual_email(client, auth_headers) -> None:
    create_customer(client, auth_headers)
    payload = business_payload()
    payload["email"] = "jane@example.com"

    response = client.post(
        "/api/v1/customers",
        json=payload,
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 201, response.text


def test_missing_customer_returns_not_found(client, auth_headers) -> None:
    response = client.get(
        "/api/v1/customers/missing", headers=auth_headers("customer:view")
    )

    assert response.status_code == 404
    assert response.json()["code"] == "CUSTOMER_NOT_FOUND"


def test_authorization_is_enforced(client, auth_headers) -> None:
    missing = client.get("/api/v1/customers")
    assert missing.status_code == 401
    assert missing.json()["code"] == "UNAUTHENTICATED"

    forbidden = client.get(
        "/api/v1/customers", headers=auth_headers("customer:manage")
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["code"] == "FORBIDDEN"

    forbidden_write = client.post(
        "/api/v1/customers",
        json=individual_payload(),
        headers=auth_headers("customer:view"),
    )
    assert forbidden_write.status_code == 403


def test_validation_errors_use_shared_envelope(client, auth_headers) -> None:
    response = client.post(
        "/api/v1/customers",
        json={"customer_type": "INDIVIDUAL", "display_name": "Jane", "unexpected": True},
        headers=auth_headers("customer:manage"),
    )

    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"
