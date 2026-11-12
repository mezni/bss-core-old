"""Domain exceptions for shipment management."""

from __future__ import annotations

from typing import Any


class ShipmentDomainError(Exception):
    """Base class for shipment domain errors with a stable error code."""

    code = "SHIPMENT_ERROR"
    http_status = 400

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ShipmentNotFound(ShipmentDomainError):
    code = "SHIPMENT_NOT_FOUND"
    http_status = 404


class OrderNotFound(ShipmentDomainError):
    code = "ORDER_NOT_FOUND"
    http_status = 404


class ShipmentValidationError(ShipmentDomainError):
    code = "SHIPMENT_VALIDATION_ERROR"
    http_status = 400


class ShipmentConflictError(ShipmentDomainError):
    """Invalid state transition or duplicate — e.g. shipment for a non-confirmed order."""

    code = "SHIPMENT_CONFLICT"
    http_status = 409


class ShipmentStaleUpdate(ShipmentDomainError):
    code = "STALE_UPDATE"
    http_status = 409

    def __init__(self, expected_version: int, current_version: int) -> None:
        self.expected_version = expected_version
        self.current_version = current_version
        super().__init__(
            "The shipment was modified by another request",
            {"expected_version": expected_version, "current_version": current_version},
        )


class InvalidTransition(ShipmentConflictError):
    code = "INVALID_TRANSITION"
    http_status = 409

    def __init__(self, from_status: str, to_status: str, reason: str | None = None) -> None:
        self.from_status = from_status
        self.to_status = to_status
        self.reason = reason or f"Invalid transition from {from_status} to {to_status}"
        super().__init__(self.reason)


class InvalidCarrierName(ShipmentValidationError):
    code = "INVALID_CARRIER_NAME"
    http_status = 400


class OrderNotConfirmed(ShipmentConflictError):
    code = "ORDER_NOT_CONFIRMED"
    http_status = 409
