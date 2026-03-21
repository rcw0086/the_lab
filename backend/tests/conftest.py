"""Pytest configuration and shared fixtures for tests.

This module provides common fixtures used across test modules, including:
- Database session management with transaction rollback
- Test database initialization
- Common test data factories
- Settings override for testing
"""

import os

# Override settings to use test database BEFORE importing anything from the_lab
# (the_lab.db.__init__ triggers get_settings() at import time via session.py)
os.environ["POSTGRES_DB"] = "the_lab_test"
# Set JWT secret key for tests (required field as of security fix)
os.environ["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-characters-long-for-testing"
)

from collections.abc import Generator
from typing import Any

import pytest
from sqlalchemy import create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from the_lab.db.base import Base

from tests.test_settings import get_test_settings

test_settings = get_test_settings()


# Create test database engine
# Use NullPool for tests to avoid connection pool issues
test_engine: Engine = create_engine(
    test_settings.database_url,
    echo=test_settings.debug,
    poolclass=pool.NullPool,  # No connection pooling for tests
    connect_args={
        "connect_timeout": 10,
        "application_name": "the_lab_test",
    },
)

# Create test session factory
TestSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database() -> Generator[None, None, None]:
    """Set up test database schema once for entire test session.

    This fixture:
    - Creates all PostgreSQL enum types
    - Creates all tables at the start of test session
    - Drops all tables at the end of test session
    - Runs automatically for all test sessions

    Using session scope ensures schema is created once, not per test,
    which significantly improves test execution speed.
    """
    # Drop and recreate schema for clean state
    with test_engine.begin() as conn:
        conn.exec_driver_sql("DROP SCHEMA IF EXISTS public CASCADE")
        conn.exec_driver_sql("CREATE SCHEMA public")

    # Create PostgreSQL enum types
    # These must be created before tables that reference them
    # Note: SQLAlchemy converts Python enum class names to lowercase for type names
    # e.g., CycleTypes -> cycletypes, SetTypes -> settypes
    with test_engine.begin() as conn:
        conn.exec_driver_sql("""
            DO $$ BEGIN
                CREATE TYPE cycle_types AS ENUM ('microcycle', 'mesocycle', 'macrocycle');
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """)
        conn.exec_driver_sql("""
            DO $$ BEGIN
                CREATE TYPE quantity_units AS ENUM (
                    'repetitions', 'meters', 'feet', 'miles', 'kilometers', 'yards',
                    'seconds', 'minutes', 'hours'
                );
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """)
        conn.exec_driver_sql("""
            DO $$ BEGIN
                CREATE TYPE cadence_units AS ENUM (
                    'strokes_per_minute', 'steps_per_minute', 'revolutions_per_minute'
                );
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """)
        conn.exec_driver_sql("""
            DO $$ BEGIN
                CREATE TYPE sides AS ENUM ('right', 'left');
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """)
        conn.exec_driver_sql("""
            DO $$ BEGIN
                CREATE TYPE carry_styles AS ENUM (
                    'vest', 'suitcase_double', 'suitcase_single',
                    'carry_double', 'carry_single', 'front_rack', 'other'
                );
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """)
        conn.exec_driver_sql("""
            DO $$ BEGIN
                CREATE TYPE external_load_units AS ENUM (
                    'lbs', 'kilograms', 'bodyweight', 'percent_1rm'
                );
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """)
        conn.exec_driver_sql("""
            DO $$ BEGIN
                CREATE TYPE pace_units AS ENUM ('per_mile', 'per_kilometer', 'per_500m');
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """)
        conn.exec_driver_sql("""
            DO $$ BEGIN
                CREATE TYPE energy_units AS ENUM ('calories', 'watts');
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """)
        conn.exec_driver_sql("""
            DO $$ BEGIN
                CREATE TYPE set_types AS ENUM ('strength', 'endurance', 'other');
            EXCEPTION WHEN duplicate_object THEN null;
            END $$;
        """)

    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    yield

    # Clean up after all tests complete
    with test_engine.begin() as conn:
        conn.exec_driver_sql("DROP SCHEMA public CASCADE")
        conn.exec_driver_sql("CREATE SCHEMA public")


@pytest.fixture(scope="function")
def db_session(setup_test_database: None) -> Generator[Session, None, None]:
    """Provide a database session with automatic transaction rollback.

    This fixture:
    - Creates a new database connection
    - Begins a transaction
    - Creates a session bound to the transaction
    - Yields the session for use in tests
    - Rolls back the transaction after the test
    - Closes the connection

    This approach is MUCH faster than recreating tables for each test.
    Tests run in complete isolation - changes in one test never affect another.

    Usage:
        def test_something(db_session: Session):
            user = User(username="test", password_hash="$2b$12$testhashtesthashtesthashtesthashtesthashtesthashte")
            db_session.add(user)
            db_session.commit()
            # Changes are rolled back after test

    Yields:
        Session: Isolated database session
    """
    # Create a connection
    connection = test_engine.connect()

    # Begin a transaction
    transaction = connection.begin()

    # Create a session bound to the connection
    session = TestSessionLocal(bind=connection)

    # Begin a nested transaction (using SAVEPOINT)
    # This allows us to use session.commit() in tests
    # while still rolling back all changes after the test
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session: Session, transaction: Any) -> None:
        """Restart the savepoint after commit/rollback."""
        if transaction.nested and not transaction._parent.nested:
            # Expire all objects so they're reloaded on next access
            session.expire_all()
            connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        # Rollback the transaction
        if nested.is_active:
            nested.rollback()
        transaction.rollback()
        connection.close()


@pytest.fixture
def test_user(db_session: Session) -> Any:
    """Create a test user for use in tests.

    This is a convenience fixture that many tests need.
    Creates a user and returns it.

    Args:
        db_session: Database session fixture

    Returns:
        User instance
    """
    from the_lab.db.models.core import User

    user = User(username="test_user", password_hash="$2b$12$fakehashfortest000000000000000000000000000000000000000")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_settings() -> Any:
    """Provide test settings.

    Returns:
        TestSettings instance configured for testing
    """
    return get_test_settings()


# Import factory fixtures to make them available
pytest_plugins = []
