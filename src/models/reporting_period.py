from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class ReportingPeriod(Base):
    __tablename__ = "reporting_period"

    period_name = Column(String(50), primary_key=True, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_custom = Column(Integer, nullable=False)  # 0=False, 1=True
    description = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<ReportingPeriod period_name={self.period_name}>"

    @property
    def is_custom_flag(self) -> bool:
        return self.is_custom == 1

    @is_custom_flag.setter
    def is_custom_flag(self, value: bool) -> None:
        self.is_custom = 1 if value else 0