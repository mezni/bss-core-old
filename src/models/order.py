from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Numeric, UUID as SQLUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OrderStatus:
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    BILLABLE = "billable"


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(__import__('uuid').uuid4()),
        nullable=False,
    )
    status = Column(String, nullable=False, default=OrderStatus.DRAFT)
    customer_id = Column(String, nullable=False)
    total_amount = Column(
        Numeric(precision=10, scale=2),
        nullable=False,
    )
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