"""Contract tests for customer search, filter, and pagination parameters."""

from __future__ import annotations


def seed_customers(client, auth_headers) -> list[dict]:
    created = []
    for index in range(25):
        if index % 2 == 0:
            payload = {
                "customer_type": "INDIVIDUAL",
                "display_name": f"Individual {index:02d}",
                "first_name": "Jane",
                "last_name": f"Person{index:02d}",
                "email": f"jane{index:02d}@example.com",
            }
        else:
            payload = {
                "customer_type": "BUSINESS",
                "display_name": f"Business {index:02d}",
                "legal_name": f"Business {index:02d} LLC",
                "registration_number": f"US-{index:06d}",
            }
        response = client.post(
            "/api/v1/customers",
            json=payload,
            headers=auth_headers("customer:manage"),
        )
        assert response.status_code == 201, response.text
        created.append(response.json())
    return created


def test_search_and_filters(client, auth_headers) -> None:
    seed_customers(client, auth_headers)
    headers = auth_headers("customer:view")

    search = client.get("/api/v1/customers?q=Individual 04", headers=headers)
    assert search.status_code == 200
    assert search.json()["total"] == 1

    by_email = client.get("/api/v1/customers?q=jane12@example.com", headers=headers)
    assert by_email.json()["total"] == 1

    individuals = client.get(
        "/api/v1/customers?customer_type=INDIVIDUAL", headers=headers
    )
    businesses = client.get(
        "/api/v1/customers?customer_type=BUSINESS", headers=headers
    )
    assert individuals.json()["total"] == 13
    assert businesses.json()["total"] == 12


def test_status_filter(client, auth_headers) -> None:
    created = seed_customers(client, auth_headers)
    client.post(
        f"/api/v1/customers/{created[0]['id']}/deactivate",
        headers=auth_headers("customer:manage"),
    )

    headers = auth_headers("customer:view")
    inactive = client.get("/api/v1/customers?status=INACTIVE", headers=headers)
    active = client.get("/api/v1/customers?status=ACTIVE", headers=headers)

    assert inactive.json()["total"] == 1
    assert active.json()["total"] == 24


def test_pagination(client, auth_headers) -> None:
    seed_customers(client, auth_headers)
    headers = auth_headers("customer:view")

    first = client.get("/api/v1/customers?page=1&page_size=10", headers=headers)
    second = client.get("/api/v1/customers?page=2&page_size=10", headers=headers)

    assert first.json()["total"] == 25
    assert len(first.json()["items"]) == 10
    assert len(second.json()["items"]) == 10
    assert {item["id"] for item in first.json()["items"]}.isdisjoint(
        {item["id"] for item in second.json()["items"]}
    )


def test_empty_result_returns_empty_items(client, auth_headers) -> None:
    response = client.get(
        "/api/v1/customers?q=no-such-customer",
        headers=auth_headers("customer:view"),
    )

    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0


def test_invalid_pagination_parameters_are_rejected(client, auth_headers) -> None:
    headers = auth_headers("customer:view")

    page = client.get("/api/v1/customers?page=0", headers=headers)
    page_size = client.get("/api/v1/customers?page_size=101", headers=headers)

    assert page.status_code == 400
    assert page.json()["code"] == "VALIDATION_ERROR"
    assert page_size.status_code == 400
