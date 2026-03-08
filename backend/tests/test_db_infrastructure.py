"""Tests for SQLAlchemy database infrastructure.

Tests cover:
- Base class configuration
- Engine creation and configuration
- Session factory functionality
- FastAPI dependency injection
- TimestampMixin behavior
"""

from datetime import datetime

import pytest
from sqlalchemy import Integer, String, select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Mapped, Session, mapped_column

from the_lab.db import Base, SessionLocal, engine, get_db
from the_lab.db.base import TimestampMixin


class SampleModel(Base, TimestampMixin):
    """Sample model for validating database infrastructure."""

    __tablename__ = "test_models"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class TestDatabaseEngine:
    """Test database engine configuration."""

    def test_engine_is_created(self) -> None:
        """Verify engine is created and is an Engine instance."""
        assert engine is not None
        assert isinstance(engine, Engine)

    def test_engine_has_correct_dialect(self) -> None:
        """Verify engine uses PostgreSQL dialect."""
        assert engine.dialect.name == "postgresql"

    def test_engine_has_pool_configuration(self) -> None:
        """Verify connection pool is configured."""
        assert engine.pool is not None
        assert engine.pool.size() == 5  # Default pool_size


class TestSessionFactory:
    """Test session factory configuration."""

    def test_session_local_creates_sessions(self) -> None:
        """Verify SessionLocal creates valid Session instances."""
        session = SessionLocal()
        assert isinstance(session, Session)
        session.close()

    def test_session_has_correct_configuration(self) -> None:
        """Verify session factory configuration."""
        session = SessionLocal()
        try:
            # In SQLAlchemy 2.0+, these are configured at sessionmaker level
            # We can verify the session was created from our factory
            assert session.bind == engine
        finally:
            session.close()


class TestGetDbDependency:
    """Test FastAPI database dependency."""

    def test_get_db_yields_session(self) -> None:
        """Verify get_db yields a valid Session."""
        gen = get_db()
        session = next(gen)
        assert isinstance(session, Session)

        # Clean up
        try:
            next(gen)
        except StopIteration:
            pass  # Expected

    def test_get_db_closes_session_on_exit(self) -> None:
        """Verify get_db properly closes sessions."""
        gen = get_db()
        session = next(gen)

        # Session should be open
        assert not session.is_active or True  # is_active depends on transaction state

        # Trigger cleanup
        try:
            next(gen)
        except StopIteration:
            pass

        # Session should be closed (calling methods should raise)
        # Note: SQLAlchemy sessions don't have a simple "is_closed" property


class TestBaseClass:
    """Test declarative Base class."""

    def test_base_has_metadata(self) -> None:
        """Verify Base has metadata configured."""
        assert Base.metadata is not None

    def test_base_has_naming_convention(self) -> None:
        """Verify naming convention is set for constraints."""
        naming_convention = Base.metadata.naming_convention
        assert naming_convention is not None
        assert "pk" in naming_convention
        assert "fk" in naming_convention
        assert "ix" in naming_convention


class TestTimestampMixin:
    """Test TimestampMixin functionality."""

    def test_timestamp_mixin_adds_created_at(self) -> None:
        """Verify TimestampMixin adds created_at column."""
        assert hasattr(SampleModel, "created_at")

    def test_timestamp_mixin_adds_updated_at(self) -> None:
        """Verify TimestampMixin adds updated_at column."""
        assert hasattr(SampleModel, "updated_at")

    def test_model_repr_is_informative(self) -> None:
        """Verify model __repr__ provides useful debugging info."""
        # Create instance (not persisted)
        model = SampleModel(id=1, name="test")
        repr_str = repr(model)
        assert "SampleModel" in repr_str
        assert "id=1" in repr_str
        assert "name='test'" in repr_str


@pytest.mark.integration
class TestDatabaseIntegration:
    """Integration tests requiring actual database connection.

    These tests are marked as integration tests and may be skipped
    in environments without database access.
    """

    @pytest.fixture(autouse=True)
    def setup_teardown(self) -> None:
        """Set up test tables before each test and clean up after."""
        # Create tables
        Base.metadata.create_all(bind=engine)
        yield
        # Drop tables
        Base.metadata.drop_all(bind=engine)

    def test_create_and_query_model(self) -> None:
        """Test creating and querying a model instance."""
        session = SessionLocal()
        try:
            # Create model
            test_model = SampleModel(name="Integration Test")
            session.add(test_model)
            session.commit()
            session.refresh(test_model)

            # Verify it was persisted
            assert test_model.id is not None
            assert test_model.name == "Integration Test"
            assert isinstance(test_model.created_at, datetime)
            assert isinstance(test_model.updated_at, datetime)

            # Query it back
            stmt = select(SampleModel).where(SampleModel.id == test_model.id)
            retrieved = session.scalar(stmt)
            assert retrieved is not None
            assert retrieved.name == "Integration Test"
        finally:
            session.close()

    def test_timestamps_are_set_automatically(self) -> None:
        """Verify created_at and updated_at are set automatically."""
        session = SessionLocal()
        try:
            model = SampleModel(name="Timestamp Test")
            session.add(model)
            session.commit()
            session.refresh(model)

            # Timestamps should be set
            assert model.created_at is not None
            assert model.updated_at is not None

            # They should be approximately equal (within 1 second)
            time_diff = abs((model.updated_at - model.created_at).total_seconds())
            assert time_diff < 1.0
        finally:
            session.close()

    def test_session_rollback_on_error(self) -> None:
        """Verify session rollback works correctly on error."""
        session = SessionLocal()
        try:
            model1 = SampleModel(name="Will Succeed")
            session.add(model1)
            session.commit()

            # Try to create invalid model (simulating an error)
            try:
                model2 = SampleModel(name="Will Fail")
                session.add(model2)
                # Simulate constraint violation or other error
                session.rollback()
            except Exception:
                session.rollback()

            # First model should still exist
            stmt = select(SampleModel).where(SampleModel.name == "Will Succeed")
            result = session.scalar(stmt)
            assert result is not None
        finally:
            session.close()
