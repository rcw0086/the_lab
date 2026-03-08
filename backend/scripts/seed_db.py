#!/usr/bin/env python3
"""
Database seed script for The Lab.

Populates the database with realistic development data:
- Users (athlete and coach roles)
- Movement catalog (movements, implements, variations)
- Training sessions with modules and sets
- Goals, cycles, injuries
- Journal notes linked to entities

Usage:
    uv run python scripts/seed_db.py          # Add seed data
    uv run python scripts/seed_db.py --reset  # Clear and re-seed
"""

import argparse
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Add backend/src to path for imports
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root / "src"))

from sqlalchemy import text
from sqlalchemy.orm import Session

from the_lab.db.enums import (
    CarryStyles,
    CycleTypes,
    EnergyUnits,
    ExternalLoadUnits,
    QuantityUnits,
    SetTypes,
)
from the_lab.db.models import (
    Cycle,
    CycleNote,
    Daily,
    EnduranceSetDetails,
    Goal,
    GoalNote,
    Implement,
    Injury,
    InjuryNote,
    Module,
    Movement,
    Note,
    Session as TrainingSession,
    Set,
    SetVariation,
    StrengthSetDetails,
    User,
    Variation,
    VariationType,
)
from the_lab.config import get_settings
from the_lab.db.session import SessionLocal, engine
from the_lab.logging import get_logger, setup_logging

# Set up logging
settings = get_settings()
setup_logging(settings)
logger = get_logger(__name__)


def clear_database(db: Session) -> None:
    """Clear all data from the database.

    Args:
        db: Database session
    """
    logger.info("Clearing existing data from database...")

    # Drop all tables in reverse dependency order
    tables = [
        "set_variations",
        "endurance_set_details",
        "strength_set_details",
        "sets",
        "modules",
        "sessions",
        "injury_notes",
        "cycle_notes",
        "goal_notes",
        "notes",
        "injuries",
        "goals",
        "cycles",
        "dailies",
        "variations",
        "variation_types",
        "implements",
        "movements",
        "users",
    ]

    for table in tables:
        db.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))

    db.commit()
    logger.info("Database cleared successfully")


def seed_users(db: Session) -> dict[str, User]:
    """Create sample users.

    Args:
        db: Database session

    Returns:
        Dictionary mapping user names to User objects
    """
    logger.info("Seeding users...")

    users = {
        "athlete": User(username="test_athlete", role="athlete"),
        "coach": User(username="coach_user", role="coach"),
    }

    db.add_all(users.values())
    db.commit()

    for key, user in users.items():
        db.refresh(user)
        logger.info(f"Created user: {user.username} (id={user.id})")

    return users


def seed_movement_catalog(db: Session) -> dict:
    """Create movement catalog with movements, implements, and variations.

    Args:
        db: Database session

    Returns:
        Dictionary with movements, implements, and variations
    """
    logger.info("Seeding movement catalog...")

    # Movements - fundamental patterns
    movements = {
        "squat": Movement(name="Squat"),
        "deadlift": Movement(name="Deadlift"),
        "bench_press": Movement(name="Bench Press"),
        "overhead_press": Movement(name="Overhead Press"),
        "row": Movement(name="Row"),
        "pullup": Movement(name="Pull-up"),
        "carry": Movement(name="Carry"),
        "lunge": Movement(name="Lunge"),
        "hinge": Movement(name="Hinge"),
        "run": Movement(name="Run"),
        "bike": Movement(name="Bike"),
        "row_erg": Movement(name="Row (Erg)"),
    }
    db.add_all(movements.values())
    db.commit()
    for key, mv in movements.items():
        db.refresh(mv)

    # Implements - equipment
    implements = {
        "barbell": Implement(name="Barbell"),
        "dumbbell": Implement(name="Dumbbell"),
        "kettlebell": Implement(name="Kettlebell"),
        "bodyweight": Implement(name="Bodyweight"),
        "trap_bar": Implement(name="Trap Bar"),
        "cable": Implement(name="Cable"),
        "band": Implement(name="Band"),
        "machine": Implement(name="Machine"),
    }
    db.add_all(implements.values())
    db.commit()
    for key, imp in implements.items():
        db.refresh(imp)

    # Variation types and variations
    stance_type = VariationType(name="Stance")
    db.add(stance_type)
    db.commit()
    db.refresh(stance_type)

    stance_variations = [
        Variation(variation_type_id=stance_type.id, name="Close"),
        Variation(variation_type_id=stance_type.id, name="Wide"),
        Variation(variation_type_id=stance_type.id, name="Split"),
        Variation(variation_type_id=stance_type.id, name="Sumo"),
    ]
    db.add_all(stance_variations)

    tempo_type = VariationType(name="Tempo")
    db.add(tempo_type)
    db.commit()
    db.refresh(tempo_type)

    tempo_variations = [
        Variation(variation_type_id=tempo_type.id, name="Pause"),
        Variation(variation_type_id=tempo_type.id, name="Slow Eccentric"),
        Variation(variation_type_id=tempo_type.id, name="Explosive"),
    ]
    db.add_all(tempo_variations)

    grip_type = VariationType(name="Grip")
    db.add(grip_type)
    db.commit()
    db.refresh(grip_type)

    grip_variations = [
        Variation(variation_type_id=grip_type.id, name="Pronated"),
        Variation(variation_type_id=grip_type.id, name="Supinated"),
        Variation(variation_type_id=grip_type.id, name="Neutral"),
        Variation(variation_type_id=grip_type.id, name="Mixed"),
    ]
    db.add_all(grip_variations)

    db.commit()

    # Refresh all variations
    variations = stance_variations + tempo_variations + grip_variations
    for var in variations:
        db.refresh(var)

    logger.info(f"Created {len(movements)} movements")
    logger.info(f"Created {len(implements)} implements")
    logger.info(f"Created {len(variations)} variations across 3 types")

    return {
        "movements": movements,
        "implements": implements,
        "variations": {
            "stance": stance_variations,
            "tempo": tempo_variations,
            "grip": grip_variations,
        },
    }


def seed_goals_and_cycles(db: Session, users: dict[str, User]) -> dict:
    """Create sample goals and training cycles.

    Args:
        db: Database session
        users: Dictionary of users

    Returns:
        Dictionary with goals and cycles
    """
    logger.info("Seeding goals and cycles...")

    athlete = users["athlete"]
    today = date.today()

    # Goals
    goals = [
        Goal(
            user_id=athlete.id,
            title="Squat 405 lbs for 1 rep",
            achieved=False,
            date_set=today - timedelta(days=60),
            notes="Focus on consistent progressive overload and recovery",
        ),
        Goal(
            user_id=athlete.id,
            title="Complete half marathon under 2 hours",
            achieved=True,
            date_set=today - timedelta(days=120),
            date_achieved=today - timedelta(days=30),
            notes="Achieved at Spring City Race",
        ),
        Goal(
            user_id=athlete.id,
            title="10 strict pull-ups",
            achieved=False,
            date_set=today - timedelta(days=45),
            notes="Currently at 6-7 reps",
        ),
    ]
    db.add_all(goals)
    db.commit()
    for goal in goals:
        db.refresh(goal)

    # Training cycles
    cycles = [
        Cycle(
            user_id=athlete.id,
            type=CycleTypes.MESOCYCLE,
            start_date=today - timedelta(days=56),
            end_date=today,
            title="8-Week Strength Mesocycle",
            notes="Focus on squat and deadlift progression",
        ),
        Cycle(
            user_id=athlete.id,
            type=CycleTypes.MICROCYCLE,
            start_date=today - timedelta(days=7),
            end_date=today,
            title="Current Week - Deload",
            notes="Reduced volume and intensity for recovery",
        ),
    ]
    db.add_all(cycles)
    db.commit()
    for cycle in cycles:
        db.refresh(cycle)

    logger.info(f"Created {len(goals)} goals")
    logger.info(f"Created {len(cycles)} cycles")

    return {"goals": goals, "cycles": cycles}


def seed_injuries_and_notes(
    db: Session, users: dict[str, User], goals: list[Goal], cycles: list[Cycle]
) -> dict:
    """Create sample injuries and journal notes.

    Args:
        db: Database session
        users: Dictionary of users
        goals: List of goals
        cycles: List of cycles

    Returns:
        Dictionary with injuries and notes
    """
    logger.info("Seeding injuries and notes...")

    athlete = users["athlete"]
    today = date.today()

    # Injuries
    injuries = [
        Injury(
            user_id=athlete.id,
            title="Left knee strain",
            injury_date=datetime.now(timezone.utc) - timedelta(days=90),
            full_resolution=datetime.now(timezone.utc) - timedelta(days=45),
        ),
        Injury(
            user_id=athlete.id,
            title="Right shoulder impingement",
            injury_date=datetime.now(timezone.utc) - timedelta(days=15),
            full_resolution=None,  # Still ongoing
        ),
    ]
    db.add_all(injuries)
    db.commit()
    for injury in injuries:
        db.refresh(injury)

    # Journal notes
    notes = [
        Note(
            user_id=athlete.id,
            entry_date=today - timedelta(days=7),
            title="Great training week",
            body="Hit new PR on squats (385x3). Feeling strong and recovered. Sleep has been excellent.",
        ),
        Note(
            user_id=athlete.id,
            entry_date=today - timedelta(days=3),
            title="Shoulder acting up",
            body="Noticed some discomfort during overhead press. Switching to neutral grip variations and reducing volume.",
        ),
        Note(
            user_id=athlete.id,
            entry_date=today - timedelta(days=1),
            title="Cycle reflection",
            body="8-week mesocycle complete. Made solid strength gains. Ready for deload week.",
        ),
    ]
    db.add_all(notes)
    db.commit()
    for note in notes:
        db.refresh(note)

    # Link notes to entities
    # Note 1 -> Goal 1 (squat PR related to squat goal)
    goal_note = GoalNote(goal_id=goals[0].id, note_id=notes[0].id)
    db.add(goal_note)

    # Note 2 -> Injury 2 (shoulder note related to shoulder injury)
    injury_note = InjuryNote(injury_id=injuries[1].id, note_id=notes[1].id)
    db.add(injury_note)

    # Note 3 -> Cycle 1 (cycle reflection)
    cycle_note = CycleNote(cycle_id=cycles[0].id, note_id=notes[2].id)
    db.add(cycle_note)

    db.commit()

    logger.info(f"Created {len(injuries)} injuries")
    logger.info(f"Created {len(notes)} notes with entity associations")

    return {"injuries": injuries, "notes": notes}


def seed_daily_tracking(db: Session, users: dict[str, User]) -> None:
    """Create sample daily tracking data.

    Args:
        db: Database session
        users: Dictionary of users
    """
    logger.info("Seeding daily tracking data...")

    athlete = users["athlete"]
    today = date.today()

    dailies = []
    for i in range(7):
        day = today - timedelta(days=i)
        daily = Daily(
            user_id=athlete.id,
            date=day,
            protein=180 + (i * 10 % 40),  # Vary between 180-220g
            sleep=7.0 + (i * 0.5 % 2),  # Vary between 7-9 hours
        )
        dailies.append(daily)

    db.add_all(dailies)
    db.commit()

    logger.info(f"Created {len(dailies)} daily records")


def seed_training_sessions(
    db: Session, users: dict[str, User], catalog: dict
) -> None:
    """Create sample training sessions with modules and sets.

    Args:
        db: Database session
        users: Dictionary of users
        catalog: Movement catalog dictionary
    """
    logger.info("Seeding training sessions...")

    athlete = users["athlete"]
    movements = catalog["movements"]
    implements = catalog["implements"]
    today = datetime.now(timezone.utc)

    # Session 1: Strength session (squats + accessories)
    session1 = TrainingSession(
        user_id=athlete.id,
        start_time=today - timedelta(days=2, hours=2),
        end_time=today - timedelta(days=2, hours=1),
        training_zeal=8,
        fatigue_concluding=7,
        fed=True,
        notes="Solid squat session. Felt strong.",
    )
    db.add(session1)
    db.commit()
    db.refresh(session1)

    # Module 1: Main strength work (squats)
    module1 = Module(
        session_id=session1.id,
        order_in_session=1,
        start_time=today - timedelta(days=2, hours=2),
        end_time=today - timedelta(days=2, hours=1, minutes=30),
        hr_avg=120,
        hr_max=145,
        notes="Back squat progression",
    )
    db.add(module1)
    db.commit()
    db.refresh(module1)

    # Sets for module 1 - Back Squat 5x5
    for i in range(5):
        set_obj = Set(
            module_id=module1.id,
            order_in_module=i + 1,
            set_type=SetTypes.STRENGTH,
            rest_period_prior_seconds=180 if i > 0 else 0,
            hr_avg=125 + (i * 2),
        )
        db.add(set_obj)
        db.commit()
        db.refresh(set_obj)

        # Add strength details
        strength_details = StrengthSetDetails(
            set_id=set_obj.id,
            movement_id=movements["squat"].id,
            implement_id=implements["barbell"].id,
            external_load_value=315,
            external_load_unit=ExternalLoadUnits.LBS,
            reps=5,
            rir=2 if i < 3 else 1,  # Less RIR on later sets
            tempo="3020",  # 3s eccentric, 0s pause, 2s concentric, 0s pause
        )
        db.add(strength_details)

    # Module 2: Accessory work (RDLs)
    module2 = Module(
        session_id=session1.id,
        order_in_session=2,
        start_time=today - timedelta(days=2, hours=1, minutes=25),
        end_time=today - timedelta(days=2, hours=1),
        hr_avg=110,
        hr_max=130,
        notes="Romanian deadlifts for hamstrings",
    )
    db.add(module2)
    db.commit()
    db.refresh(module2)

    # Sets for module 2 - RDLs 3x8
    for i in range(3):
        set_obj = Set(
            module_id=module2.id,
            order_in_module=i + 1,
            set_type=SetTypes.STRENGTH,
            rest_period_prior_seconds=120 if i > 0 else 0,
        )
        db.add(set_obj)
        db.commit()
        db.refresh(set_obj)

        strength_details = StrengthSetDetails(
            set_id=set_obj.id,
            movement_id=movements["hinge"].id,
            implement_id=implements["barbell"].id,
            external_load_value=225,
            external_load_unit=ExternalLoadUnits.LBS,
            reps=8,
            rir=3,
        )
        db.add(strength_details)

    db.commit()

    # Session 2: Mixed session (strength + endurance)
    session2 = TrainingSession(
        user_id=athlete.id,
        start_time=today - timedelta(days=1, hours=1, minutes=30),
        end_time=today - timedelta(days=1, hours=0, minutes=30),
        training_zeal=7,
        fatigue_concluding=6,
        fed=False,
        notes="Morning session. Felt good despite fasted state.",
    )
    db.add(session2)
    db.commit()
    db.refresh(session2)

    # Module 1: Bench press
    module3 = Module(
        session_id=session2.id,
        order_in_session=1,
        start_time=today - timedelta(days=1, hours=1, minutes=30),
        end_time=today - timedelta(days=1, hours=1, minutes=10),
        notes="Bench press 4x6",
    )
    db.add(module3)
    db.commit()
    db.refresh(module3)

    for i in range(4):
        set_obj = Set(
            module_id=module3.id,
            order_in_module=i + 1,
            set_type=SetTypes.STRENGTH,
            rest_period_prior_seconds=150 if i > 0 else 0,
        )
        db.add(set_obj)
        db.commit()
        db.refresh(set_obj)

        strength_details = StrengthSetDetails(
            set_id=set_obj.id,
            movement_id=movements["bench_press"].id,
            implement_id=implements["barbell"].id,
            external_load_value=225,
            external_load_unit=ExternalLoadUnits.LBS,
            reps=6,
            rir=2,
        )
        db.add(strength_details)

    # Module 2: Endurance work (bike)
    module4 = Module(
        session_id=session2.id,
        order_in_session=2,
        start_time=today - timedelta(days=1, hours=1, minutes=5),
        end_time=today - timedelta(days=1, hours=0, minutes=30),
        hr_avg=145,
        hr_max=165,
        notes="Steady state cardio",
    )
    db.add(module4)
    db.commit()
    db.refresh(module4)

    # Single endurance set
    set_obj = Set(
        module_id=module4.id,
        order_in_module=1,
        set_type=SetTypes.ENDURANCE,
    )
    db.add(set_obj)
    db.commit()
    db.refresh(set_obj)

    endurance_details = EnduranceSetDetails(
        set_id=set_obj.id,
        quantity_value=20,
        quantity_unit=QuantityUnits.MINUTES,
        energy_value=250,
        energy_unit=EnergyUnits.CALORIES,
    )
    db.add(endurance_details)

    db.commit()

    logger.info(f"Created 2 training sessions with multiple modules and sets")


def main() -> None:
    """Main entry point for seed script."""
    parser = argparse.ArgumentParser(
        description="Seed The Lab database with development data"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear existing data before seeding",
    )
    args = parser.parse_args()

    logger.info("Starting database seeding...")

    # Create database session
    db = SessionLocal()

    try:
        # Clear data if requested
        if args.reset:
            clear_database(db)

        # Seed data in dependency order
        users = seed_users(db)
        catalog = seed_movement_catalog(db)
        goals_cycles = seed_goals_and_cycles(db, users)
        seed_injuries_and_notes(
            db, users, goals_cycles["goals"], goals_cycles["cycles"]
        )
        seed_daily_tracking(db, users)
        seed_training_sessions(db, users, catalog)

        logger.info("Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"Error during seeding: {e}", exc_info=True)
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
