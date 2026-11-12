"""Ports for the billing management application module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from ..domain.entities import Invoice, Payment


@dataclass(frozen=True)
class OrderItemSummary:
    """Order line item as required for invoice generation."""

    description: str
    quantity: float
    unit_price: float
    line_total: float


@dataclass(frozen=True)
class OrderSummary:
    """Read-only order projection required by the billing module."""

    id: str
    status: str
    customer_id: str
    total: float
    items: tuple[OrderItemSummary, ...]


class OrderReadPort(Protocol):
    """Read-only order contract for invoice generation."""

    def get_order(self, order_id: str) -> OrderSummary | None:
        """Return an order projection, or ``None`` when it does not exist."""
        ...


class InvoiceRepositoryPort(Protocol):
    """Persistence boundary for the invoice aggregate."""

    def get(self, invoice_id: str) -> Invoice | None:
        """Return an invoice aggregate or ``None``."""
        ...

    def get_by_order_id(self, order_id: str) -> Invoice | None:
        """Return the invoice for an order, if any."""
        ...

    def add(self, invoice: Invoice) -> Invoice:
        """Persist a new invoice aggregate."""
        ...

    def update(self, invoice: Invoice, expected_version: int) -> Invoice:
        """Persist changes when ``expected_version`` matches the stored version."""
        ...

    def list(
        self,
        customer_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Invoice], int]:
        """Return a page of invoices and the total count."""
        ...

    def count_for_date(self, billing_date) -> int:
        """Return the number of invoices generated on a given date."""
        ...


class PaymentRepositoryPort(Protocol):
    """Persistence boundary for the payment aggregate."""

    def get(self, payment_id: str) -> Payment | None:
        """Return a payment aggregate or ``None``."""
        ...

    def add(self, payment: Payment) -> Payment:
        """Persist a new payment aggregate."""
        ...

    def list(self, invoice_id: str | None = None) -> list[Payment]:
        """Return payments, optionally filtered by invoice."""
        ...
