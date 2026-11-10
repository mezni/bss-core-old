"""SQLAlchemy ORM models for customer management."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base shared by all customer management tables."""


class CustomerORM(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    customer_type: Mapped[str] = mapped_column(String(20), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ACTIVE")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    contacts: Mapped[list[ContactORM]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ContactORM.created_at",
    )
    addresses: Mapped[list[AddressORM]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="AddressORM.created_at",
    )

    __table_args__ = (
        Index("ix_customers_type_status", "customer_type", "status"),
        Index("ix_customers_display_name", "display_name"),
        Index("ix_customers_email", "email"),
        Index("ix_customers_registration_number", "registration_number"),
        Index(
            "uq_customers_individual_email",
            "email",
            unique=True,
            sqlite_where=text("customer_type = 'INDIVIDUAL'"),
        ),
        Index(
            "uq_customers_business_registration",
            "registration_number",
            unique=True,
            sqlite_where=text("customer_type = 'BUSINESS'"),
        ),
    )


class ContactORM(Base):
    __tablename__ = "customer_contacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    contact_type: Mapped[str] = mapped_column(String(20), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    customer: Mapped[CustomerORM] = relationship(back_populates="contacts")

    __table_args__ = (
        Index("ix_customer_contacts_customer", "customer_id"),
        Index(
            "uq_customer_contacts_primary",
            "customer_id",
            unique=True,
            sqlite_where=text("is_primary = 1"),
        ),
    )


class AddressORM(Base):
    __tablename__ = "customer_addresses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    customer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("customers.id", ondelete="CASCADE"), nullable=False
    )
    label: Mapped[str | None] = mapped_column(String(80), nullable=True)
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(32), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    customer: Mapped[CustomerORM] = relationship(back_populates="addresses")

    __table_args__ = (
        Index("ix_customer_addresses_customer", "customer_id"),
        Index(
            "uq_customer_addresses_primary",
            "customer_id",
            unique=True,
            sqlite_where=text("is_primary = 1"),
        ),
    )
