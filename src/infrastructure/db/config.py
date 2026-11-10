from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.domain.models import Base

DATABASE_URL = "sqlite:///./src/infrastructure/db/orders.db"

engine: Engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False)


get_db = lambda: SessionLocal()  # noqa: E731


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)