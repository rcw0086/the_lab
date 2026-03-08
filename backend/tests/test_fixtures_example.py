"""Example tests demonstrating database testing infrastructure.

This module shows how to use the testing fixtures, factories, and
assertion helpers for effective database testing.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from tests.fixtures.assertions import (
    assert_cascade_deleted,
    assert_check_constraint_violated,
    assert_count,
    assert_exists,
    assert_field_value,
    assert_not_exists,
    assert_relationship_count,
    assert_unique_constraint_violated,
)
from tests.fixtures.factories import (
    create_complete_endurance_set,
    create_complete_strength_set,
    create_cycle,
    create_daily,
    create_goal,
    create_implement,
    create_injury,
    create_module,
    create_movement,
    create_note,
    create_training_session,
    create_user,
    create_variation,
    create_variation_type,
)
from the_lab.db.enums import CycleTypes, ExternalLoadUnits, QuantityUnits, SetTypes
from the_lab.db.models.catalog import Implement, Movement, Variation, VariationType
from the_lab.db.models.core import Cycle, Daily, Goal, Injury, User
from the_lab.db.models.journal import Note
from the_lab.db.models.session import Module, Session as TrainingSession
from the_lab.db.models.sets import EnduranceSetDetails, Set, StrengthSetDetails


class TestBasicModelCreation:
    """Examples of basic model creation using factories."""

    def test_create_user_with_factory(self, db_session: Session) -> None:
        """Test creating a user with factory function."""
        user = create_user(db_session, username="athlete123", role="athlete")

        # Verify user was created
        assert_exists(db_session, User, username="athlete123")
        assert user.role == "athlete"
        assert user.id is not None

    def test_create_multiple_users(self, db_session: Session) -> None:
        """Test creating multiple users in isolation."""
        user1 = create_user(db_session, username="user1")
        user2 = create_user(db_session, username="user2")

        db_session.commit()

        # Verify both exist
        assert_count(db_session, User, 2)
        assert user1.id != user2.id

    def test_create_daily_record(self, db_session: Session) -> None:
        """Test creating daily health record."""
        user = create_user(db_session)
        daily = create_daily(
            db_session,
            user=user,
            date_value=date.today(),
            protein=180,
            sleep=Decimal("8.5"),
        )

        db_session.commit()

        # Verify using assertion helpers
        assert_field_value(db_session, Daily, daily.id, "protein", 180)
        assert_field_value(db_session, Daily, daily.id, "sleep", Decimal("8.5"))

    def test_create_training_cycle(self, db_session: Session) -> None:
        """Test creating a training cycle."""
        user = create_user(db_session)
        cycle = create_cycle(
            db_session,
            user=user,
            cycle_type=CycleTypes.MESOCYCLE,
            title="Hypertrophy Phase",
            start_date=date(2026, 3, 1),
            end_date=date(2026, 5, 31),
        )

        db_session.commit()

        assert_exists(db_session, Cycle, title="Hypertrophy Phase")
        assert cycle.type == CycleTypes.MESOCYCLE


class TestConstraintValidation:
    """Examples of testing database constraints."""

    def test_unique_username_constraint(self, db_session: Session) -> None:
        """Test that usernames must be unique."""
        create_user(db_session, username="duplicate")
        db_session.commit()

        # Try to create another user with same username
        create_user(db_session, username="duplicate")

        with pytest.raises(IntegrityError) as exc_info:
            db_session.commit()

        # Use assertion helper to verify it's a unique constraint
        assert_unique_constraint_violated(exc_info.value)

    def test_protein_check_constraint(self, db_session: Session) -> None:
        """Test that protein must be non-negative."""
        user = create_user(db_session)
        create_daily(db_session, user=user, protein=-10)

        with pytest.raises(IntegrityError) as exc_info:
            db_session.commit()

        assert_check_constraint_violated(exc_info.value)

    def test_sleep_range_constraint(self, db_session: Session) -> None:
        """Test that sleep must be between 0 and 24 hours."""
        user = create_user(db_session)
        create_daily(db_session, user=user, sleep=Decimal("25.0"))

        with pytest.raises(IntegrityError) as exc_info:
            db_session.commit()

        assert_check_constraint_violated(exc_info.value)

    def test_cycle_date_validation(self, db_session: Session) -> None:
        """Test that cycle end_date must be >= start_date."""
        user = create_user(db_session)
        create_cycle(
            db_session,
            user=user,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 5, 1),  # Invalid: before start
        )

        with pytest.raises(IntegrityError) as exc_info:
            db_session.commit()

        assert_check_constraint_violated(exc_info.value)


class TestRelationships:
    """Examples of testing model relationships."""

    def test_user_has_multiple_dailies(self, db_session: Session) -> None:
        """Test user can have multiple daily records."""
        user = create_user(db_session)

        # Create dailies for different days
        for i in range(5):
            create_daily(
                db_session,
                user=user,
                date_value=date.today() - timedelta(days=i),
                protein=150 + i * 10,
            )

        db_session.commit()

        # Verify relationship count
        assert_relationship_count(db_session, user, "dailies", 5)

    def test_cascade_delete_on_user(self, db_session: Session) -> None:
        """Test that deleting user cascades to related records."""
        user = create_user(db_session)

        # Create related records
        daily = create_daily(db_session, user=user)
        cycle = create_cycle(db_session, user=user)
        goal = create_goal(db_session, user=user)
        injury = create_injury(db_session, user=user)

        db_session.commit()

        # Get IDs before deletion
        daily_id = daily.id
        cycle_id = cycle.id
        goal_id = goal.id
        injury_id = injury.id

        # Delete user
        db_session.delete(user)
        db_session.commit()

        # Verify cascade deletion
        assert_cascade_deleted(db_session, Daily, daily_id)
        assert_cascade_deleted(db_session, Cycle, cycle_id)
        assert_cascade_deleted(db_session, Goal, goal_id)
        assert_cascade_deleted(db_session, Injury, injury_id)

    def test_session_module_relationship(self, db_session: Session) -> None:
        """Test session can have multiple ordered modules."""
        user = create_user(db_session)
        session = create_training_session(db_session, user=user)

        # Create modules in order
        module1 = create_module(db_session, session, order_in_session=1)
        module2 = create_module(db_session, session, order_in_session=2)
        module3 = create_module(db_session, session, order_in_session=3)

        db_session.commit()

        # Verify relationship
        assert_relationship_count(db_session, session, "modules", 3)


class TestComplexScenarios:
    """Examples of testing complex multi-entity scenarios."""

    def test_complete_strength_training_session(self, db_session: Session) -> None:
        """Test creating a complete strength training session."""
        # Create user and session
        user = create_user(db_session, username="lifter")
        session = create_training_session(
            db_session, user=user, training_zeal=8, fed=True
        )

        # Create module for strength work
        module = create_module(db_session, session, order_in_session=1)

        # Create complete strength sets using factory
        set1, details1, movement1, implement1 = create_complete_strength_set(
            db_session,
            module=module,
            movement_name="Squat",
            implement_name="Barbell",
            reps=5,
            load=Decimal("225"),
            order=1,
        )

        set2, details2, movement2, implement2 = create_complete_strength_set(
            db_session,
            module=module,
            movement_name="Bench Press",
            implement_name="Barbell",
            reps=8,
            load=Decimal("185"),
            order=2,
        )

        db_session.commit()

        # Verify structure
        assert_count(db_session, TrainingSession, 1)
        assert_count(db_session, Module, 1)
        assert_count(db_session, Set, 2)
        assert_count(db_session, StrengthSetDetails, 2)
        assert_count(db_session, Movement, 2)
        assert_count(db_session, Implement, 1)  # Both use same implement

        # Verify details
        assert details1.reps == 5
        assert details1.external_load_value == Decimal("225")
        assert details2.reps == 8

    def test_mixed_modality_session(self, db_session: Session) -> None:
        """Test session with both strength and endurance work."""
        user = create_user(db_session)
        session = create_training_session(db_session, user=user)

        # Module 1: Strength
        strength_module = create_module(db_session, session, order_in_session=1)
        strength_set, strength_details, _, _ = create_complete_strength_set(
            db_session,
            module=strength_module,
            movement_name="Deadlift",
            implement_name="Barbell",
            reps=5,
            load=Decimal("315"),
        )

        # Module 2: Endurance
        endurance_module = create_module(db_session, session, order_in_session=2)
        endurance_set, endurance_details = create_complete_endurance_set(
            db_session,
            module=endurance_module,
            distance=Decimal("5000"),
            unit=QuantityUnits.METERS,
        )

        db_session.commit()

        # Verify both modalities exist
        assert_count(db_session, Module, 2)
        assert_count(db_session, Set, 2)
        assert_count(db_session, StrengthSetDetails, 1)
        assert_count(db_session, EnduranceSetDetails, 1)

        # Verify set types
        assert strength_set.set_type == SetTypes.STRENGTH
        assert endurance_set.set_type == SetTypes.ENDURANCE

    def test_movement_catalog_with_variations(self, db_session: Session) -> None:
        """Test creating movements with variations."""
        # Create movement
        squat = create_movement(db_session, name="Squat")

        # Create variation type
        stance_type = create_variation_type(db_session, name="Stance")

        # Create variations
        wide = create_variation(db_session, stance_type, name="Wide")
        narrow = create_variation(db_session, stance_type, name="Narrow")
        split = create_variation(db_session, stance_type, name="Split")

        db_session.commit()

        # Verify catalog structure
        assert_count(db_session, Movement, 1)
        assert_count(db_session, VariationType, 1)
        assert_count(db_session, Variation, 3)

        # Verify relationships
        assert_relationship_count(db_session, stance_type, "variations", 3)


class TestTransactionIsolation:
    """Examples demonstrating test isolation via transaction rollback."""

    def test_changes_isolated_between_tests_1(self, db_session: Session) -> None:
        """First test: create a user."""
        user = create_user(db_session, username="isolated_user_1")
        db_session.commit()

        assert_count(db_session, User, 1)

    def test_changes_isolated_between_tests_2(self, db_session: Session) -> None:
        """Second test: should not see user from previous test."""
        # This test should start with clean slate due to transaction rollback
        assert_count(db_session, User, 0)

        # Create different user
        user = create_user(db_session, username="isolated_user_2")
        db_session.commit()

        assert_count(db_session, User, 1)

    def test_changes_isolated_between_tests_3(self, db_session: Session) -> None:
        """Third test: verify isolation again."""
        # Should still start clean
        assert_count(db_session, User, 0)


class TestJournalNotes:
    """Examples of testing journal notes system."""

    def test_create_note_for_goal(self, db_session: Session) -> None:
        """Test creating a note linked to a goal."""
        from the_lab.db.models.journal import GoalNote

        user = create_user(db_session)
        goal = create_goal(db_session, user=user, title="Hit 225 bench")
        note = create_note(
            db_session,
            user=user,
            title="Training Update",
            body="Hit 215 for 3 today. Getting close!",
        )

        # Link note to goal
        goal_note = GoalNote(goal_id=goal.id, note_id=note.id)
        db_session.add(goal_note)
        db_session.commit()

        # Verify relationship
        assert_count(db_session, Note, 1)
        assert_count(db_session, GoalNote, 1)

    def test_note_linked_to_multiple_entities(self, db_session: Session) -> None:
        """Test that a single note can be linked to multiple entities."""
        from the_lab.db.models.journal import CycleNote, GoalNote

        user = create_user(db_session)
        goal = create_goal(db_session, user=user, title="Test Goal")
        cycle = create_cycle(db_session, user=user, title="Test Cycle")
        note = create_note(
            db_session, user=user, title="Reflection", body="Overall progress good"
        )

        # Link to both goal and cycle
        db_session.add(GoalNote(goal_id=goal.id, note_id=note.id))
        db_session.add(CycleNote(cycle_id=cycle.id, note_id=note.id))
        db_session.commit()

        # Verify
        assert_count(db_session, Note, 1)
        assert_count(db_session, GoalNote, 1)
        assert_count(db_session, CycleNote, 1)


class TestPerformanceConsiderations:
    """Examples demonstrating performance best practices."""

    def test_bulk_insert_performance(self, db_session: Session) -> None:
        """Test that bulk operations are efficient.

        This test creates many records to demonstrate that the transaction-based
        approach handles bulk operations efficiently.
        """
        user = create_user(db_session)

        # Create 100 daily records
        for i in range(100):
            create_daily(
                db_session,
                user=user,
                date_value=date(2025, 1, 1) + timedelta(days=i),
                protein=150 + i,
            )

        # Single commit at the end
        db_session.commit()

        # Verify all created
        assert_count(db_session, Daily, 100)

    def test_query_efficiency_with_relationships(self, db_session: Session) -> None:
        """Test efficient querying with relationships loaded."""
        user = create_user(db_session)
        session = create_training_session(db_session, user=user)

        # Create multiple modules
        for i in range(5):
            create_module(db_session, session, order_in_session=i + 1)

        db_session.commit()

        # Query with relationship loading
        from sqlalchemy.orm import selectinload

        queried_session = (
            db_session.query(TrainingSession)
            .options(selectinload(TrainingSession.modules))
            .first()
        )

        # Access relationship without additional query
        assert len(queried_session.modules) == 5
