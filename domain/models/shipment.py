from datetime import datetime, timezone
import uuid

from sqlalchemy import Column, String, DateTime, UUID as SQLUUID

from ._base import Base


class ShipmentStatus(Enum):
    PENDING = "pending"
    IN_TRANSIT = "in-transit"
    DELIVERED = "delivered"
    EXCEPTION = "exception"


class Shipment(Base):
    """Represents a delivery request for an order.

    Key attributes:
    - Unique identifier (UUID v4 format: SHIP-550e8400-e29b-41d4-a716-446655440000)
    - Status lifecycle: pending → in-transit → delivered (terminal)
    - Tracking reference generated on creation
    - Carrier name required for pending status
    - Associated with a confirmed order via order_id foreign key
    """

    __tablename__ = "shipments"

    id = Column(
        SQLUUID(as_uuid=True),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    status = Column(
        SQLEnum(
            ShipmentStatus,
            native_enum=False,
            create_type=True,
        ),
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