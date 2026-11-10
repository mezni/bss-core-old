"""SQLAlchemy ORM models for order management."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base shared by all order management tables."""


class OrderItemORM(Base):
    __tablename__ = "order_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[float] = mapped_column(nullable=False)
    unit_price: Mapped[float] = mapped_column(nullable=False)
    line_total: Mapped[float] = mapped_column(nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    order: Mapped[OrderORM] = relationship(back_populates="items")

    __table_args__ = (Index("ix_order_items_order", "order_id"),)


class OrderORM(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0.0)
    customer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    items: Mapped[list[OrderItemORM]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="OrderItemORM.created_at",
    )

    __table_args__ = (
        Index("ix_orders_status", "status"),
        Index("ix_orders_customer", "customer_id"),
        Index("ix_orders_version", "version"),
    )
