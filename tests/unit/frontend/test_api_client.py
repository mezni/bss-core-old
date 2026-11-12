"""Unit tests for the CustomerAPIClient error handling."""

from __future__ import annotations

import httpx
import pytest

from src.frontend.customer.api_client import CustomerAPIClient, CustomerAPIError


def test_network_failure_is_structured() -> None:
    """A transport-level error should raise CustomerAPIError with BACKEND_UNAVAILABLE."""
    def handler(request):
        raise httpx.ConnectError("refused", request=request)

    client = CustomerAPIClient(
        base_url="http://test",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(CustomerAPIError) as exc:
        client.list_customers()

    assert exc.value.code == "BACKEND_UNAVAILABLE"
    assert "Could not reach the backend" in exc.value.message


def test_flat_error_envelope_is_parsed() -> None:
    """The standardized flat envelope maps onto CustomerAPIError fields."""

    def handler(request):
        return httpx.Response(
            404,
            json={
                "error": "not_found",
                "message": "Customer C-999 not found.",
                "code": "CUSTOMER_NOT_FOUND",
            },
        )

    client = CustomerAPIClient(
        base_url="http://test",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(CustomerAPIError) as exc:
        client.get_customer("C-999")

    assert exc.value.code == "CUSTOMER_NOT_FOUND"
    assert exc.value.message == "Customer C-999 not found."
    assert exc.value.status_code == 404


def test_non_json_error_body_falls_back() -> None:
    """A non-JSON error body still raises a structured error."""

    def handler(request):
        return httpx.Response(500, text="Internal server error")

    client = CustomerAPIClient(
        base_url="http://test",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(CustomerAPIError) as exc:
        client.list_customers()

    assert exc.value.code == "API_ERROR"
    assert exc.value.status_code == 500