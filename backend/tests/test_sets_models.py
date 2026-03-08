"""Tests for sets system models.

Tests cover:
- Set model creation and constraints
- StrengthSetDetails model creation and constraints
- EnduranceSetDetails model creation and constraints
- SetVariation join table
- Relationships between models
- Hierarchical set relationships (supersets, clusters)
"""

import pytest
from decimal import Decimal
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DBSession

from the_lab.db.models.catalog import Movement, Implement, Variation, VariationType
from the_lab.db.models.core import User
from the_lab.db.models.session import Session, Module
from the_lab.db.models.sets import (
    Set,
    StrengthSetDetails,
    EnduranceSetDetails,
    SetVariation,
)
from the_lab.db.enums import (
    SetTypes,
    ExternalLoadUnits,
    QuantityUnits,
    CadenceUnits,
    PaceUnits,
    EnergyUnits,
    CarryStyles,
)


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


@pytest.fixture
def test_module(db_session: DBSession, test_session: Session) -> Module:
    """Create a test module."""
    module = Module(session_id=test_session.id, order_in_session=1)
    db_session.add(module)
    db_session.commit()
    return module


@pytest.fixture
def test_movement(db_session: DBSession) -> Movement:
    """Create a test movement."""
    movement = Movement(name="Squat")
    db_session.add(movement)
    db_session.commit()
    return movement


@pytest.fixture
def test_implement(db_session: DBSession) -> Implement:
    """Create a test implement."""
    implement = Implement(name="Barbell")
    db_session.add(implement)
    db_session.commit()
    return implement


@pytest.fixture
def test_variation_type(db_session: DBSession) -> VariationType:
    """Create a test variation type."""
    var_type = VariationType(name="Stance")
    db_session.add(var_type)
    db_session.commit()
    return var_type


@pytest.fixture
def test_variation(
    db_session: DBSession, test_variation_type: VariationType
) -> Variation:
    """Create a test variation."""
    variation = Variation(variation_type_id=test_variation_type.id, name="Wide")
    db_session.add(variation)
    db_session.commit()
    return variation


class TestSet:
    """Tests for Set model."""

    def test_create_set(self, db_session: DBSession, test_module: Module) -> None:
        """Test creating a basic set."""
        set_obj = Set(
            module_id=test_module.id,
            order_in_module=1,
            set_type=SetTypes.STRENGTH,
            rest_period_prior_seconds=60,
            hr_avg=140,
            hr_min=130,
            hr_max=150,
            notes="Great set!",
        )
        db_session.add(set_obj)
        db_session.commit()

        assert set_obj.id is not None
        assert set_obj.module_id == test_module.id
        assert set_obj.order_in_module == 1
        assert set_obj.set_type == SetTypes.STRENGTH
        assert set_obj.rest_period_prior_seconds == 60
        assert set_obj.hr_avg == 140

    def test_set_minimal_fields(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test creating set with only required fields."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        assert set_obj.id is not None
        assert set_obj.rest_period_prior_seconds is None
        assert set_obj.hr_avg is None

    def test_set_order_check_constraint(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test that order_in_module must be >= 1."""
        set_obj = Set(module_id=test_module.id, order_in_module=0)
        db_session.add(set_obj)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_set_rest_check_constraint(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test that rest_period_prior_seconds must be >= 0."""
        set_obj = Set(
            module_id=test_module.id,
            order_in_module=1,
            rest_period_prior_seconds=-1,
        )
        db_session.add(set_obj)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_set_hr_check_constraint(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test that heart rate values must be > 0."""
        set_obj = Set(module_id=test_module.id, order_in_module=1, hr_avg=0)
        db_session.add(set_obj)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_set_unique_module_order(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test that (module_id, order_in_module) is unique."""
        set1 = Set(module_id=test_module.id, order_in_module=1)
        set2 = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set1)
        db_session.commit()
        db_session.add(set2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_set_hierarchical_relationship(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test parent-child set relationships (for supersets)."""
        parent_set = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(parent_set)
        db_session.commit()

        child_set = Set(
            module_id=test_module.id,
            order_in_module=2,
            parent_set_id=parent_set.id,
        )
        db_session.add(child_set)
        db_session.commit()

        assert child_set.parent_set_id == parent_set.id
        assert len(parent_set.child_sets) == 1
        assert parent_set.child_sets[0].id == child_set.id

    def test_set_cascade_delete_from_module(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test that deleting a module cascades to sets."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()
        set_id = set_obj.id

        db_session.delete(test_module)
        db_session.commit()

        assert db_session.get(Set, set_id) is None


class TestStrengthSetDetails:
    """Tests for StrengthSetDetails model."""

    def test_create_strength_details(
        self,
        db_session: DBSession,
        test_module: Module,
        test_movement: Movement,
        test_implement: Implement,
    ) -> None:
        """Test creating strength set details."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        details = StrengthSetDetails(
            set_id=set_obj.id,
            movement_id=test_movement.id,
            implement_id=test_implement.id,
            external_load_value=Decimal("225.00"),
            external_load_unit=ExternalLoadUnits.LBS,
            reps=5,
            rir=2,
            intensity_percentage=Decimal("85.50"),
            tempo="3010",
        )
        db_session.add(details)
        db_session.commit()

        assert details.set_id == set_obj.id
        assert details.movement_id == test_movement.id
        assert details.reps == 5
        assert details.rir == 2
        assert float(details.external_load_value) == 225.00

    def test_strength_details_minimal_fields(
        self,
        db_session: DBSession,
        test_module: Module,
        test_movement: Movement,
    ) -> None:
        """Test creating strength details with only required fields."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        details = StrengthSetDetails(
            set_id=set_obj.id, movement_id=test_movement.id
        )
        db_session.add(details)
        db_session.commit()

        assert details.set_id == set_obj.id
        assert details.implement_id is None
        assert details.reps is None

    def test_strength_reps_check_constraint(
        self,
        db_session: DBSession,
        test_module: Module,
        test_movement: Movement,
    ) -> None:
        """Test that reps must be >= 0."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        details = StrengthSetDetails(
            set_id=set_obj.id, movement_id=test_movement.id, reps=-1
        )
        db_session.add(details)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_strength_rir_check_constraint(
        self,
        db_session: DBSession,
        test_module: Module,
        test_movement: Movement,
    ) -> None:
        """Test that RIR must be between 0 and 10."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        details = StrengthSetDetails(
            set_id=set_obj.id, movement_id=test_movement.id, rir=11
        )
        db_session.add(details)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_strength_intensity_check_constraint(
        self,
        db_session: DBSession,
        test_module: Module,
        test_movement: Movement,
    ) -> None:
        """Test that intensity_percentage must be between 0 and 100."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        details = StrengthSetDetails(
            set_id=set_obj.id,
            movement_id=test_movement.id,
            intensity_percentage=Decimal("101.00"),
        )
        db_session.add(details)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_strength_cascade_delete_from_set(
        self,
        db_session: DBSession,
        test_module: Module,
        test_movement: Movement,
    ) -> None:
        """Test that deleting a set cascades to strength details."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        details = StrengthSetDetails(
            set_id=set_obj.id, movement_id=test_movement.id, reps=5
        )
        db_session.add(details)
        db_session.commit()

        db_session.delete(set_obj)
        db_session.commit()

        assert db_session.get(StrengthSetDetails, set_obj.id) is None


class TestEnduranceSetDetails:
    """Tests for EnduranceSetDetails model."""

    def test_create_endurance_details(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test creating endurance set details."""
        set_obj = Set(
            module_id=test_module.id, order_in_module=1, set_type=SetTypes.ENDURANCE
        )
        db_session.add(set_obj)
        db_session.commit()

        details = EnduranceSetDetails(
            set_id=set_obj.id,
            quantity_value=Decimal("5000.000"),
            quantity_unit=QuantityUnits.METERS,
            average_cadence=180,
            cadence_unit=CadenceUnits.STEPS_PER_MINUTE,
            pace_seconds=300,
            pace_unit=PaceUnits.PER_MILE,
            energy_value=Decimal("250.000"),
            energy_unit=EnergyUnits.CALORIES,
        )
        db_session.add(details)
        db_session.commit()

        assert details.set_id == set_obj.id
        assert float(details.quantity_value) == 5000.0
        assert details.quantity_unit == QuantityUnits.METERS
        assert details.average_cadence == 180

    def test_endurance_details_with_carry(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test creating endurance details with loaded carry."""
        set_obj = Set(
            module_id=test_module.id, order_in_module=1, set_type=SetTypes.ENDURANCE
        )
        db_session.add(set_obj)
        db_session.commit()

        details = EnduranceSetDetails(
            set_id=set_obj.id,
            quantity_value=Decimal("1000.000"),
            quantity_unit=QuantityUnits.METERS,
            external_load_value=Decimal("50.00"),
            external_load_unit=ExternalLoadUnits.LBS,
            carry_style=CarryStyles.VEST,
        )
        db_session.add(details)
        db_session.commit()

        assert details.carry_style == CarryStyles.VEST
        assert float(details.external_load_value) == 50.0

    def test_endurance_quantity_check_constraint(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test that quantity_value must be >= 0."""
        set_obj = Set(
            module_id=test_module.id, order_in_module=1, set_type=SetTypes.ENDURANCE
        )
        db_session.add(set_obj)
        db_session.commit()

        details = EnduranceSetDetails(
            set_id=set_obj.id, quantity_value=Decimal("-100.000")
        )
        db_session.add(details)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_endurance_cascade_delete_from_set(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test that deleting a set cascades to endurance details."""
        set_obj = Set(
            module_id=test_module.id, order_in_module=1, set_type=SetTypes.ENDURANCE
        )
        db_session.add(set_obj)
        db_session.commit()

        details = EnduranceSetDetails(
            set_id=set_obj.id,
            quantity_value=Decimal("1000.000"),
            quantity_unit=QuantityUnits.METERS,
        )
        db_session.add(details)
        db_session.commit()

        db_session.delete(set_obj)
        db_session.commit()

        assert db_session.get(EnduranceSetDetails, set_obj.id) is None


class TestSetVariation:
    """Tests for SetVariation join table."""

    def test_create_set_variation(
        self,
        db_session: DBSession,
        test_module: Module,
        test_variation: Variation,
    ) -> None:
        """Test creating a set-variation relationship."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        set_var = SetVariation(set_id=set_obj.id, variation_id=test_variation.id)
        db_session.add(set_var)
        db_session.commit()

        assert set_var.set_id == set_obj.id
        assert set_var.variation_id == test_variation.id

    def test_set_variations_relationship(
        self,
        db_session: DBSession,
        test_module: Module,
        test_variation: Variation,
    ) -> None:
        """Test the many-to-many relationship between sets and variations."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        # Add variation to set
        set_obj.variations.append(test_variation)
        db_session.commit()

        # Verify relationship
        assert len(set_obj.variations) == 1
        assert set_obj.variations[0].id == test_variation.id
        assert len(test_variation.sets) == 1
        assert test_variation.sets[0].id == set_obj.id

    def test_set_variation_cascade_delete(
        self,
        db_session: DBSession,
        test_module: Module,
        test_variation: Variation,
    ) -> None:
        """Test that deleting a set cascades to set_variations."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        set_obj.variations.append(test_variation)
        db_session.commit()

        db_session.delete(set_obj)
        db_session.commit()

        # Variation should still exist, but join should be gone
        assert db_session.get(Variation, test_variation.id) is not None
        result = db_session.execute(
            db_session.query(SetVariation)
            .filter_by(set_id=set_obj.id)
            .statement
        ).first()
        assert result is None


class TestRelationships:
    """Tests for relationships between models."""

    def test_module_sets_relationship(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test the Module -> Set relationship."""
        set1 = Set(module_id=test_module.id, order_in_module=1)
        set2 = Set(module_id=test_module.id, order_in_module=2)
        db_session.add_all([set1, set2])
        db_session.commit()

        assert len(test_module.sets) == 2
        assert test_module.sets[0].order_in_module == 1
        assert test_module.sets[1].order_in_module == 2

    def test_set_strength_details_relationship(
        self,
        db_session: DBSession,
        test_module: Module,
        test_movement: Movement,
    ) -> None:
        """Test the Set -> StrengthSetDetails relationship."""
        set_obj = Set(module_id=test_module.id, order_in_module=1)
        db_session.add(set_obj)
        db_session.commit()

        details = StrengthSetDetails(
            set_id=set_obj.id, movement_id=test_movement.id, reps=5
        )
        db_session.add(details)
        db_session.commit()

        assert set_obj.strength_details is not None
        assert set_obj.strength_details.reps == 5
        assert details.set.id == set_obj.id

    def test_set_endurance_details_relationship(
        self, db_session: DBSession, test_module: Module
    ) -> None:
        """Test the Set -> EnduranceSetDetails relationship."""
        set_obj = Set(
            module_id=test_module.id, order_in_module=1, set_type=SetTypes.ENDURANCE
        )
        db_session.add(set_obj)
        db_session.commit()

        details = EnduranceSetDetails(
            set_id=set_obj.id,
            quantity_value=Decimal("1000.000"),
            quantity_unit=QuantityUnits.METERS,
        )
        db_session.add(details)
        db_session.commit()

        assert set_obj.endurance_details is not None
        assert float(set_obj.endurance_details.quantity_value) == 1000.0
        assert details.set.id == set_obj.id
