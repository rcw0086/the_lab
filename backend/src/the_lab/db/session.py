"""Database session management and engine configuration.

This module provides:
- Database engine with connection pooling
- Session factory for creating database sessions
- FastAPI dependency for automatic session management
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine, event, pool
from sqlalchemy.orm import Session, sessionmaker

from the_lab.config import get_settings

settings = get_settings()


def _on_connect(dbapi_conn: Any, connection_record: Any) -> None:
    """Set up connection-level settings.

    This hook is called when a new database connection is established.
    Useful for setting connection-level parameters like timeouts.

    Example usage:
        cursor = dbapi_conn.cursor()
        cursor.execute("SET statement_timeout = 30000")
        cursor.close()
    """
    pass


# Create database engine with connection pooling
# QueuePool is the default and provides a fixed-size pool of connections
engine: Engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log all SQL statements when debug=True
    pool_pre_ping=True,  # Verify connections before using them
    poolclass=pool.QueuePool,
    pool_size=5,  # Number of permanent connections
    max_overflow=10,  # Number of temporary connections when pool is full
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
        "application_name": "the_lab",  # Identify connections in pg_stat_activity
    },
)

# Register connection event listener
event.listen(engine, "connect", _on_connect)

# Create session factory
# Sessions should be created per-request and disposed after the request completes
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # Don't expire objects after commit
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that provides a database session.

    Yields a SQLAlchemy session and ensures it's properly closed after use.
    Use this as a dependency in FastAPI route handlers.

    Example:
        @app.get("/users/{user_id}")
        def get_user(user_id: int, db: Session = Depends(get_db)):
            return db.get(User, user_id)

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
