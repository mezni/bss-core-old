"""SQLAlchemy ORM models for shipment management."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base shared by all shipment management tables."""


class ShipmentORM(Base):
    __tablename__ = "shipments"

    id: Mapped[str] = mapped_column(String(41), primary_key=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    tracking_reference: Mapped[str] = mapped_column(
        String(40), unique=True, nullable=False
    )
    carrier_name: Mapped[str] = mapped_column(String(120), nullable=False)
    order_id: Mapped[str] = mapped_column(String(36), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index("ix_shipments_order", "order_id"),
        Index("ix_shipments_status", "status"),
    )