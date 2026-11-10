"""Domain exceptions for order management."""

from __future__ import annotations

from typing import Any


class OrderDomainError(Exception):
    """Base class for order domain errors with a stable error code."""

    code = "ORDER_ERROR"
    http_status = 400

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class InvalidOrder(OrderDomainError):
    code = "INVALID_ORDER"
    http_status = 400


class OrderNotFound(OrderDomainError):
    code = "ORDER_NOT_FOUND"
    http_status = 404


class OrderItemError(OrderDomainError):
    code = "ORDER_ITEM_ERROR"
    http_status = 400


class DuplicateItem(OrderDomainError):
    code = "DUPLICATE_ITEM"
    http_status = 409


class StaleUpdate(OrderDomainError):
    code = "STALE_UPDATE"
    http_status = 409

    def __init__(self, expected_version: int, current_version: int) -> None:
        self.expected_version = expected_version
        self.current_version = current_version
        super().__init__(
            "The order was modified by another request",
            {"expected_version": expected_version, "current_version": current_version},
        )


class InvalidTransition(OrderDomainError):
    code = "INVALID_TRANSITION"
    http_status = 409

    def __init__(self, from_status: str, to_status: str, reason: str | None = None) -> None:
        self.from_status = from_status
        self.to_status = to_status
        self.reason = reason or f"Invalid transition from {from_status} to {to_status}"
        super().__init__(self.reason)


class ItemPrerequisiteError(OrderDomainError):
    code = "ITEM_PREREQUISITE_ERROR"
    http_status = 409

    def __init__(self, message: str) -> None:
        super().__init__(message)
