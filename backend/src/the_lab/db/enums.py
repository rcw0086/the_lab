"""
PostgreSQL enum types as Python enums.

These enums provide type safety and validation for database enum columns.
Each enum maps directly to a PostgreSQL custom type defined in the schema.
"""

from enum import Enum


class CycleTypes(str, Enum):
    """Training cycle types."""

    MICROCYCLE = "microcycle"
    MESOCYCLE = "mesocycle"
    MACROCYCLE = "macrocycle"


class QuantityUnits(str, Enum):
    """Units for measuring exercise quantities."""

    REPETITIONS = "repetitions"
    METERS = "meters"
    FEET = "feet"
    MILES = "miles"
    KILOMETERS = "kilometers"
    YARDS = "yards"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"


class CadenceUnits(str, Enum):
    """Units for measuring movement cadence."""

    STROKES_PER_MINUTE = "strokes_per_minute"
    STEPS_PER_MINUTE = "steps_per_minute"
    REVOLUTIONS_PER_MINUTE = "revolutions_per_minute"


class Sides(str, Enum):
    """Body sides for unilateral exercises."""

    RIGHT = "right"
    LEFT = "left"


class CarryStyles(str, Enum):
    """Loaded carry exercise styles."""

    VEST = "vest"
    SUITCASE_DOUBLE = "suitcase_double"
    SUITCASE_SINGLE = "suitcase_single"
    CARRY_DOUBLE = "carry_double"
    CARRY_SINGLE = "carry_single"
    FRONT_RACK = "front_rack"
    OTHER = "other"


class ExternalLoadUnits(str, Enum):
    """Units for measuring external resistance."""

    LBS = "lbs"
    KILOGRAMS = "kilograms"
    BODYWEIGHT = "bodyweight"
    PERCENT_1RM = "percent_1rm"


class PaceUnits(str, Enum):
    """Units for measuring pace."""

    PER_MILE = "per_mile"
    PER_KILOMETER = "per_kilometer"
    PER_500M = "per_500m"


class EnergyUnits(str, Enum):
    """Units for measuring energy expenditure."""

    CALORIES = "calories"
    WATTS = "watts"


class SetTypes(str, Enum):
    """Exercise set types."""

    STRENGTH = "strength"
    ENDURANCE = "endurance"
    OTHER = "other"
