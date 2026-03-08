"""Sets system models.

This module defines the sets tracking system:
- Set: Base set entity with type, ordering, and heart rate data
- StrengthSetDetails: Strength-specific details (reps, load, RIR, etc.)
- EnduranceSetDetails: Endurance-specific details (distance, pace, cadence, etc.)
- SetVariation: Many-to-many join table for set variations

The sets system uses a base + detail pattern where set_type determines
which detail table contains the specific metrics.

Reference:
- Schema: docs/the_lab_v0_5.sql lines 259-348
- Indexes: docs/the_lab_v0_5.sql lines 355-363
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from the_lab.db.base import Base
from the_lab.db.enums import (
    CadenceUnits,
    CarryStyles,
    EnergyUnits,
    ExternalLoadUnits,
    PaceUnits,
    QuantityUnits,
    SetTypes,
)

if TYPE_CHECKING:
    from the_lab.db.models.catalog import Implement, Movement, Variation
    from the_lab.db.models.session import Module


class Set(Base):
    """Base set model.

    Represents a single set within a training module.
    May be strength, endurance, or other type (determined by set_type).
    Detail-specific data stored in corresponding detail tables.
    """

    __tablename__ = "sets"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    module_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent module",
    )
    order_in_module: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Order of this set within the module (1-based)",
    )
    set_type: Mapped[SetTypes] = mapped_column(
        Enum(SetTypes, name="set_types", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        server_default="strength",
        doc="Type of set (strength, endurance, other)",
    )
    parent_set_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("sets.id", ondelete="SET NULL"),
        nullable=True,
        doc="Optional parent set for hierarchical relationships (supersets, clusters)",
    )
    rest_period_prior_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Rest period before this set in seconds",
    )
    hr_avg: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Average heart rate during set (bpm)",
    )
    hr_min: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Minimum heart rate during set (bpm)",
    )
    hr_max: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Maximum heart rate during set (bpm)",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Set notes and observations",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        doc="Record creation timestamp",
    )

    # Relationships
    module: Mapped["Module"] = relationship(
        "Module",
        back_populates="sets",
        doc="Parent module",
    )
    parent_set: Mapped["Set | None"] = relationship(
        "Set",
        remote_side=[id],
        back_populates="child_sets",
        doc="Parent set for hierarchical relationships",
    )
    child_sets: Mapped[list["Set"]] = relationship(
        "Set",
        back_populates="parent_set",
        cascade="all, delete-orphan",
        doc="Child sets in hierarchical relationships",
    )
    strength_details: Mapped["StrengthSetDetails | None"] = relationship(
        "StrengthSetDetails",
        back_populates="set",
        uselist=False,
        cascade="all, delete-orphan",
        doc="Strength-specific details",
    )
    endurance_details: Mapped["EnduranceSetDetails | None"] = relationship(
        "EnduranceSetDetails",
        back_populates="set",
        uselist=False,
        cascade="all, delete-orphan",
        doc="Endurance-specific details",
    )
    variations: Mapped[list["Variation"]] = relationship(
        "Variation",
        secondary="set_variations",
        back_populates="sets",
        doc="Variations applied to this set",
    )

    __table_args__ = (
        UniqueConstraint("module_id", "order_in_module", name="module_order_uk"),
        CheckConstraint("order_in_module >= 1", name="order_ck"),
        CheckConstraint(
            "rest_period_prior_seconds IS NULL OR rest_period_prior_seconds >= 0",
            name="rest_ck",
        ),
        CheckConstraint(
            "(hr_avg IS NULL OR hr_avg > 0) AND "
            "(hr_min IS NULL OR hr_min > 0) AND "
            "(hr_max IS NULL OR hr_max > 0)",
            name="hr_ck",
        ),
        # Index for ordered retrieval of sets within a module
        Index("idx_sets_module_order", "module_id", "order_in_module"),
        # Index for hierarchical queries (finding sets in a superset/cluster)
        Index("idx_sets_parent", "parent_set_id"),
    )

    def __repr__(self) -> str:
        return (
            f"Set(id={self.id!r}, module_id={self.module_id!r}, "
            f"order_in_module={self.order_in_module!r}, set_type={self.set_type!r})"
        )


class StrengthSetDetails(Base):
    """Strength set details model.

    Contains strength-specific metrics for a set:
    - Movement and implement
    - External load (weight)
    - Reps and RIR (Reps In Reserve)
    - Intensity percentage
    - Tempo
    - Special technique counts (myo reps, cheated reps, negatives)
    """

    __tablename__ = "strength_set_details"

    set_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sets.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Corresponding set",
    )
    movement_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("movements.id", ondelete="RESTRICT"),
        nullable=False,
        doc="Movement performed",
    )
    implement_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("implements.id", ondelete="RESTRICT"),
        nullable=True,
        doc="Optional implement used",
    )
    external_load_value: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        doc="External load value",
    )
    external_load_unit: Mapped[ExternalLoadUnits | None] = mapped_column(
        Enum(ExternalLoadUnits, name="external_load_units", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="External load unit",
    )
    external_load_desc: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        doc="External load description for non-standard loads",
    )
    reps: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Repetitions completed",
    )
    rir: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Reps in reserve (0-10 scale)",
    )
    intensity_percentage: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Intensity as percentage of 1RM",
    )
    tempo: Mapped[str | None] = mapped_column(
        String(8),
        nullable=True,
        doc="Tempo notation (e.g., '3010')",
    )
    myo_reps_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Number of myo reps performed",
    )
    cheated_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Number of cheated reps",
    )
    negatives_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Number of negative reps",
    )

    # Relationships
    set: Mapped["Set"] = relationship(
        "Set",
        back_populates="strength_details",
        doc="Parent set",
    )
    movement: Mapped["Movement"] = relationship(
        "Movement",
        doc="Movement performed",
    )
    implement: Mapped["Implement | None"] = relationship(
        "Implement",
        doc="Implement used",
    )

    __table_args__ = (
        CheckConstraint("reps IS NULL OR reps >= 0", name="reps_ck"),
        CheckConstraint("rir IS NULL OR (rir >= 0 AND rir <= 10)", name="rir_ck"),
        CheckConstraint(
            "intensity_percentage IS NULL OR "
            "(intensity_percentage >= 0 AND intensity_percentage <= 100)",
            name="intensity_ck",
        ),
        CheckConstraint(
            "(myo_reps_count IS NULL OR myo_reps_count >= 0) AND "
            "(cheated_count IS NULL OR cheated_count >= 0) AND "
            "(negatives_count IS NULL OR negatives_count >= 0)",
            name="counts_ck",
        ),
        CheckConstraint(
            "external_load_value IS NULL OR external_load_value >= 0",
            name="load_ck",
        ),
        # Index for filtering by movement
        Index("idx_strength_movement", "movement_id"),
        # Composite index for movement + implement queries
        Index("idx_strength_movement_implement", "movement_id", "implement_id"),
        # Index for RIR-based analysis
        Index("idx_strength_rir", "rir"),
    )

    def __repr__(self) -> str:
        return (
            f"StrengthSetDetails(set_id={self.set_id!r}, movement_id={self.movement_id!r}, "
            f"reps={self.reps!r}, rir={self.rir!r})"
        )


class EnduranceSetDetails(Base):
    """Endurance set details model.

    Contains endurance-specific metrics for a set:
    - Quantity (distance, time)
    - Cadence
    - Pace
    - Energy expenditure
    - External load (for weighted vests, carries)
    """

    __tablename__ = "endurance_set_details"

    set_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sets.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Corresponding set",
    )
    quantity_value: Mapped[float | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
        doc="Quantity value (distance or time)",
    )
    quantity_unit: Mapped[QuantityUnits | None] = mapped_column(
        Enum(QuantityUnits, name="quantity_units", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="Quantity unit",
    )
    average_cadence: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Average cadence",
    )
    cadence_unit: Mapped[CadenceUnits | None] = mapped_column(
        Enum(CadenceUnits, name="cadence_units", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="Cadence unit",
    )
    pace_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Pace in seconds",
    )
    pace_unit: Mapped[PaceUnits | None] = mapped_column(
        Enum(PaceUnits, name="pace_units", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="Pace unit",
    )
    energy_value: Mapped[float | None] = mapped_column(
        Numeric(12, 3),
        nullable=True,
        doc="Energy expenditure value",
    )
    energy_unit: Mapped[EnergyUnits | None] = mapped_column(
        Enum(EnergyUnits, name="energy_units", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="Energy unit",
    )
    external_load_value: Mapped[float | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        doc="External load value (for weighted vests, carries)",
    )
    external_load_unit: Mapped[ExternalLoadUnits | None] = mapped_column(
        Enum(ExternalLoadUnits, name="external_load_units", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="External load unit",
    )
    carry_style: Mapped[CarryStyles | None] = mapped_column(
        Enum(CarryStyles, name="carry_styles", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="Carry style (for loaded carries)",
    )

    # Relationships
    set: Mapped["Set"] = relationship(
        "Set",
        back_populates="endurance_details",
        doc="Parent set",
    )

    __table_args__ = (
        CheckConstraint(
            "quantity_value IS NULL OR quantity_value >= 0",
            name="quantity_ck",
        ),
        CheckConstraint(
            "average_cadence IS NULL OR average_cadence >= 0",
            name="cadence_ck",
        ),
        CheckConstraint(
            "pace_seconds IS NULL OR pace_seconds >= 0",
            name="pace_ck",
        ),
        CheckConstraint(
            "energy_value IS NULL OR energy_value >= 0",
            name="energy_ck",
        ),
        CheckConstraint(
            "external_load_value IS NULL OR external_load_value >= 0",
            name="load_ck",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"EnduranceSetDetails(set_id={self.set_id!r}, "
            f"quantity_value={self.quantity_value!r}, quantity_unit={self.quantity_unit!r})"
        )


class SetVariation(Base):
    """Set-to-variation join table.

    Many-to-many relationship between sets and variations.
    Allows attaching multiple variation descriptors to a set
    (e.g., "Wide Grip" + "Pause Reps").
    """

    __tablename__ = "set_variations"

    set_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sets.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Set being varied",
    )
    variation_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("variations.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Variation applied to the set",
    )

    __table_args__ = (
        # Index for forward lookups (find all variations for a set)
        Index("idx_set_variations_set", "set_id"),
        # Index for reverse lookups (find all sets with a variation)
        Index("idx_set_variations_variation", "variation_id"),
    )

    def __repr__(self) -> str:
        return f"SetVariation(set_id={self.set_id!r}, variation_id={self.variation_id!r})"
