"""Create dashboard reporting tables.

Revision ID: 0005_dashboard_reporting
Revises: 0004_billing_management
Create Date: 2026-11-11
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0005_dashboard_reporting"
down_revision = "0004_billing_management"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dashboard_metric",
        sa.Column("metric_name", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("aggregation_type", sa.String(length=20), nullable=False),
        sa.Column("date_range_start", sa.DateTime(), nullable=False),
        sa.Column("date_range_end", sa.DateTime(), nullable=False),
        sa.Column("reporting_period", sa.String(length=30), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("category_specific_id", sa.String(length=36), nullable=True),
        sa.Column("role_tier", sa.String(length=20), nullable=True),
        sa.Column("last_refreshed", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("metric_name"),
    )

    op.create_table(
        "reporting_period",
        sa.Column("period_name", sa.String(length=50), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("is_custom", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("period_name"),
    )


def downgrade() -> None:
    op.drop_table("reporting_period")
    op.drop_table("dashboard_metric")
