from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Column,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


ORDER_STATUS_CHOICES = ("draft", "confirmed", "shipped", "delivered", "cancelled")


class Order(Base):
    """Represents a customer's purchase request."""

    __tablename__ = "order"

    id = Column(
        String(36), primary_key=True, unique=True, nullable=False,
        default=lambda: f"ORD-{str(uuid.uuid4())}"
    )  # UUID v4 format ORD-...
    status = Column(
        SqlEnum("draft", "confirmed", "shipped", "delivered", "cancelled", name="order_status"),
        nullable=False,
        default="draft",
    )
    subtotal = Column(Numeric(10, 2), nullable=False, default="0.00")
    tax_amount = Column(Numeric(10, 2), nullable=False, default="0.00")
    total = Column(Numeric(10, 2), nullable=False, default="0.00")
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Order id={self.id} status={self.status}>"


class OrderItem(Base):
    """Represents a line item within an order."""

    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True)
    order_id = Column(String(36), ForeignKey("order.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(10, 2), nullable=False)

    def __repr__(self) -> str:
        return f"<OrderItem id={self.id} description={self.description}>"


class Customer(Base):
    """Represents an individual or business customer."""

    __tablename__ = "customer"

    id = Column(Integer, primary_key=True)
    type = Column(String(20), nullable=False)
    contact_info = Column(Text, nullable=True)
    eligibility_status = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Customer id={self.id} type={self.type}>"