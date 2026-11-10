"""initial migration

Revision ID: b7926efd4cf1
Revises: 
Create Date: 2026-11-10 10:36:19.126542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7926efd4cf1'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "customer",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("contact_info", sa.Text, nullable=True),
        sa.Column("eligibility_status", sa.Boolean, nullable=False, default=False),
    )
    op.create_table(
        "order",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("status", sa.Enum("draft", "confirmed", "shipped", "delivered", "cancelled", name="order_status"), nullable=False, default="draft"),
        sa.Column("subtotal", sa.Numeric(10, 2), nullable=False, default="0.00"),
        sa.Column("tax_amount", sa.Numeric(10, 2), nullable=False, default="0.00"),
        sa.Column("total", sa.Numeric(10, 2), nullable=False, default="0.00"),
        sa.Column("customer_id", sa.Integer, sa.ForeignKey("customer.id"), nullable=False),
    )
    op.create_table(
        "order_item",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("order.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("line_total", sa.Numeric(10, 2), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("order_item")
    op.drop_table("order")
    op.drop_table("customer")
