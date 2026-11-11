from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, UUID
from sqlalchemy.sql import func

from ._base import Base


class OrderStatus:
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    """Represents a customer's purchase request.

    Relationships:
    - One order can have associated shipments that track delivery progress
    - One order can have multiple shipments; each shipment belongs to exactly one order
    """

    __tablename__ = "orders"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(uuid4()),
        nullable=False,
    )
    status = Column(
        SQLEnum(OrderStatus, native_enum=False, create_type=True),
        nullable=False,
        default=OrderStatus.DRAFT,
    )
    customer_id = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


def uuid4():
    import uuid
    return uuid.uuid4()