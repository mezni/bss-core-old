import pytest


@pytest.fixture(scope="session")
def db_session():
    """Session-scoped database fixture."""
    import sqlite3
    import os

    os.makedirs("db", exist_ok=True)
    conn = sqlite3.connect("db/bss_core.db")
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def db(db_session):
    """Function-scoped database fixture."""
    conn = db_session
    conn.execute("PRAGMA journal_mode=WAL")
    yield conn
    conn.rollback()
