"""Database connection and session management for BSS Core.

Provides SQLAlchemy engine and session configuration designed per constitution
technology standards. Initially configured for SQLite, designed for evolution
to other databases (PostgreSQL, MySQL) per module needs.
"""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

# SQLite configuration - initial database per constitution technology standards.
# BSS_DATABASE_URL allows tests and migration checks to target a clean database.
SQLALCHEMY_DATABASE_URL = os.environ.get("BSS_DATABASE_URL", "sqlite:///./db/bss_core.db")

# Engine configuration with connection pooling and thread safety
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """Enforce referential integrity on SQLite (constitution Section 7)."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Session factory configured for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Dependency injection function that provides a database session.

    Yields a SQLAlchemy session that is automatically rolled back after use.
    Designed for use with FastAPI dependency injection.

    Returns:
        Session: A SQLAlchemy session instance
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Session:
    """Create a new database session.

    Returns:
        Session: A new SQLAlchemy session instance
    """
    return SessionLocal()
