"""Billing aggregate roots."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from .exceptions import (
    InvoiceConflictError,
    InvoiceValidationError,
    PaymentAmountError,
)
from .value_objects import (
    PAYMENT_METHODS,
    InvoiceNumber,
    InvoiceStatus,
    PaymentStatus,
)


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class InvoiceItem:
    """A single line item on an invoice."""

    id: str
    description: str
    quantity: float
    unit_price: float
    line_total: float
    created_at: datetime


class Invoice:
    """Represents a billing document for an order."""

    def __init__(
        self,
        id: str,
        invoice_number: InvoiceNumber,
        status: InvoiceStatus,
        total_amount: float,
        order_id: str,
        billing_date: datetime,
        due_date: datetime,
        customer_id: str,
        items: list[InvoiceItem] | None = None,
        payment_date: datetime | None = None,
        payment_method: str | None = None,
        version: int = 1,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.invoice_number = invoice_number
        self.status = status
        self.total_amount = total_amount
        self.order_id = order_id
        self.billing_date = billing_date
        self.due_date = due_date
        self.payment_date = payment_date
        self.payment_method = payment_method
        self.customer_id = customer_id
        self.items = items or []
        self.version = version
        self.created_at = created_at or _now()
        self.updated_at = updated_at or _now()

    @property
    def reference_id(self) -> str:
        """Alias used by the billing API contract for the order reference."""
        return self.order_id

    @classmethod
    def create(
        cls,
        invoice_number: InvoiceNumber,
        order_id: str,
        customer_id: str,
        total_amount: float,
        billing_date: datetime,
        due_date: datetime,
        items: list[InvoiceItem] | None = None,
    ) -> Invoice:
        """Create a new invoice in pending status."""
        if due_date <= billing_date:
            raise InvoiceValidationError("due_date must be after billing_date")
        if total_amount <= 0:
            raise InvoiceValidationError("total_amount must be positive")
        return cls(
            id=f"INV-{uuid4()}",
            invoice_number=invoice_number,
            status=InvoiceStatus.PENDING,
            total_amount=round(total_amount, 2),
            order_id=order_id,
            billing_date=billing_date,
            due_date=due_date,
            customer_id=customer_id,
            items=items,
        )

    def mark_paid(self, payment_method: str) -> None:
        """Mark the invoice as paid."""
        if self.status != InvoiceStatus.PENDING:
            raise InvoiceConflictError("Invoice is not in pending status")
        if payment_method not in PAYMENT_METHODS:
            raise PaymentAmountError("invalid payment method")
        self.status = InvoiceStatus.PAID
        self.payment_date = _now()
        self.payment_method = payment_method
        self.updated_at = _now()
        self.version += 1

    def is_terminal(self) -> bool:
        return self.status in (InvoiceStatus.PAID, InvoiceStatus.TERMINAL)

    def can_be_paid(self) -> bool:
        return self.status == InvoiceStatus.PENDING


class Payment:
    """Represents a payment record against an invoice."""

    def __init__(
        self,
        id: str,
        invoice_id: str,
        amount: float,
        payment_method: str,
        status: PaymentStatus,
        transaction_id: str,
        payment_date: datetime | None = None,
        customer_id: str | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        self.id = id
        self.invoice_id = invoice_id
        self.amount = amount
        self.payment_method = payment_method
        self.status = status
        self.transaction_id = transaction_id
        self.payment_date = payment_date or _now()
        self.customer_id = customer_id
        self.created_at = created_at or _now()
        self.updated_at = updated_at or _now()

    @classmethod
    def create(
        cls,
        invoice_id: str,
        amount: float,
        payment_method: str,
        customer_id: str | None = None,
        transaction_id: str | None = None,
    ) -> Payment:
        """Create a completed payment for an invoice."""
        if amount <= 0:
            raise PaymentAmountError("payment amount must be positive")
        if payment_method not in PAYMENT_METHODS:
            raise PaymentAmountError("invalid payment method")
        return cls(
            id=f"PAY-{uuid4()}",
            invoice_id=invoice_id,
            amount=round(amount, 2),
            payment_method=payment_method,
            status=PaymentStatus.COMPLETED,
            transaction_id=transaction_id or f"TXN-{uuid4()}",
            customer_id=customer_id,
        )

    def mark_completed(self) -> None:
        """Mark the payment as completed."""
        self.status = PaymentStatus.COMPLETED
        self.payment_date = _now()
        self.updated_at = _now()
