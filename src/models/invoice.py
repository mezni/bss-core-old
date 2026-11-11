from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, UUID as SQLUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class InvoiceStatus:
    PENDING = "pending"
    PAID = "paid"
    TERMINAL = "terminal"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__('uuid').uuid4()),
        nullable=False,
    )
    invoice_number = Column(String, nullable=False)
    status = Column(String, nullable=False, default=InvoiceStatus.PENDING)
    total_amount = Column(
        Numeric(precision=10, scale=2),
        nullable=False,
    )
    reference_id = Column(SQLUUID(as_uuid=True), nullable=False)
    billing_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    due_date = Column(
        DateTime(timezone=True),
        nullable=False,
    )
    payment_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )
    payment_method = Column(String, nullable=True)
    customer_id = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )