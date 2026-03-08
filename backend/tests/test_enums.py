"""Tests for PostgreSQL enum types as Python enums.

Verifies that:
- All enum types are defined
- Enum values match SQL schema exactly
- Enums can be imported and used with type hints
- String serialization works correctly
"""

import json

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


class TestCycleTypes:
    """Test CycleTypes enum."""

    def test_enum_values(self):
        """Verify all cycle type values match SQL schema."""
        assert CycleTypes.MICROCYCLE.value == "microcycle"
        assert CycleTypes.MESOCYCLE.value == "mesocycle"
        assert CycleTypes.MACROCYCLE.value == "macrocycle"

    def test_enum_count(self):
        """Verify correct number of values."""
        assert len(CycleTypes) == 3

    def test_string_behavior(self):
        """Verify enum behaves as string."""
        assert isinstance(CycleTypes.MICROCYCLE, str)
        assert CycleTypes.MICROCYCLE == "microcycle"


class TestQuantityUnits:
    """Test QuantityUnits enum."""

    def test_enum_values(self):
        """Verify all quantity unit values match SQL schema."""
        assert QuantityUnits.REPETITIONS.value == "repetitions"
        assert QuantityUnits.METERS.value == "meters"
        assert QuantityUnits.FEET.value == "feet"
        assert QuantityUnits.MILES.value == "miles"
        assert QuantityUnits.KILOMETERS.value == "kilometers"
        assert QuantityUnits.YARDS.value == "yards"
        assert QuantityUnits.SECONDS.value == "seconds"
        assert QuantityUnits.MINUTES.value == "minutes"
        assert QuantityUnits.HOURS.value == "hours"

    def test_enum_count(self):
        """Verify correct number of values."""
        assert len(QuantityUnits) == 9


class TestCadenceUnits:
    """Test CadenceUnits enum."""

    def test_enum_values(self):
        """Verify all cadence unit values match SQL schema."""
        assert CadenceUnits.STROKES_PER_MINUTE.value == "strokes_per_minute"
        assert CadenceUnits.STEPS_PER_MINUTE.value == "steps_per_minute"
        assert CadenceUnits.REVOLUTIONS_PER_MINUTE.value == "revolutions_per_minute"

    def test_enum_count(self):
        """Verify correct number of values."""
        assert len(CadenceUnits) == 3

    def test_underscore_format(self):
        """Verify snake_case format is preserved."""
        assert "strokes_per_minute" in CadenceUnits.STROKES_PER_MINUTE.value


class TestSides:
    """Test Sides enum."""

    def test_enum_values(self):
        """Verify all side values match SQL schema."""
        assert Sides.RIGHT.value == "right"
        assert Sides.LEFT.value == "left"

    def test_enum_count(self):
        """Verify correct number of values."""
        assert len(Sides) == 2


class TestCarryStyles:
    """Test CarryStyles enum."""

    def test_enum_values(self):
        """Verify all carry style values match SQL schema."""
        assert CarryStyles.VEST.value == "vest"
        assert CarryStyles.SUITCASE_DOUBLE.value == "suitcase_double"
        assert CarryStyles.SUITCASE_SINGLE.value == "suitcase_single"
        assert CarryStyles.CARRY_DOUBLE.value == "carry_double"
        assert CarryStyles.CARRY_SINGLE.value == "carry_single"
        assert CarryStyles.FRONT_RACK.value == "front_rack"
        assert CarryStyles.OTHER.value == "other"

    def test_enum_count(self):
        """Verify correct number of values."""
        assert len(CarryStyles) == 7


class TestExternalLoadUnits:
    """Test ExternalLoadUnits enum."""

    def test_enum_values(self):
        """Verify all external load unit values match SQL schema."""
        assert ExternalLoadUnits.LBS.value == "lbs"
        assert ExternalLoadUnits.KILOGRAMS.value == "kilograms"
        assert ExternalLoadUnits.BODYWEIGHT.value == "bodyweight"
        assert ExternalLoadUnits.PERCENT_1RM.value == "percent_1rm"

    def test_enum_count(self):
        """Verify correct number of values."""
        assert len(ExternalLoadUnits) == 4


class TestPaceUnits:
    """Test PaceUnits enum."""

    def test_enum_values(self):
        """Verify all pace unit values match SQL schema."""
        assert PaceUnits.PER_MILE.value == "per_mile"
        assert PaceUnits.PER_KILOMETER.value == "per_kilometer"
        assert PaceUnits.PER_500M.value == "per_500m"

    def test_enum_count(self):
        """Verify correct number of values."""
        assert len(PaceUnits) == 3


class TestEnergyUnits:
    """Test EnergyUnits enum."""

    def test_enum_values(self):
        """Verify all energy unit values match SQL schema."""
        assert EnergyUnits.CALORIES.value == "calories"
        assert EnergyUnits.WATTS.value == "watts"

    def test_enum_count(self):
        """Verify correct number of values."""
        assert len(EnergyUnits) == 2


class TestSetTypes:
    """Test SetTypes enum."""

    def test_enum_values(self):
        """Verify all set type values match SQL schema."""
        assert SetTypes.STRENGTH.value == "strength"
        assert SetTypes.ENDURANCE.value == "endurance"
        assert SetTypes.OTHER.value == "other"

    def test_enum_count(self):
        """Verify correct number of values."""
        assert len(SetTypes) == 3


class TestEnumImports:
    """Test that enums can be imported from the db module."""

    def test_import_from_db_module(self):
        """Verify enums are accessible from the_lab.db."""
        # Import via the_lab.db module to verify __all__ exports
        from the_lab import db

        assert db.CycleTypes.MICROCYCLE == "microcycle"
        assert db.QuantityUnits.REPETITIONS == "repetitions"
        assert db.CadenceUnits.STROKES_PER_MINUTE == "strokes_per_minute"
        assert db.Sides.RIGHT == "right"
        assert db.CarryStyles.VEST == "vest"
        assert db.ExternalLoadUnits.LBS == "lbs"
        assert db.PaceUnits.PER_MILE == "per_mile"
        assert db.EnergyUnits.CALORIES == "calories"
        assert db.SetTypes.STRENGTH == "strength"


class TestEnumSerialization:
    """Test enum serialization behavior."""

    def test_json_serialization(self):
        """Verify enums serialize as strings for JSON."""
        data = {"cycle": CycleTypes.MICROCYCLE}
        # Should be JSON serializable
        result = json.dumps(data, default=str)
        assert "microcycle" in result

    def test_comparison_with_string(self):
        """Verify enums can be compared to strings."""
        assert CycleTypes.MICROCYCLE == "microcycle"
        assert CycleTypes.MESOCYCLE == "mesocycle"
