from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class DashboardMetric(Base):
    __tablename__ = "dashboard_metric"

    metric_name = Column(
        String(255), primary_key=True, nullable=False
    )
    value = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(50), nullable=False)
    aggregation_type = Column(String(20), nullable=False, default="count")
    date_range_start = Column(DateTime, nullable=False)
    date_range_end = Column(DateTime, nullable=False)
    reporting_period = Column(String(30), nullable=False, default="custom")
    category = Column(String(50), nullable=False)
    category_specific_id = Column(String(36), nullable=True)
    role_tier = Column(String(20), nullable=True)
    last_refreshed = Column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    created_at = Column(
        DateTime, nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    def __repr__(self) -> str:
        return f"<DashboardMetric metric_name={self.metric_name} category={self.category}>"