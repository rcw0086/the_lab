"""Movement catalog models for The Lab.

Models:
- Movement: Fundamental movement patterns (squat, press, pull, etc.)
- Implement: Equipment used for movements (barbell, dumbbell, etc.)
- VariationType: Categories of variations (tempo, stance, grip, etc.)
- Variation: Specific variations grouped by type

This catalog provides a flexible taxonomy for exercises without hard-coding
specific exercise names. Follows ADR-008: Do not overfit to any one training
philosophy.

Example usage:
    Movement("Squat") + Implement("Barbell") + Variation("Wide", type="Stance")
    = "Wide-stance Barbell Squat"
"""

from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Identity,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from the_lab.db.base import Base

if TYPE_CHECKING:
    from the_lab.db.models.sets import Set


class Movement(Base):
    """Fundamental movement pattern model.

    Represents core movement patterns (squat, hinge, press, pull, carry, etc.)
    that form the basis of exercise taxonomy.
    """

    __tablename__ = "movements"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        doc="Movement pattern name (e.g., 'Squat', 'Press', 'Row')",
    )

    __table_args__ = (UniqueConstraint("name", name="movements_name_uk"),)

    def __repr__(self) -> str:
        return f"Movement(id={self.id!r}, name={self.name!r})"


class Implement(Base):
    """Exercise implement (equipment) model.

    Represents equipment used to perform movements (barbell, dumbbell,
    kettlebell, bodyweight, etc.).
    """

    __tablename__ = "implements"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Implement name (e.g., 'Barbell', 'Kettlebell', 'Dumbbell')",
    )

    __table_args__ = (UniqueConstraint("name", name="implements_name_uk"),)

    def __repr__(self) -> str:
        return f"Implement(id={self.id!r}, name={self.name!r})"


class VariationType(Base):
    """Variation type (category) model.

    Represents categories of exercise variations (tempo, stance, grip, etc.).
    Variations are grouped by type to provide structure.
    """

    __tablename__ = "variation_types"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Variation type name (e.g., 'Tempo', 'Stance', 'Grip')",
    )

    # Relationship to variations
    variations: Mapped[list["Variation"]] = relationship(
        "Variation",
        back_populates="variation_type",
        doc="Variations belonging to this type",
    )

    __table_args__ = (UniqueConstraint("name", name="variation_types_name_uk"),)

    def __repr__(self) -> str:
        return f"VariationType(id={self.id!r}, name={self.name!r})"


class Variation(Base):
    """Exercise variation model.

    Represents specific variations grouped by type. Examples:
    - VariationType="Stance": "Close", "Wide", "Split"
    - VariationType="Tempo": "Pause", "1-1-1", "3-0-1"
    - VariationType="Grip": "Pronated", "Supinated", "Neutral"
    """

    __tablename__ = "variations"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    variation_type_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("variation_types.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Foreign key to variation_types",
    )
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        doc="Variation name (e.g., 'Close', 'Wide', 'Pause')",
    )

    # Relationship to variation type
    variation_type: Mapped["VariationType"] = relationship(
        "VariationType",
        back_populates="variations",
        doc="The variation type this variation belongs to",
    )

    # Relationship to sets (many-to-many via set_variations)
    sets: Mapped[list["Set"]] = relationship(
        "Set",
        secondary="set_variations",
        back_populates="variations",
        doc="Sets that use this variation",
    )

    __table_args__ = (
        UniqueConstraint(
            "variation_type_id",
            "name",
            name="variations_type_name_uk",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Variation(id={self.id!r}, variation_type_id={self.variation_type_id!r}, "
            f"name={self.name!r})"
        )
