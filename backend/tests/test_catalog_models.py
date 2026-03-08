"""Tests for movement catalog models.

Tests cover:
- Model instantiation
- Constraint validation (unique constraints)
- Relationships (VariationType <-> Variation)
- Foreign key constraints
- Database operations
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from the_lab.db.models.catalog import (
    Implement,
    Movement,
    Variation,
    VariationType,
)


class TestMovement:
    """Tests for Movement model."""

    def test_create_movement(self, db_session: Session) -> None:
        """Test creating a movement with required fields."""
        movement = Movement(name="Squat")
        db_session.add(movement)
        db_session.commit()

        assert movement.id is not None
        assert movement.name == "Squat"

    def test_movement_name_unique_constraint(self, db_session: Session) -> None:
        """Test that movement name must be unique."""
        movement1 = Movement(name="Press")
        db_session.add(movement1)
        db_session.commit()

        movement2 = Movement(name="Press")
        db_session.add(movement2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_movement_repr(self, db_session: Session) -> None:
        """Test movement string representation."""
        movement = Movement(name="Row")
        db_session.add(movement)
        db_session.commit()

        repr_str = repr(movement)
        assert "Movement" in repr_str
        assert "Row" in repr_str
        assert str(movement.id) in repr_str


class TestImplement:
    """Tests for Implement model."""

    def test_create_implement(self, db_session: Session) -> None:
        """Test creating an implement with required fields."""
        implement = Implement(name="Barbell")
        db_session.add(implement)
        db_session.commit()

        assert implement.id is not None
        assert implement.name == "Barbell"

    def test_implement_name_unique_constraint(self, db_session: Session) -> None:
        """Test that implement name must be unique."""
        implement1 = Implement(name="Kettlebell")
        db_session.add(implement1)
        db_session.commit()

        implement2 = Implement(name="Kettlebell")
        db_session.add(implement2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_implement_repr(self, db_session: Session) -> None:
        """Test implement string representation."""
        implement = Implement(name="Dumbbell")
        db_session.add(implement)
        db_session.commit()

        repr_str = repr(implement)
        assert "Implement" in repr_str
        assert "Dumbbell" in repr_str
        assert str(implement.id) in repr_str


class TestVariationType:
    """Tests for VariationType model."""

    def test_create_variation_type(self, db_session: Session) -> None:
        """Test creating a variation type with required fields."""
        variation_type = VariationType(name="Stance")
        db_session.add(variation_type)
        db_session.commit()

        assert variation_type.id is not None
        assert variation_type.name == "Stance"

    def test_variation_type_name_unique_constraint(
        self, db_session: Session
    ) -> None:
        """Test that variation type name must be unique."""
        vtype1 = VariationType(name="Tempo")
        db_session.add(vtype1)
        db_session.commit()

        vtype2 = VariationType(name="Tempo")
        db_session.add(vtype2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_variation_type_repr(self, db_session: Session) -> None:
        """Test variation type string representation."""
        variation_type = VariationType(name="Grip")
        db_session.add(variation_type)
        db_session.commit()

        repr_str = repr(variation_type)
        assert "VariationType" in repr_str
        assert "Grip" in repr_str
        assert str(variation_type.id) in repr_str


class TestVariation:
    """Tests for Variation model."""

    def test_create_variation(self, db_session: Session) -> None:
        """Test creating a variation with required fields."""
        # Create variation type first
        vtype = VariationType(name="Stance")
        db_session.add(vtype)
        db_session.commit()

        # Create variation
        variation = Variation(variation_type_id=vtype.id, name="Wide")
        db_session.add(variation)
        db_session.commit()

        assert variation.id is not None
        assert variation.variation_type_id == vtype.id
        assert variation.name == "Wide"

    def test_variation_type_name_unique_constraint(
        self, db_session: Session
    ) -> None:
        """Test that (variation_type_id, name) must be unique."""
        # Create variation type
        vtype = VariationType(name="Stance")
        db_session.add(vtype)
        db_session.commit()

        # Create first variation
        variation1 = Variation(variation_type_id=vtype.id, name="Close")
        db_session.add(variation1)
        db_session.commit()

        # Try to create duplicate
        variation2 = Variation(variation_type_id=vtype.id, name="Close")
        db_session.add(variation2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_variation_same_name_different_types(
        self, db_session: Session
    ) -> None:
        """Test that same name can exist under different variation types."""
        # Create two variation types
        vtype1 = VariationType(name="Stance")
        vtype2 = VariationType(name="Tempo")
        db_session.add_all([vtype1, vtype2])
        db_session.commit()

        # Create variations with same name under different types
        variation1 = Variation(variation_type_id=vtype1.id, name="Wide")
        variation2 = Variation(variation_type_id=vtype2.id, name="Wide")
        db_session.add_all([variation1, variation2])
        db_session.commit()

        # Both should succeed
        assert variation1.id is not None
        assert variation2.id is not None
        assert variation1.id != variation2.id

    def test_variation_foreign_key_restrict(self, db_session: Session) -> None:
        """Test that deleting variation type is restricted if variations exist."""
        # Create variation type and variation
        vtype = VariationType(name="Tempo")
        db_session.add(vtype)
        db_session.commit()

        variation = Variation(variation_type_id=vtype.id, name="Pause")
        db_session.add(variation)
        db_session.commit()

        # Try to delete variation type
        db_session.delete(vtype)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_variation_invalid_type_id(self, db_session: Session) -> None:
        """Test that creating variation with invalid type_id fails."""
        variation = Variation(variation_type_id=999999, name="Invalid")
        db_session.add(variation)
        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_variation_repr(self, db_session: Session) -> None:
        """Test variation string representation."""
        vtype = VariationType(name="Grip")
        db_session.add(vtype)
        db_session.commit()

        variation = Variation(variation_type_id=vtype.id, name="Pronated")
        db_session.add(variation)
        db_session.commit()

        repr_str = repr(variation)
        assert "Variation" in repr_str
        assert "Pronated" in repr_str
        assert str(variation.id) in repr_str
        assert str(vtype.id) in repr_str


class TestCatalogRelationships:
    """Tests for relationships between catalog models."""

    def test_variation_type_to_variations_relationship(
        self, db_session: Session
    ) -> None:
        """Test that VariationType.variations relationship works."""
        # Create variation type
        vtype = VariationType(name="Stance")
        db_session.add(vtype)
        db_session.commit()

        # Create multiple variations
        var1 = Variation(variation_type_id=vtype.id, name="Close")
        var2 = Variation(variation_type_id=vtype.id, name="Wide")
        var3 = Variation(variation_type_id=vtype.id, name="Split")
        db_session.add_all([var1, var2, var3])
        db_session.commit()

        # Refresh to load relationships
        db_session.refresh(vtype)

        # Check relationship
        assert len(vtype.variations) == 3
        variation_names = {v.name for v in vtype.variations}
        assert variation_names == {"Close", "Wide", "Split"}

    def test_variation_to_variation_type_relationship(
        self, db_session: Session
    ) -> None:
        """Test that Variation.variation_type relationship works."""
        # Create variation type
        vtype = VariationType(name="Tempo")
        db_session.add(vtype)
        db_session.commit()

        # Create variation
        variation = Variation(variation_type_id=vtype.id, name="Pause")
        db_session.add(variation)
        db_session.commit()

        # Refresh to load relationships
        db_session.refresh(variation)

        # Check relationship
        assert variation.variation_type is not None
        assert variation.variation_type.id == vtype.id
        assert variation.variation_type.name == "Tempo"


class TestCatalogExampleData:
    """Tests using example data from issue #30."""

    def test_example_squat_variations(self, db_session: Session) -> None:
        """Test creating the squat example from the issue."""
        # Create movement
        movement = Movement(name="Squat")
        db_session.add(movement)

        # Create implement
        implement = Implement(name="Barbell")
        db_session.add(implement)

        # Create stance variations
        stance_type = VariationType(name="Stance")
        db_session.add(stance_type)
        db_session.commit()

        stance_variations = [
            Variation(variation_type_id=stance_type.id, name="Close"),
            Variation(variation_type_id=stance_type.id, name="Wide"),
            Variation(variation_type_id=stance_type.id, name="Split"),
        ]
        db_session.add_all(stance_variations)

        # Create tempo variations
        tempo_type = VariationType(name="Tempo")
        db_session.add(tempo_type)
        db_session.commit()

        tempo_variations = [
            Variation(variation_type_id=tempo_type.id, name="Pause"),
            Variation(variation_type_id=tempo_type.id, name="1-1-1"),
            Variation(variation_type_id=tempo_type.id, name="3-0-1"),
        ]
        db_session.add_all(tempo_variations)
        db_session.commit()

        # Verify everything was created
        assert db_session.query(Movement).count() == 1
        assert db_session.query(Implement).count() == 1
        assert db_session.query(VariationType).count() == 2
        assert db_session.query(Variation).count() == 6

        # Verify stance variations
        db_session.refresh(stance_type)
        assert len(stance_type.variations) == 3

        # Verify tempo variations
        db_session.refresh(tempo_type)
        assert len(tempo_type.variations) == 3
