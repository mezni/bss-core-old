"""Create customer management tables.

Revision ID: 0001_customer_management
Revises:
Create Date: 2026-11-09
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_customer_management"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("customer_type", sa.String(length=20), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=120), nullable=True),
        sa.Column("last_name", sa.String(length=120), nullable=True),
        sa.Column("legal_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("registration_number", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="ACTIVE"),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_type_status", "customers", ["customer_type", "status"])
    op.create_index("ix_customers_display_name", "customers", ["display_name"])
    op.create_index("ix_customers_email", "customers", ["email"])
    op.create_index(
        "ix_customers_registration_number", "customers", ["registration_number"]
    )
    op.create_index(
        "uq_customers_individual_email",
        "customers",
        ["email"],
        unique=True,
        sqlite_where=sa.text("customer_type = 'INDIVIDUAL'"),
    )
    op.create_index(
        "uq_customers_business_registration",
        "customers",
        ["registration_number"],
        unique=True,
        sqlite_where=sa.text("customer_type = 'BUSINESS'"),
    )

    op.create_table(
        "customer_contacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("contact_type", sa.String(length=20), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_customer_contacts_customer", "customer_contacts", ["customer_id"]
    )
    op.create_index(
        "uq_customer_contacts_primary",
        "customer_contacts",
        ["customer_id"],
        unique=True,
        sqlite_where=sa.text("is_primary = 1"),
    )

    op.create_table(
        "customer_addresses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("label", sa.String(length=80), nullable=True),
        sa.Column("line1", sa.String(length=255), nullable=False),
        sa.Column("line2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=120), nullable=False),
        sa.Column("region", sa.String(length=120), nullable=True),
        sa.Column("postal_code", sa.String(length=32), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_customer_addresses_customer", "customer_addresses", ["customer_id"]
    )
    op.create_index(
        "uq_customer_addresses_primary",
        "customer_addresses",
        ["customer_id"],
        unique=True,
        sqlite_where=sa.text("is_primary = 1"),
    )


def downgrade() -> None:
    op.drop_index("uq_customer_addresses_primary", table_name="customer_addresses")
    op.drop_index("ix_customer_addresses_customer", table_name="customer_addresses")
    op.drop_table("customer_addresses")

    op.drop_index("uq_customer_contacts_primary", table_name="customer_contacts")
    op.drop_index("ix_customer_contacts_customer", table_name="customer_contacts")
    op.drop_table("customer_contacts")

    op.drop_index("uq_customers_business_registration", table_name="customers")
    op.drop_index("uq_customers_individual_email", table_name="customers")
    op.drop_index("ix_customers_registration_number", table_name="customers")
    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_index("ix_customers_display_name", table_name="customers")
    op.drop_index("ix_customers_type_status", table_name="customers")
    op.drop_table("customers")
