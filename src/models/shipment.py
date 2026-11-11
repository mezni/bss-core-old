from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, DateTime, UUID as SQLUUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ShipmentStatus:
    PENDING = "pending"
    IN_TRANSIT = "in-transit"
    DELIVERED = "delivered"
    EXCEPTION = "exception"


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    status = Column(
        String,
        nullable=False,
        default=ShipmentStatus.PENDING,
    )
    tracking_reference = Column(String, nullable=False)
    carrier_name = Column(String, nullable=True)
    order_id = Column(
        SQLUUID(as_uuid=True),
        nullable=False,
    )
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
    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )