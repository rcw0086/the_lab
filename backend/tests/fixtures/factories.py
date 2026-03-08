"""Factory fixtures for creating test data.

This module provides factory functions for creating test instances of domain models.
Factories provide sensible defaults while allowing customization for specific test cases.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from the_lab.db.enums import (
    CadenceUnits,
    CarryStyles,
    CycleTypes,
    EnergyUnits,
    ExternalLoadUnits,
    PaceUnits,
    QuantityUnits,
    SetTypes,
    Sides,
)
from the_lab.db.models.catalog import Implement, Movement, Variation, VariationType
from the_lab.db.models.core import Cycle, Daily, Goal, Injury, User
from the_lab.db.models.journal import CycleNote, GoalNote, InjuryNote, Note
from the_lab.db.models.session import Module, Session as TrainingSession
from the_lab.db.models.sets import (
    EnduranceSetDetails,
    Set,
    SetVariation,
    StrengthSetDetails,
)


# ============================================================
# Core Entity Factories
# ============================================================


def create_user(
    session: Session,
    username: str | None = None,
    role: str | None = None,
    **kwargs: Any,
) -> User:
    """Create a test user.

    Args:
        session: Database session
        username: User's username (default: test_user_<timestamp>)
        role: User's role (optional)
        **kwargs: Additional fields to override

    Returns:
        User: Created user instance
    """
    if username is None:
        username = f"test_user_{datetime.now().timestamp()}"

    user = User(username=username, role=role, **kwargs)
    session.add(user)
    session.flush()  # Flush to get ID without committing
    return user


def create_daily(
    session: Session,
    user: User,
    date_value: date | None = None,
    protein: int | None = None,
    sleep: Decimal | None = None,
    **kwargs: Any,
) -> Daily:
    """Create a test daily record.

    Args:
        session: Database session
        user: User who owns this daily
        date_value: Date for the daily (default: today)
        protein: Protein intake in grams
        sleep: Sleep duration in hours
        **kwargs: Additional fields to override

    Returns:
        Daily: Created daily instance
    """
    if date_value is None:
        date_value = date.today()

    daily = Daily(
        user_id=user.id, date=date_value, protein=protein, sleep=sleep, **kwargs
    )
    session.add(daily)
    session.flush()
    return daily


def create_cycle(
    session: Session,
    user: User,
    cycle_type: CycleTypes = CycleTypes.MESOCYCLE,
    title: str = "Test Cycle",
    start_date: date | None = None,
    end_date: date | None = None,
    notes: str | None = None,
    **kwargs: Any,
) -> Cycle:
    """Create a test training cycle.

    Args:
        session: Database session
        user: User who owns this cycle
        cycle_type: Type of cycle (micro/meso/macro)
        title: Cycle title
        start_date: Cycle start date
        end_date: Cycle end date
        notes: Cycle notes
        **kwargs: Additional fields to override

    Returns:
        Cycle: Created cycle instance
    """
    cycle = Cycle(
        user_id=user.id,
        type=cycle_type,
        title=title,
        start_date=start_date,
        end_date=end_date,
        notes=notes,
        **kwargs,
    )
    session.add(cycle)
    session.flush()
    return cycle


def create_goal(
    session: Session,
    user: User,
    title: str = "Test Goal",
    achieved: bool = False,
    date_set: date | None = None,
    date_achieved: date | None = None,
    notes: str | None = None,
    **kwargs: Any,
) -> Goal:
    """Create a test goal.

    Args:
        session: Database session
        user: User who owns this goal
        title: Goal title
        achieved: Whether goal is achieved
        date_set: Date goal was set
        date_achieved: Date goal was achieved
        notes: Goal notes
        **kwargs: Additional fields to override

    Returns:
        Goal: Created goal instance
    """
    if date_set is None:
        date_set = date.today()

    goal = Goal(
        user_id=user.id,
        title=title,
        achieved=achieved,
        date_set=date_set,
        date_achieved=date_achieved,
        notes=notes,
        **kwargs,
    )
    session.add(goal)
    session.flush()
    return goal


def create_injury(
    session: Session,
    user: User,
    title: str = "Test Injury",
    injury_date: datetime | None = None,
    full_resolution: datetime | None = None,
    **kwargs: Any,
) -> Injury:
    """Create a test injury record.

    Args:
        session: Database session
        user: User who owns this injury
        title: Injury title
        injury_date: Date of injury
        full_resolution: Date of full resolution
        **kwargs: Additional fields to override

    Returns:
        Injury: Created injury instance
    """
    if injury_date is None:
        injury_date = datetime.now()

    injury = Injury(
        user_id=user.id,
        title=title,
        injury_date=injury_date,
        full_resolution=full_resolution,
        **kwargs,
    )
    session.add(injury)
    session.flush()
    return injury


# ============================================================
# Journal Factories
# ============================================================


def create_note(
    session: Session,
    user: User,
    entry_date: date | None = None,
    title: str = "Test Note",
    body: str = "Test note body",
    **kwargs: Any,
) -> Note:
    """Create a test journal note.

    Args:
        session: Database session
        user: User who owns this note
        entry_date: Date of note entry
        title: Note title
        body: Note body content
        **kwargs: Additional fields to override

    Returns:
        Note: Created note instance
    """
    if entry_date is None:
        entry_date = date.today()

    note = Note(
        user_id=user.id, entry_date=entry_date, title=title, body=body, **kwargs
    )
    session.add(note)
    session.flush()
    return note


# ============================================================
# Session Factories
# ============================================================


def create_training_session(
    session: Session,
    user: User,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    training_zeal: int | None = None,
    fatigue_concluding: int | None = None,
    fed: bool | None = None,
    notes: str | None = None,
    **kwargs: Any,
) -> TrainingSession:
    """Create a test training session.

    Args:
        session: Database session
        user: User who owns this session
        start_time: Session start time
        end_time: Session end time
        training_zeal: Training zeal rating (1-10)
        fatigue_concluding: Fatigue rating (1-10)
        fed: Whether athlete was fed
        notes: Session notes
        **kwargs: Additional fields to override

    Returns:
        TrainingSession: Created session instance
    """
    if start_time is None:
        start_time = datetime.now()

    training_session = TrainingSession(
        user_id=user.id,
        start_time=start_time,
        end_time=end_time,
        training_zeal=training_zeal,
        fatigue_concluding=fatigue_concluding,
        fed=fed,
        notes=notes,
        **kwargs,
    )
    session.add(training_session)
    session.flush()
    return training_session


def create_module(
    session: Session,
    training_session: TrainingSession,
    order_in_session: int = 1,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    hr_avg: int | None = None,
    hr_max: int | None = None,
    notes: str | None = None,
    **kwargs: Any,
) -> Module:
    """Create a test training module.

    Args:
        session: Database session
        training_session: Session this module belongs to
        order_in_session: Order position in session
        start_time: Module start time
        end_time: Module end time
        hr_avg: Average heart rate
        hr_max: Maximum heart rate
        notes: Module notes
        **kwargs: Additional fields to override

    Returns:
        Module: Created module instance
    """
    if start_time is None:
        start_time = training_session.start_time or datetime.now()

    module = Module(
        session_id=training_session.id,
        order_in_session=order_in_session,
        start_time=start_time,
        end_time=end_time,
        hr_avg=hr_avg,
        hr_max=hr_max,
        notes=notes,
        **kwargs,
    )
    session.add(module)
    session.flush()
    return module


# ============================================================
# Catalog Factories
# ============================================================


def create_movement(
    session: Session, name: str = "Test Movement", **kwargs: Any
) -> Movement:
    """Create a test movement.

    Args:
        session: Database session
        name: Movement name (must be unique)
        **kwargs: Additional fields to override

    Returns:
        Movement: Created movement instance
    """
    movement = Movement(name=name, **kwargs)
    session.add(movement)
    session.flush()
    return movement


def create_implement(
    session: Session, name: str = "Test Implement", **kwargs: Any
) -> Implement:
    """Create a test implement.

    Args:
        session: Database session
        name: Implement name (must be unique)
        **kwargs: Additional fields to override

    Returns:
        Implement: Created implement instance
    """
    implement = Implement(name=name, **kwargs)
    session.add(implement)
    session.flush()
    return implement


def create_variation_type(
    session: Session, name: str = "Test Variation Type", **kwargs: Any
) -> VariationType:
    """Create a test variation type.

    Args:
        session: Database session
        name: Variation type name (must be unique)
        **kwargs: Additional fields to override

    Returns:
        VariationType: Created variation type instance
    """
    variation_type = VariationType(name=name, **kwargs)
    session.add(variation_type)
    session.flush()
    return variation_type


def create_variation(
    session: Session,
    variation_type: VariationType,
    name: str = "Test Variation",
    **kwargs: Any,
) -> Variation:
    """Create a test variation.

    Args:
        session: Database session
        variation_type: Variation type this belongs to
        name: Variation name
        **kwargs: Additional fields to override

    Returns:
        Variation: Created variation instance
    """
    variation = Variation(variation_type_id=variation_type.id, name=name, **kwargs)
    session.add(variation)
    session.flush()
    return variation


# ============================================================
# Set Factories
# ============================================================


def create_set(
    session: Session,
    module: Module,
    order_in_module: int = 1,
    set_type: SetTypes = SetTypes.STRENGTH,
    parent_set_id: int | None = None,
    rest_period_prior_seconds: int | None = None,
    hr_avg: int | None = None,
    hr_min: int | None = None,
    hr_max: int | None = None,
    notes: str | None = None,
    **kwargs: Any,
) -> Set:
    """Create a test set.

    Args:
        session: Database session
        module: Module this set belongs to
        order_in_module: Order position in module
        set_type: Type of set (strength/endurance/other)
        parent_set_id: Parent set ID for supersets
        rest_period_prior_seconds: Rest before this set
        hr_avg: Average heart rate
        hr_min: Minimum heart rate
        hr_max: Maximum heart rate
        notes: Set notes
        **kwargs: Additional fields to override

    Returns:
        Set: Created set instance
    """
    set_obj = Set(
        module_id=module.id,
        order_in_module=order_in_module,
        set_type=set_type,
        parent_set_id=parent_set_id,
        rest_period_prior_seconds=rest_period_prior_seconds,
        hr_avg=hr_avg,
        hr_min=hr_min,
        hr_max=hr_max,
        notes=notes,
        **kwargs,
    )
    session.add(set_obj)
    session.flush()
    return set_obj


def create_strength_set_details(
    session: Session,
    set_obj: Set,
    movement: Movement,
    implement: Implement | None = None,
    reps: int | None = None,
    external_load_value: Decimal | None = None,
    external_load_unit: ExternalLoadUnits | None = None,
    rir: int | None = None,
    intensity_percentage: Decimal | None = None,
    tempo: str | None = None,
    **kwargs: Any,
) -> StrengthSetDetails:
    """Create test strength set details.

    Args:
        session: Database session
        set_obj: Set this details record belongs to
        movement: Movement performed
        implement: Implement used
        reps: Number of repetitions
        external_load_value: Load value
        external_load_unit: Load unit
        rir: Reps in reserve
        intensity_percentage: Intensity as percentage of 1RM
        tempo: Tempo notation
        **kwargs: Additional fields to override

    Returns:
        StrengthSetDetails: Created strength details instance
    """
    details = StrengthSetDetails(
        set_id=set_obj.id,
        movement_id=movement.id,
        implement_id=implement.id if implement else None,
        reps=reps,
        external_load_value=external_load_value,
        external_load_unit=external_load_unit,
        rir=rir,
        intensity_percentage=intensity_percentage,
        tempo=tempo,
        **kwargs,
    )
    session.add(details)
    session.flush()
    return details


def create_endurance_set_details(
    session: Session,
    set_obj: Set,
    quantity_value: Decimal | None = None,
    quantity_unit: QuantityUnits | None = None,
    average_cadence: Decimal | None = None,
    cadence_unit: CadenceUnits | None = None,
    pace_seconds: int | None = None,
    pace_unit: PaceUnits | None = None,
    energy_value: Decimal | None = None,
    energy_unit: EnergyUnits | None = None,
    **kwargs: Any,
) -> EnduranceSetDetails:
    """Create test endurance set details.

    Args:
        session: Database session
        set_obj: Set this details record belongs to
        quantity_value: Distance/duration value
        quantity_unit: Distance/duration unit
        average_cadence: Average cadence
        cadence_unit: Cadence unit
        pace_seconds: Pace in seconds
        pace_unit: Pace unit
        energy_value: Energy expenditure value
        energy_unit: Energy unit
        **kwargs: Additional fields to override

    Returns:
        EnduranceSetDetails: Created endurance details instance
    """
    details = EnduranceSetDetails(
        set_id=set_obj.id,
        quantity_value=quantity_value,
        quantity_unit=quantity_unit,
        average_cadence=average_cadence,
        cadence_unit=cadence_unit,
        pace_seconds=pace_seconds,
        pace_unit=pace_unit,
        energy_value=energy_value,
        energy_unit=energy_unit,
        **kwargs,
    )
    session.add(details)
    session.flush()
    return details


# ============================================================
# Complex Scenario Factories
# ============================================================


def create_complete_strength_set(
    session: Session,
    module: Module,
    movement_name: str = "Squat",
    implement_name: str = "Barbell",
    reps: int = 5,
    load: Decimal = Decimal("135"),
    order: int = 1,
) -> tuple[Set, StrengthSetDetails, Movement, Implement]:
    """Create a complete strength set with all related entities.

    Args:
        session: Database session
        module: Module this set belongs to
        movement_name: Name of movement
        implement_name: Name of implement
        reps: Number of reps
        load: External load value
        order: Order in module

    Returns:
        Tuple of (Set, StrengthSetDetails, Movement, Implement)
    """
    # Create catalog entities
    movement = create_movement(session, name=movement_name)
    implement = create_implement(session, name=implement_name)

    # Create set
    set_obj = create_set(
        session, module=module, order_in_module=order, set_type=SetTypes.STRENGTH
    )

    # Create details
    details = create_strength_set_details(
        session=session,
        set_obj=set_obj,
        movement=movement,
        implement=implement,
        reps=reps,
        external_load_value=load,
        external_load_unit=ExternalLoadUnits.LBS,
    )

    return set_obj, details, movement, implement


def create_complete_endurance_set(
    session: Session,
    module: Module,
    distance: Decimal = Decimal("5000"),
    unit: QuantityUnits = QuantityUnits.METERS,
    order: int = 1,
) -> tuple[Set, EnduranceSetDetails]:
    """Create a complete endurance set with all related entities.

    Args:
        session: Database session
        module: Module this set belongs to
        distance: Distance value
        unit: Distance unit
        order: Order in module

    Returns:
        Tuple of (Set, EnduranceSetDetails)
    """
    # Create set
    set_obj = create_set(
        session, module=module, order_in_module=order, set_type=SetTypes.ENDURANCE
    )

    # Create details
    details = create_endurance_set_details(
        session=session, set_obj=set_obj, quantity_value=distance, quantity_unit=unit
    )

    return set_obj, details
