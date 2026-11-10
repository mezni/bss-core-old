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