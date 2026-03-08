"""SQLAlchemy ORM models.

This package contains all database models organized by domain:
- core: Core entities (User, Dailies, Cycles, Goals, Injuries)
- session: Training session models (Session, Module)
- catalog: Movement catalog (Movement, Implement, VariationType, Variation)
- journal: Journal notes and join tables
- sets: Sets system (Set, StrengthSetDetails, EnduranceSetDetails, SetVariation)
"""

from the_lab.db.models.catalog import (
    Implement,
    Movement,
    Variation,
    VariationType,
)
from the_lab.db.models.core import (
    Cycle,
    Daily,
    Goal,
    Injury,
    User,
)
from the_lab.db.models.journal import (
    CycleNote,
    GoalNote,
    InjuryNote,
    Note,
)
from the_lab.db.models.session import (
    Module,
    Session,
)
from the_lab.db.models.sets import (
    EnduranceSetDetails,
    Set,
    SetVariation,
    StrengthSetDetails,
)

__all__ = [
    "Cycle",
    "CycleNote",
    "Daily",
    "EnduranceSetDetails",
    "Goal",
    "GoalNote",
    "Implement",
    "Injury",
    "InjuryNote",
    "Module",
    "Movement",
    "Note",
    "Session",
    "Set",
    "SetVariation",
    "StrengthSetDetails",
    "User",
    "Variation",
    "VariationType",
]
