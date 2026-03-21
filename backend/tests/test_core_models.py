"""Tests for core entity models.

Tests cover:
- Model instantiation
- Constraint validation
- Relationships
- Database operations
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from the_lab.db.models.core import User, Daily, Cycle, Goal, Injury
from the_lab.db.enums import CycleTypes


class TestUser:
    """Tests for User model."""

    def test_create_user(self, db_session: Session) -> None:
        """Test creating a user with required fields."""
        user = User(username="test_user", password_hash="$2b$12$testhashtesthashtesthashtesthashtesthashtesthashte")
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == "test_user"
        assert user.role is None
        assert user.created_at is not None

    def test_username_unique_constraint(self, db_session: Session) -> None:
        """Test that username must be unique."""
        user1 = User(username="duplicate", password_hash="$2b$12$testhashtesthashtesthashtesthashtesthashtesthashte")
        db_session.add(user1)
        db_session.commit()

        user2 = User(username="duplicate", password_hash="$2b$12$testhashtesthashtesthashtesthashtesthashtesthashte")
        db_session.add(user2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_with_role(self, db_session: Session) -> None:
        """Test creating user with role."""
        user = User(username="admin_user", password_hash="$2b$12$testhashtesthashtesthashtesthashtesthashtesthashte", role="admin")
        db_session.add(user)
        db_session.commit()

        assert user.role == "admin"


class TestDaily:
    """Tests for Daily model."""

    def test_create_daily(self, db_session: Session, test_user: User) -> None:
        """Test creating a daily record."""
        today = date.today()
        daily = Daily(
            user_id=test_user.id,
            date=today,
            protein=150,
            sleep=Decimal("7.5"),
        )
        db_session.add(daily)
        db_session.commit()

        assert daily.id is not None
        assert daily.date == today
        assert daily.protein == 150
        assert daily.sleep == Decimal("7.5")

    def test_unique_user_date_constraint(
        self, db_session: Session, test_user: User
    ) -> None:
        """Test that user_id + date must be unique."""
        today = date.today()
        daily1 = Daily(user_id=test_user.id, date=today)
        db_session.add(daily1)
        db_session.commit()

        daily2 = Daily(user_id=test_user.id, date=today)
        db_session.add(daily2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_protein_check_constraint(
        self, db_session: Session, test_user: User
    ) -> None:
        """Test that protein must be >= 0."""
        daily = Daily(user_id=test_user.id, date=date.today(), protein=-10)
        db_session.add(daily)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_sleep_check_constraint(
        self, db_session: Session, test_user: User
    ) -> None:
        """Test that sleep must be between 0 and 24."""
        daily = Daily(user_id=test_user.id, date=date.today(), sleep=Decimal("25.0"))
        db_session.add(daily)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestCycle:
    """Tests for Cycle model."""

    def test_create_cycle(self, db_session: Session, test_user: User) -> None:
        """Test creating a training cycle."""
        cycle = Cycle(
            user_id=test_user.id,
            type=CycleTypes.MESOCYCLE,
            title="Base Building Phase",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 31),
            notes="Focus on volume",
        )
        db_session.add(cycle)
        db_session.commit()

        assert cycle.id is not None
        assert cycle.type == CycleTypes.MESOCYCLE
        assert cycle.title == "Base Building Phase"

    def test_dates_check_constraint(
        self, db_session: Session, test_user: User
    ) -> None:
        """Test that end_date must be >= start_date."""
        cycle = Cycle(
            user_id=test_user.id,
            start_date=date(2026, 3, 31),
            end_date=date(2026, 1, 1),
        )
        db_session.add(cycle)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_cycle_without_dates(
        self, db_session: Session, test_user: User
    ) -> None:
        """Test creating cycle without dates (valid)."""
        cycle = Cycle(
            user_id=test_user.id,
            type=CycleTypes.MICROCYCLE,
            title="Recovery Week",
        )
        db_session.add(cycle)
        db_session.commit()

        assert cycle.id is not None
        assert cycle.start_date is None
        assert cycle.end_date is None


class TestGoal:
    """Tests for Goal model."""

    def test_create_goal(self, db_session: Session, test_user: User) -> None:
        """Test creating a goal."""
        goal = Goal(
            user_id=test_user.id,
            title="Bench press 225 lbs",
            achieved=False,
            date_set=date.today(),
        )
        db_session.add(goal)
        db_session.commit()

        assert goal.id is not None
        assert goal.title == "Bench press 225 lbs"
        assert goal.achieved is False

    def test_achieved_goal(self, db_session: Session, test_user: User) -> None:
        """Test marking goal as achieved."""
        goal = Goal(
            user_id=test_user.id,
            title="Run 5K under 25 minutes",
            achieved=True,
            date_set=date(2026, 1, 1),
            date_achieved=date(2026, 2, 15),
        )
        db_session.add(goal)
        db_session.commit()

        assert goal.achieved is True
        assert goal.date_achieved is not None

    def test_dates_check_constraint(
        self, db_session: Session, test_user: User
    ) -> None:
        """Test that date_achieved must be >= date_set."""
        goal = Goal(
            user_id=test_user.id,
            title="Invalid goal",
            date_set=date(2026, 2, 15),
            date_achieved=date(2026, 1, 1),
        )
        db_session.add(goal)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestInjury:
    """Tests for Injury model."""

    def test_create_injury(self, db_session: Session, test_user: User) -> None:
        """Test creating an injury record."""
        injury = Injury(
            user_id=test_user.id,
            title="Left knee pain",
            injury_date=datetime.now(),
        )
        db_session.add(injury)
        db_session.commit()

        assert injury.id is not None
        assert injury.title == "Left knee pain"
        assert injury.injury_date is not None
        assert injury.full_resolution is None

    def test_resolved_injury(self, db_session: Session, test_user: User) -> None:
        """Test injury with resolution date."""
        injury_date = datetime.now()
        resolution_date = injury_date + timedelta(days=14)

        injury = Injury(
            user_id=test_user.id,
            title="Right shoulder strain",
            injury_date=injury_date,
            full_resolution=resolution_date,
        )
        db_session.add(injury)
        db_session.commit()

        assert injury.full_resolution is not None
        assert injury.full_resolution > injury.injury_date

    def test_dates_check_constraint(
        self, db_session: Session, test_user: User
    ) -> None:
        """Test that full_resolution must be >= injury_date."""
        injury = Injury(
            user_id=test_user.id,
            title="Invalid injury",
            injury_date=datetime.now(),
            full_resolution=datetime.now() - timedelta(days=1),
        )
        db_session.add(injury)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestRelationships:
    """Tests for model relationships."""

    def test_user_cascade_delete(self, db_session: Session, test_user: User) -> None:
        """Test that deleting a user cascades to related entities."""
        # Create related entities
        Daily(user_id=test_user.id, date=date.today())
        Cycle(user_id=test_user.id, title="Test Cycle")
        Goal(user_id=test_user.id, title="Test Goal")
        Injury(user_id=test_user.id, title="Test Injury")
        db_session.commit()

        # Delete user
        db_session.delete(test_user)
        db_session.commit()

        # Verify all related entities were deleted
        assert db_session.query(Daily).count() == 0
        assert db_session.query(Cycle).count() == 0
        assert db_session.query(Goal).count() == 0
        assert db_session.query(Injury).count() == 0


# Fixtures


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    user = User(username="test_user", password_hash="$2b$12$testhashtesthashtesthashtesthashtesthashtesthashte")
    db_session.add(user)
    db_session.commit()
    return user
