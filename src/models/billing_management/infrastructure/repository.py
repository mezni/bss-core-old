"""SQLAlchemy implementations of the billing repository ports."""

from __future__ import annotations

from datetime import datetime, time

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..domain.entities import Invoice, InvoiceItem, Payment
from ..domain.exceptions import InvoiceNotFound, StaleUpdate
from ..domain.value_objects import InvoiceNumber, InvoiceStatus, PaymentStatus
from .orm import InvoiceItemORM, InvoiceORM, PaymentORM


class InvoiceRepository:
    """Persist invoice aggregates in SQLAlchemy-backed tables."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, invoice_id: str) -> Invoice | None:
        orm = self.session.get(InvoiceORM, invoice_id)
        return self._to_domain(orm) if orm is not None else None

    def get_by_order_id(self, order_id: str) -> Invoice | None:
        orm = self.session.scalar(
            select(InvoiceORM).where(InvoiceORM.order_id == order_id)
        )
        return self._to_domain(orm) if orm is not None else None

    def add(self, invoice: Invoice) -> Invoice:
        self.session.add(self._to_orm(invoice))
        self.session.commit()
        return invoice

    def update(self, invoice: Invoice, expected_version: int) -> Invoice:
        orm = self.session.get(InvoiceORM, invoice.id)
        if orm is None:
            raise InvoiceNotFound(f"Invoice {invoice.id} was not found")
        if orm.version != expected_version:
            raise StaleUpdate(expected_version, orm.version)
        orm.status = invoice.status.value
        orm.payment_date = invoice.payment_date
        orm.payment_method = invoice.payment_method
        orm.updated_at = invoice.updated_at
        orm.version = invoice.version
        self.session.commit()
        return invoice

    def list(
        self,
        customer_id: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Invoice], int]:
        filters = []
        if customer_id:
            filters.append(InvoiceORM.customer_id == customer_id)
        if status:
            filters.append(InvoiceORM.status == status)

        count_query = select(func.count()).select_from(InvoiceORM)
        query = select(InvoiceORM)
        for condition in filters:
            count_query = count_query.where(condition)
            query = query.where(condition)

        total = self.session.scalar(count_query) or 0
        query = (
            query.order_by(InvoiceORM.billing_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        invoices = [self._to_domain(orm) for orm in self.session.scalars(query)]
        return invoices, total

    def count_for_date(self, billing_date: datetime) -> int:
        start = datetime.combine(billing_date.date(), time.min, tzinfo=billing_date.tzinfo)
        end = datetime.combine(billing_date.date(), time.max, tzinfo=billing_date.tzinfo)
        return (
            self.session.scalar(
                select(func.count())
                .select_from(InvoiceORM)
                .where(InvoiceORM.billing_date >= start)
                .where(InvoiceORM.billing_date <= end)
            )
            or 0
        )

    def _to_orm(self, invoice: Invoice) -> InvoiceORM:
        return InvoiceORM(
            id=invoice.id,
            invoice_number=str(invoice.invoice_number),
            status=invoice.status.value,
            total_amount=invoice.total_amount,
            customer_id=invoice.customer_id,
            order_id=invoice.order_id,
            billing_date=invoice.billing_date,
            due_date=invoice.due_date,
            payment_date=invoice.payment_date,
            payment_method=invoice.payment_method,
            created_at=invoice.created_at,
            updated_at=invoice.updated_at,
            version=invoice.version,
            items=[
                InvoiceItemORM(
                    id=item.id,
                    invoice_id=invoice.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                    created_at=item.created_at,
                )
                for item in invoice.items
            ],
        )

    def _to_domain(self, orm: InvoiceORM) -> Invoice:
        return Invoice(
            id=orm.id,
            invoice_number=InvoiceNumber(orm.invoice_number),
            status=InvoiceStatus(orm.status),
            total_amount=float(orm.total_amount),
            order_id=orm.order_id,
            billing_date=orm.billing_date,
            due_date=orm.due_date,
            customer_id=orm.customer_id,
            items=[
                InvoiceItem(
                    id=item.id,
                    description=item.description,
                    quantity=float(item.quantity),
                    unit_price=float(item.unit_price),
                    line_total=float(item.line_total),
                    created_at=item.created_at,
                )
                for item in orm.items
            ],
            payment_date=orm.payment_date,
            payment_method=orm.payment_method,
            version=orm.version,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )


class PaymentRepository:
    """Persist payment aggregates in SQLAlchemy-backed tables."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, payment_id: str) -> Payment | None:
        orm = self.session.get(PaymentORM, payment_id)
        return self._to_domain(orm) if orm is not None else None

    def add(self, payment: Payment) -> Payment:
        self.session.add(self._to_orm(payment))
        self.session.commit()
        return payment

    def list(self, invoice_id: str | None = None) -> list[Payment]:
        query = select(PaymentORM)
        if invoice_id:
            query = query.where(PaymentORM.invoice_id == invoice_id)
        return [self._to_domain(orm) for orm in self.session.scalars(query)]

    def _to_orm(self, payment: Payment) -> PaymentORM:
        return PaymentORM(
            id=payment.id,
            invoice_id=payment.invoice_id,
            amount=payment.amount,
            payment_method=payment.payment_method,
            transaction_id=payment.transaction_id,
            status=payment.status.value,
            payment_date=payment.payment_date,
            customer_id=payment.customer_id,
            created_at=payment.created_at,
            updated_at=payment.updated_at,
        )

    def _to_domain(self, orm: PaymentORM) -> Payment:
        return Payment(
            id=orm.id,
            invoice_id=orm.invoice_id,
            amount=float(orm.amount),
            payment_method=orm.payment_method,
            status=PaymentStatus(orm.status),
            transaction_id=orm.transaction_id,
            payment_date=orm.payment_date,
            customer_id=orm.customer_id,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )
