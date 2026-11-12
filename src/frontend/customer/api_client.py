"""HTTP client for the customer management API.

The frontend talks to the backend exclusively through this client; it never
imports domain, application, or infrastructure code.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_BASE_URL = os.environ.get("BSS_API_URL", "http://localhost:8000")


class CustomerAPIError(Exception):
    """A structured error returned by the customer API."""

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        status_code: int | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class CustomerAPIClient:
    """Thin synchronous client over the customer REST endpoints."""

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.token = token if token is not None else os.environ.get("BSS_API_TOKEN", "")
        self._client = http_client or httpx.Client(timeout=10.0)

    def _headers(self) -> dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        try:
            response = self._client.request(
                method,
                f"{self.base_url}{path}",
                headers=self._headers(),
                **kwargs,
            )
        except httpx.RequestError as error:
            raise CustomerAPIError(
                code="BACKEND_UNAVAILABLE",
                message=f"Could not reach the backend at {self.base_url}.",
                details={"reason": str(error)},
            ) from error
        if response.status_code >= 400:
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            raise CustomerAPIError(
                code=payload.get("code", "API_ERROR"),
                message=payload.get("message", response.text),
                status_code=response.status_code,
            )
        return response

    def _json(self, method: str, path: str, **kwargs: Any) -> Any:
        response = self._request(method, path, **kwargs)
        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    def list_customers(
        self,
        *,
        q: str | None = None,
        customer_type: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if q:
            params["q"] = q
        if customer_type:
            params["customer_type"] = customer_type
        if status:
            params["status"] = status
        return self._json("GET", "/api/v1/customers", params=params)

    def get_customer(self, customer_id: str) -> dict[str, Any]:
        return self._json("GET", f"/api/v1/customers/{customer_id}")

    def create_customer(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", "/api/v1/customers", json=payload)

    def update_customer(self, customer_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json("PATCH", f"/api/v1/customers/{customer_id}", json=payload)

    def deactivate_customer(self, customer_id: str) -> dict[str, Any]:
        return self._json("POST", f"/api/v1/customers/{customer_id}/deactivate")

    def reactivate_customer(self, customer_id: str) -> dict[str, Any]:
        return self._json("POST", f"/api/v1/customers/{customer_id}/reactivate")

    def get_eligibility(self, customer_id: str) -> dict[str, Any]:
        return self._json("GET", f"/api/v1/customers/{customer_id}/eligibility")

    def add_contact(self, customer_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", f"/api/v1/customers/{customer_id}/contacts", json=payload)

    def update_contact(
        self, customer_id: str, contact_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self._json(
            "PATCH",
            f"/api/v1/customers/{customer_id}/contacts/{contact_id}",
            json=payload,
        )

    def remove_contact(self, customer_id: str, contact_id: str, version: int) -> None:
        self._json(
            "DELETE",
            f"/api/v1/customers/{customer_id}/contacts/{contact_id}",
            json={"version": version},
        )

    def add_address(self, customer_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._json("POST", f"/api/v1/customers/{customer_id}/addresses", json=payload)

    def update_address(
        self, customer_id: str, address_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        return self._json(
            "PATCH",
            f"/api/v1/customers/{customer_id}/addresses/{address_id}",
            json=payload,
        )

    def remove_address(self, customer_id: str, address_id: str, version: int) -> None:
        self._json(
            "DELETE",
            f"/api/v1/customers/{customer_id}/addresses/{address_id}",
            json={"version": version},
        )

    def close(self) -> None:
        self._client.close()
