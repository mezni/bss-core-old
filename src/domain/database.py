"""Database connection and session management for BSS Core.

Provides SQLAlchemy engine and session configuration designed per constitution
technology standards. Initially configured for SQLite, designed for evolution
to other databases (PostgreSQL, MySQL) per module needs.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# SQLite configuration - initial database per constitution technology standards
# Designed for evolution to other databases by changing the connection string
SQLALCHEMY_DATABASE_URL = "sqlite:///./db/bss_core.db"

# Engine configuration with connection pooling and thread safety
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

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
