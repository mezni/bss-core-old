"""Billing management application service.

Coordinates the order-to-invoice and invoice-to-payment workflows, wiring
persistence through repository ports and order lookups through the read port.
Emits ``order_to_invoice`` / ``invoice_to_payment`` workflow events (FR-008).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from src.infrastructure.logging import (
    log_workflow_completed,
    log_workflow_failed,
    log_workflow_started,
)

from ..domain.entities import Invoice, InvoiceItem, Payment
from ..domain.exceptions import (
    BillingDomainError,
    InvoiceAlreadyPaid,
    InvoiceConflictError,
    InvoiceNotFound,
    InvoiceValidationError,
    OrderNotFound,
    PaymentAmountError,
)
from ..domain.value_objects import InvoiceNumber, InvoiceStatus
from .dto import InvoiceDTO, PaymentDTO
from .ports import (
    InvoiceRepositoryPort,
    OrderReadPort,
    PaymentRepositoryPort,
)

INVOICE_WORKFLOW = "order_to_invoice"
PAYMENT_WORKFLOW = "invoice_to_payment"
INVOICE_MODULES = ["order_management", "billing_management"]
PAYMENT_MODULES = ["billing_management"]

DEFAULT_DUE_DAYS = 30


@dataclass
class BillingService:
    """Coordinates invoice and payment use cases."""

    invoices: InvoiceRepositoryPort
    payments: PaymentRepositoryPort
    orders: OrderReadPort

    def generate_invoice(self, order_id: str, due_days: int = DEFAULT_DUE_DAYS) -> InvoiceDTO:
        """Generate an invoice for a confirmed order."""
        log_workflow_started(
            INVOICE_WORKFLOW, step="generate_invoice", modules=INVOICE_MODULES
        )
        try:
            order = self.orders.get_order(order_id)
            if order is None:
                raise OrderNotFound(f"Order {order_id} was not found")
            if order.status != "confirmed":
                raise InvoiceConflictError(
                    "Invoice can only be generated for confirmed orders"
                )
            if self.invoices.get_by_order_id(order_id) is not None:
                raise InvoiceConflictError(
                    f"Order {order_id} already has an invoice"
                )
            if due_days <= 0:
                raise InvoiceValidationError("due_days must be positive")

            billing_date = datetime.now(UTC)
            due_date = billing_date + timedelta(days=due_days)
            sequence = self.invoices.count_for_date(billing_date) + 1
            items = [
                InvoiceItem(
                    id=f"INVIT-{uuid4()}",
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                    created_at=billing_date,
                )
                for item in order.items
            ]
            invoice = Invoice.create(
                invoice_number=InvoiceNumber.generate(billing_date, sequence),
                order_id=order.id,
                customer_id=order.customer_id,
                total_amount=order.total,
                billing_date=billing_date,
                due_date=due_date,
                items=items,
            )
            invoice = self.invoices.add(invoice)
        except BillingDomainError as error:
            log_workflow_failed(
                INVOICE_WORKFLOW,
                step="generate_invoice",
                error=error.message,
                modules=INVOICE_MODULES,
            )
            raise
        log_workflow_completed(
            INVOICE_WORKFLOW, step="generate_invoice", modules=INVOICE_MODULES
        )
        return InvoiceDTO.from_domain(invoice)

    def get_invoice(self, invoice_id: str) -> InvoiceDTO:
        """Get an invoice by ID."""
        return InvoiceDTO.from_domain(self._get_invoice(invoice_id))

    def list_invoices(
        self,
        customer_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[InvoiceDTO], int]:
        """List invoices with optional filters."""
        invoices, total = self.invoices.list(
            customer_id=customer_id, status=status, page=page, page_size=page_size
        )
        return [InvoiceDTO.from_domain(invoice) for invoice in invoices], total

    
    def list_payments(
        self,
        customer_id: str | None = None,
        invoice_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[PaymentDTO], int]:
        """List payments with optional filters."""
        payments, total = self.payments.list(
            customer_id=customer_id, invoice_id=invoice_id, status=status, page=page, page_size=page_size
        )
        return [PaymentDTO.from_domain(p) for p in payments], total
    def mark_invoice_paid(self, invoice_id: str, payment_method: str) -> InvoiceDTO:
        """Mark an invoice as paid (PATCH status transition)."""
        invoice = self._get_invoice(invoice_id)
        expected_version = invoice.version
        invoice.mark_paid(payment_method)
        invoice = self.invoices.update(invoice, expected_version=expected_version)
        return InvoiceDTO.from_domain(invoice)

    def process_payment(
        self,
        invoice_id: str,
        amount: float,
        payment_method: str,
        transaction_id: str | None = None,
    ) -> PaymentDTO:
        """Process a payment for a pending invoice and mark it paid."""
        log_workflow_started(
            PAYMENT_WORKFLOW, step="process_payment", modules=PAYMENT_MODULES
        )
        try:
            invoice = self.invoices.get(invoice_id)
            if invoice is None:
                raise InvoiceNotFound(f"Invoice {invoice_id} was not found")
            if invoice.status != InvoiceStatus.PENDING:
                raise InvoiceAlreadyPaid(
                    "Payment cannot be processed for a non-pending invoice"
                )
            if round(amount, 2) != round(invoice.total_amount, 2):
                raise PaymentAmountError(
                    "Payment amount must match the invoice total"
                )
            expected_version = invoice.version
            payment = Payment.create(
                invoice_id=invoice.id,
                amount=amount,
                payment_method=payment_method,
                customer_id=invoice.customer_id,
                transaction_id=transaction_id,
            )
            payment = self.payments.add(payment)
            invoice.mark_paid(payment_method)
            self.invoices.update(invoice, expected_version=expected_version)
        except BillingDomainError as error:
            log_workflow_failed(
                PAYMENT_WORKFLOW,
                step="process_payment",
                error=error.message,
                modules=PAYMENT_MODULES,
            )
            raise
        log_workflow_completed(
            PAYMENT_WORKFLOW, step="process_payment", modules=PAYMENT_MODULES
        )
        return PaymentDTO.from_domain(payment)

    def get_payment(self, payment_id: str) -> PaymentDTO:
        """Get a payment by ID."""
        payment = self.payments.get(payment_id)
        if payment is None:
            raise InvoiceNotFound(f"Payment {payment_id} was not found")
        return PaymentDTO.from_domain(payment)

    def _get_invoice(self, invoice_id: str) -> Invoice:
        invoice = self.invoices.get(invoice_id)
        if invoice is None:
            raise InvoiceNotFound(f"Invoice {invoice_id} was not found")
        return invoice
