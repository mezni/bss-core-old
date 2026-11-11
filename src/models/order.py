from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, DateTime, UUID as SQLUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OrderStatus:
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id = Column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    status = Column(
        String,
        nullable=False,
        default=OrderStatus.DRAFT,
    )
    customer_id = Column(String, nullable=False)
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