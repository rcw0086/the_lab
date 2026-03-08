"""Tests for training session models.

Tests cover:
- Session model creation and constraints
- Module model creation and constraints
- Session-Module relationships
- Ordering and uniqueness constraints
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession

from the_lab.db.models.core import User
from the_lab.db.models.session import Session, Module


class TestSession:
    """Tests for Session model."""

    def test_create_session(self, db_session: DBSession, test_user: User) -> None:
        """Test creating a training session."""
        now = datetime.now()
        session = Session(
            user_id=test_user.id,
            start_time=now,
            end_time=now + timedelta(hours=1),
            training_zeal=8,
            fatigue_concluding=6,
            fed=True,
            notes="Great session!",
        )
        db_session.add(session)
        db_session.commit()

        assert session.id is not None
        assert session.user_id == test_user.id
        assert session.training_zeal == 8
        assert session.fatigue_concluding == 6
        assert session.fed is True

    def test_session_minimal_fields(
        self, db_session: DBSession, test_user: User
    ) -> None:
        """Test creating session with only required fields."""
        session = Session(user_id=test_user.id)
        db_session.add(session)
        db_session.commit()

        assert session.id is not None
        assert session.start_time is None
        assert session.training_zeal is None

    def test_times_check_constraint(
        self, db_session: DBSession, test_user: User
    ) -> None:
        """Test that end_time must be >= start_time."""
        now = datetime.now()
        session = Session(
            user_id=test_user.id,
            start_time=now,
            end_time=now - timedelta(hours=1),
        )
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_training_zeal_check_constraint(
        self, db_session: DBSession, test_user: User
    ) -> None:
        """Test that training_zeal must be between 1 and 10."""
        session = Session(user_id=test_user.id, training_zeal=11)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_fatigue_check_constraint(
        self, db_session: DBSession, test_user: User
    ) -> None:
        """Test that fatigue_concluding must be between 1 and 10."""
        session = Session(user_id=test_user.id, fatigue_concluding=0)
        db_session.add(session)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestModule:
    """Tests for Module model."""

    def test_create_module(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test creating a training module."""
        now = datetime.now()
        module = Module(
            session_id=test_session.id,
            order_in_session=1,
            start_time=now,
            end_time=now + timedelta(minutes=30),
            hr_avg=140,
            hr_max=165,
            notes="Warm-up",
        )
        db_session.add(module)
        db_session.commit()

        assert module.id is not None
        assert module.session_id == test_session.id
        assert module.order_in_session == 1
        assert module.hr_avg == 140
        assert module.hr_max == 165

    def test_module_minimal_fields(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test creating module with only required fields."""
        module = Module(session_id=test_session.id, order_in_session=1)
        db_session.add(module)
        db_session.commit()

        assert module.id is not None
        assert module.start_time is None
        assert module.hr_avg is None

    def test_unique_session_order_constraint(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test that session_id + order_in_session must be unique."""
        module1 = Module(session_id=test_session.id, order_in_session=1)
        db_session.add(module1)
        db_session.commit()

        module2 = Module(session_id=test_session.id, order_in_session=1)
        db_session.add(module2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_order_check_constraint(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test that order_in_session must be >= 1."""
        module = Module(session_id=test_session.id, order_in_session=0)
        db_session.add(module)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_times_check_constraint(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test that end_time must be >= start_time."""
        now = datetime.now()
        module = Module(
            session_id=test_session.id,
            order_in_session=1,
            start_time=now,
            end_time=now - timedelta(minutes=1),
        )
        db_session.add(module)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_hr_check_constraint_avg(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test that hr_avg must be > 0."""
        module = Module(
            session_id=test_session.id, order_in_session=1, hr_avg=-10
        )
        db_session.add(module)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_hr_check_constraint_max(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test that hr_max must be > 0."""
        module = Module(
            session_id=test_session.id, order_in_session=1, hr_max=0
        )
        db_session.add(module)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestRelationships:
    """Tests for Session-Module relationships."""

    def test_session_modules_relationship(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test that session.modules returns ordered modules."""
        # Create modules out of order
        module3 = Module(session_id=test_session.id, order_in_session=3)
        module1 = Module(session_id=test_session.id, order_in_session=1)
        module2 = Module(session_id=test_session.id, order_in_session=2)
        db_session.add_all([module3, module1, module2])
        db_session.commit()

        # Refresh session to load relationship
        db_session.refresh(test_session)

        # Verify modules are ordered
        assert len(test_session.modules) == 3
        assert test_session.modules[0].order_in_session == 1
        assert test_session.modules[1].order_in_session == 2
        assert test_session.modules[2].order_in_session == 3

    def test_module_session_relationship(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test that module.session returns parent session."""
        module = Module(session_id=test_session.id, order_in_session=1)
        db_session.add(module)
        db_session.commit()
        db_session.refresh(module)

        assert module.session.id == test_session.id
        assert module.session.user_id == test_session.user_id

    def test_cascade_delete(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test that deleting a session cascades to modules."""
        module1 = Module(session_id=test_session.id, order_in_session=1)
        module2 = Module(session_id=test_session.id, order_in_session=2)
        db_session.add_all([module1, module2])
        db_session.commit()

        # Delete session
        db_session.delete(test_session)
        db_session.commit()

        # Verify modules were deleted
        assert db_session.query(Module).count() == 0

    def test_mixed_modality_session(
        self, db_session: DBSession, test_session: Session
    ) -> None:
        """Test session with multiple module types (strength + endurance)."""
        # Strength module
        strength = Module(
            session_id=test_session.id,
            order_in_session=1,
            notes="Strength work",
        )
        # Endurance module with heart rate
        endurance = Module(
            session_id=test_session.id,
            order_in_session=2,
            hr_avg=155,
            hr_max=172,
            notes="Conditioning",
        )
        db_session.add_all([strength, endurance])
        db_session.commit()

        db_session.refresh(test_session)
        assert len(test_session.modules) == 2
        assert test_session.modules[0].notes == "Strength work"
        assert test_session.modules[1].hr_avg == 155


# Fixtures


@pytest.fixture
def test_user(db_session: DBSession) -> User:
    """Create a test user."""
    user = User(username="test_user")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_session(db_session: DBSession, test_user: User) -> Session:
    """Create a test session."""
    session = Session(user_id=test_user.id)
    db_session.add(session)
    db_session.commit()
    return session
