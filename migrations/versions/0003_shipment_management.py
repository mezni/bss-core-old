"""Create shipment management tables.

Revision ID: 0003_shipment_management
Revises: 0002_order_management
Create Date: 2026-11-11
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_shipment_management"
down_revision = "0002_order_management"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "shipments",
        sa.Column("id", sa.String(length=41), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("tracking_reference", sa.String(length=40), nullable=False),
        sa.Column("carrier_name", sa.String(length=120), nullable=False),
        sa.Column("order_id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tracking_reference", name="uq_shipments_tracking_reference"),
    )
    op.create_index("ix_shipments_order", "shipments", ["order_id"])
    op.create_index("ix_shipments_status", "shipments", ["status"])


def downgrade() -> None:
    op.drop_index("ix_shipments_status", table_name="shipments")
    op.drop_index("ix_shipments_order", table_name="shipments")
    op.drop_table("shipments")