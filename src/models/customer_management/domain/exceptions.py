"""Domain exceptions for customer management."""

from __future__ import annotations

from typing import Any


class CustomerDomainError(Exception):
    """Base class for customer domain errors with a stable error code."""

    code = "CUSTOMER_ERROR"
    http_status = 400

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class CustomerNotFound(CustomerDomainError):
    code = "CUSTOMER_NOT_FOUND"
    http_status = 404


class ContactNotFound(CustomerDomainError):
    code = "CONTACT_NOT_FOUND"
    http_status = 404


class AddressNotFound(CustomerDomainError):
    code = "ADDRESS_NOT_FOUND"
    http_status = 404


class DuplicateCustomer(CustomerDomainError):
    code = "DUPLICATE_CUSTOMER"
    http_status = 409


class DuplicatePrimary(CustomerDomainError):
    code = "DUPLICATE_PRIMARY"
    http_status = 409


class DuplicatePrimaryContact(DuplicatePrimary):
    code = "DUPLICATE_PRIMARY_CONTACT"


class DuplicatePrimaryAddress(DuplicatePrimary):
    code = "DUPLICATE_PRIMARY_ADDRESS"


class StaleUpdate(CustomerDomainError):
    code = "STALE_UPDATE"
    http_status = 409

    def __init__(self, expected_version: int, current_version: int) -> None:
        self.expected_version = expected_version
        self.current_version = current_version
        super().__init__(
            "The customer was modified by another request",
            {"expected_version": expected_version, "current_version": current_version},
        )


class InvalidCustomer(CustomerDomainError):
    code = "UNPROCESSABLE_ENTITY"
    http_status = 422
