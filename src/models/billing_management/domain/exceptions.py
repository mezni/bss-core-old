"""Domain exceptions for billing management."""

from __future__ import annotations

from typing import Any


class BillingDomainError(Exception):
    """Base class for billing domain errors with a stable error code."""

    code = "BILLING_ERROR"
    http_status = 400

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class InvoiceNotFound(BillingDomainError):
    code = "INVOICE_NOT_FOUND"
    http_status = 404


class OrderNotFound(BillingDomainError):
    code = "ORDER_NOT_FOUND"
    http_status = 404


class InvoiceValidationError(BillingDomainError):
    code = "INVOICE_VALIDATION_ERROR"
    http_status = 400


class InvoiceConflictError(BillingDomainError):
    """Duplicate invoice generation or invoice for a non-confirmed order."""

    code = "INVOICE_CONFLICT"
    http_status = 409


class InvoiceAlreadyPaid(BillingDomainError):
    """Payment attempt against an already-paid invoice."""

    code = "INVOICE_ALREADY_PAID"
    http_status = 409


class PaymentAmountError(BillingDomainError):
    """Payment amount does not match the invoice's outstanding balance."""

    code = "PAYMENT_AMOUNT_MISMATCH"
    http_status = 400


class StaleUpdate(BillingDomainError):
    code = "STALE_UPDATE"
    http_status = 409

    def __init__(self, expected_version: int, current_version: int) -> None:
        self.expected_version = expected_version
        self.current_version = current_version
        super().__init__(
            "The invoice was modified by another request",
            {"expected_version": expected_version, "current_version": current_version},
        )