"""Billing management DTOs."""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.entities import Invoice, InvoiceItem, Payment


@dataclass(frozen=True)
class InvoiceItemDTO:
    """Data transfer object for an invoice line item."""

    id: str
    description: str
    quantity: float
    unit_price: float
    line_total: float

    @staticmethod
    def from_domain(item: InvoiceItem) -> InvoiceItemDTO:
        return InvoiceItemDTO(
            id=item.id,
            description=item.description,
            quantity=item.quantity,
            unit_price=item.unit_price,
            line_total=item.line_total,
        )


@dataclass(frozen=True)
class InvoiceDTO:
    """Data transfer object for an invoice."""

    id: str
    invoice_number: str
    status: str
    total_amount: float
    reference_id: str
    order_id: str
    customer_id: str
    billing_date: str
    due_date: str
    payment_date: str | None
    payment_method: str | None
    version: int
    items: tuple[InvoiceItemDTO, ...] = ()

    @staticmethod
    def from_domain(invoice: Invoice) -> InvoiceDTO:
        return InvoiceDTO(
            id=invoice.id,
            invoice_number=str(invoice.invoice_number),
            status=invoice.status.value,
            total_amount=invoice.total_amount,
            reference_id=invoice.reference_id,
            order_id=invoice.order_id,
            customer_id=invoice.customer_id,
            billing_date=invoice.billing_date.isoformat(),
            due_date=invoice.due_date.isoformat(),
            payment_date=invoice.payment_date.isoformat() if invoice.payment_date else None,
            payment_method=invoice.payment_method,
            version=invoice.version,
            items=tuple(InvoiceItemDTO.from_domain(item) for item in invoice.items),
        )


@dataclass(frozen=True)
class PaymentDTO:
    """Data transfer object for a payment."""

    id: str
    invoice_id: str
    amount: float
    payment_method: str
    status: str
    transaction_id: str
    payment_date: str
    customer_id: str | None
    created_at: str

    @staticmethod
    def from_domain(payment: Payment) -> PaymentDTO:
        return PaymentDTO(
            id=payment.id,
            invoice_id=payment.invoice_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            status=payment.status.value,
            transaction_id=payment.transaction_id,
            payment_date=payment.payment_date.isoformat(),
            customer_id=payment.customer_id,
            created_at=payment.created_at.isoformat(),
        )
