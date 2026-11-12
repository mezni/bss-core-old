"""Smoke test for the e2e fixture stack (T012).

Verifies the TestClient app fixture, JWT minting helpers, and the
standardized error envelope using the customer module's existing
bearer-token enforcement.
"""

from __future__ import annotations


def test_unauthenticated_request_uses_standard_envelope(client) -> None:
    response = client.get("/api/v1/customers")

    assert response.status_code == 401
    body = response.json()
    assert body["code"] == "UNAUTHENTICATED"
    assert body["error"] == "unauthenticated"
    assert body["message"]


def test_missing_permission_is_forbidden(client, view_headers) -> None:
    response = client.get("/api/v1/customers", headers=view_headers)

    assert response.status_code == 403
    body = response.json()
    assert body["code"] == "FORBIDDEN"
    assert body["error"] == "forbidden"
    assert body["message"]
