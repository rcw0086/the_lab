"""Helper utilities for asserting database state in tests.

This module provides convenient assertion functions for verifying
database state without verbose query boilerplate.
"""

from typing import Any, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from the_lab.db.base import Base

T = TypeVar("T", bound=Base)


def assert_count(session: Session, model: Type[T], expected: int) -> None:
    """Assert that the count of records matches expected value.

    Args:
        session: Database session
        model: SQLAlchemy model class
        expected: Expected count

    Raises:
        AssertionError: If count doesn't match expected
    """
    actual = session.query(model).count()
    assert (
        actual == expected
    ), f"Expected {expected} {model.__name__} records, found {actual}"


def assert_exists(session: Session, model: Type[T], **filters: Any) -> T:
    """Assert that a record exists matching the given filters.

    Args:
        session: Database session
        model: SQLAlchemy model class
        **filters: Field=value filters

    Returns:
        The matching record

    Raises:
        AssertionError: If no record found or multiple records found
    """
    records = session.query(model).filter_by(**filters).all()

    if len(records) == 0:
        raise AssertionError(
            f"Expected to find {model.__name__} with {filters}, found none"
        )

    if len(records) > 1:
        raise AssertionError(
            f"Expected to find one {model.__name__} with {filters}, found {len(records)}"
        )

    return records[0]


def assert_not_exists(session: Session, model: Type[T], **filters: Any) -> None:
    """Assert that no record exists matching the given filters.

    Args:
        session: Database session
        model: SQLAlchemy model class
        **filters: Field=value filters

    Raises:
        AssertionError: If any matching record is found
    """
    count = session.query(model).filter_by(**filters).count()
    assert count == 0, f"Expected no {model.__name__} with {filters}, found {count}"


def assert_field_value(
    session: Session, model: Type[T], record_id: int, field: str, expected: Any
) -> None:
    """Assert that a specific field has the expected value.

    Args:
        session: Database session
        model: SQLAlchemy model class
        record_id: ID of the record to check
        field: Field name to check
        expected: Expected value

    Raises:
        AssertionError: If field value doesn't match expected
    """
    record = session.get(model, record_id)
    assert record is not None, f"{model.__name__} with id={record_id} not found"

    actual = getattr(record, field)
    assert (
        actual == expected
    ), f"Expected {model.__name__}.{field} to be {expected}, got {actual}"


def assert_relationship_count(
    session: Session, instance: Base, relationship: str, expected: int
) -> None:
    """Assert that a relationship has the expected number of related objects.

    Args:
        session: Database session
        instance: Model instance to check
        relationship: Relationship attribute name
        expected: Expected count of related objects

    Raises:
        AssertionError: If relationship count doesn't match expected
    """
    # Refresh to ensure relationships are loaded
    session.refresh(instance)

    related = getattr(instance, relationship)

    # Handle both list and query relationships
    if isinstance(related, list):
        actual = len(related)
    elif hasattr(related, "count"):
        actual = related.count()
    else:
        actual = len(related)

    assert (
        actual == expected
    ), f"Expected {expected} related {relationship}, found {actual}"


def assert_cascade_deleted(
    session: Session, model: Type[T], record_id: int
) -> None:
    """Assert that a record was cascade deleted.

    Args:
        session: Database session
        model: SQLAlchemy model class
        record_id: ID of the record that should be deleted

    Raises:
        AssertionError: If record still exists
    """
    # Expire all to ensure we get fresh data from the database
    session.expire_all()
    record = session.get(model, record_id)
    assert (
        record is None
    ), f"Expected {model.__name__} with id={record_id} to be deleted, but it exists"


def assert_unique_constraint_violated(exception: Exception) -> None:
    """Assert that an exception is a unique constraint violation.

    Args:
        exception: Exception to check

    Raises:
        AssertionError: If exception is not a unique constraint violation
    """
    from sqlalchemy.exc import IntegrityError

    assert isinstance(exception, IntegrityError), (
        f"Expected IntegrityError, got {type(exception).__name__}"
    )

    error_msg = str(exception.orig).lower()
    assert "unique" in error_msg or "duplicate" in error_msg, (
        f"Expected unique constraint violation, got: {exception.orig}"
    )


def assert_check_constraint_violated(exception: Exception) -> None:
    """Assert that an exception is a check constraint violation.

    Args:
        exception: Exception to check

    Raises:
        AssertionError: If exception is not a check constraint violation
    """
    from sqlalchemy.exc import IntegrityError

    assert isinstance(exception, IntegrityError), (
        f"Expected IntegrityError, got {type(exception).__name__}"
    )

    error_msg = str(exception.orig).lower()
    assert "check" in error_msg or "violates check constraint" in error_msg, (
        f"Expected check constraint violation, got: {exception.orig}"
    )


def assert_foreign_key_constraint_violated(exception: Exception) -> None:
    """Assert that an exception is a foreign key constraint violation.

    Args:
        exception: Exception to check

    Raises:
        AssertionError: If exception is not a foreign key constraint violation
    """
    from sqlalchemy.exc import IntegrityError

    assert isinstance(exception, IntegrityError), (
        f"Expected IntegrityError, got {type(exception).__name__}"
    )

    error_msg = str(exception.orig).lower()
    assert "foreign key" in error_msg or "fk_" in error_msg, (
        f"Expected foreign key constraint violation, got: {exception.orig}"
    )


def get_all(session: Session, model: Type[T]) -> list[T]:
    """Get all records for a model (convenience function).

    Args:
        session: Database session
        model: SQLAlchemy model class

    Returns:
        List of all records
    """
    return session.query(model).all()


def get_by_id(session: Session, model: Type[T], record_id: int) -> T | None:
    """Get a record by ID (convenience function).

    Args:
        session: Database session
        model: SQLAlchemy model class
        record_id: Record ID

    Returns:
        Record or None if not found
    """
    return session.get(model, record_id)


def refresh_and_get(session: Session, model: Type[T], record_id: int) -> T | None:
    """Get a record by ID and refresh it from database.

    Useful for verifying updates after commit.

    Args:
        session: Database session
        model: SQLAlchemy model class
        record_id: Record ID

    Returns:
        Refreshed record or None if not found
    """
    record = session.get(model, record_id)
    if record:
        session.refresh(record)
    return record
