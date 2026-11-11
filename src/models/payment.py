from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, UUID as SQLUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PaymentStatus:
    PENDING = "pending"
    COMPLETED = "completed"
    TERMINAL = "terminal"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__('uuid').uuid4()),
        nullable=False,
    )
    invoice_id = Column(SQLUUID(as_uuid=True), nullable=False)
    amount = Column(
        Numeric(precision=10, scale=2),
        nullable=False,
    )
    payment_method = Column(String, nullable=False)
    status = Column(String, nullable=False, default=PaymentStatus.PENDING)
    transaction_id = Column(String, nullable=True)
    payment_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )
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