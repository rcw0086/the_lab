"""
Core entity models for The Lab.

Models:
- User: Application users
- Daily: Daily health/nutrition metrics
- Cycle: Training cycles (micro, meso, macro)
- Goal: Training and performance goals
- Injury: Injury tracking and resolution

All models follow ADR-008 (Training Data Domain Philosophy):
- Fact-first data modeling
- Preserve what actually happened
- Support analytical clarity
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from the_lab.db.base import Base
from the_lab.db.enums import CycleTypes

if TYPE_CHECKING:
    from the_lab.db.models.journal import CycleNote, GoalNote, InjuryNote


class User(Base):
    """Application user model.

    Represents authenticated users who track training and health data.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    username: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="Unique username for authentication",
    )
    role: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="User role (e.g., 'admin', 'athlete')",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        doc="Account creation timestamp",
    )

    __table_args__ = (UniqueConstraint("username", name="users_username_uk"),)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r}, role={self.role!r})"


class Daily(Base):
    """Daily health and nutrition tracking model.

    Records day-level metrics like protein intake and sleep hours.
    One record per user per day (enforced by unique constraint).
    """

    __tablename__ = "dailies"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date of the daily record",
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="User this daily record belongs to",
    )
    protein: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Protein intake in grams",
    )
    sleep: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        doc="Sleep duration in hours (0-24)",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="dailies_user_date_uk"),
        CheckConstraint("protein IS NULL OR protein >= 0", name="protein_ck"),
        CheckConstraint(
            "sleep IS NULL OR (sleep >= 0 AND sleep <= 24)",
            name="sleep_ck",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Daily(id={self.id!r}, date={self.date!r}, user_id={self.user_id!r}, "
            f"protein={self.protein!r}, sleep={self.sleep!r})"
        )


class Cycle(Base):
    """Training cycle model.

    Represents training cycles at different time scales (micro, meso, macro).
    Supports periodization and structured training phases.
    """

    __tablename__ = "cycles"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="User this cycle belongs to",
    )
    type: Mapped[CycleTypes | None] = mapped_column(
        Enum(CycleTypes, name="cycle_types", values_callable=lambda x: [e.value for e in x]),
        nullable=True,
        doc="Cycle type (microcycle, mesocycle, macrocycle)",
    )
    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        doc="Cycle start date",
    )
    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        doc="Cycle end date",
    )
    title: Mapped[str | None] = mapped_column(
        String(256),
        nullable=True,
        doc="Cycle title or name",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Cycle notes or description",
    )

    # Relationship to journal notes via join table
    journal_notes: Mapped[list["CycleNote"]] = relationship(
        "CycleNote",
        back_populates="cycle",
        cascade="all, delete-orphan",
        doc="Journal notes associated with this cycle",
    )

    __table_args__ = (
        CheckConstraint(
            "start_date IS NULL OR end_date IS NULL OR end_date >= start_date",
            name="dates_ck",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Cycle(id={self.id!r}, user_id={self.user_id!r}, type={self.type!r}, "
            f"title={self.title!r}, start_date={self.start_date!r}, end_date={self.end_date!r})"
        )


class Goal(Base):
    """Training and performance goal model.

    Tracks goals set by users and their achievement status.
    Supports both achieved and in-progress goals.
    """

    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="User this goal belongs to",
    )
    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        doc="Goal title or description",
    )
    achieved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
        doc="Whether the goal has been achieved",
    )
    date_set: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        doc="Date the goal was set",
    )
    date_achieved: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        doc="Date the goal was achieved",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Goal notes or context",
    )

    # Relationship to journal notes via join table
    journal_notes: Mapped[list["GoalNote"]] = relationship(
        "GoalNote",
        back_populates="goal",
        cascade="all, delete-orphan",
        doc="Journal notes associated with this goal",
    )

    __table_args__ = (
        CheckConstraint(
            "date_set IS NULL OR date_achieved IS NULL OR date_achieved >= date_set",
            name="dates_ck",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Goal(id={self.id!r}, user_id={self.user_id!r}, title={self.title!r}, "
            f"achieved={self.achieved!r})"
        )


class Injury(Base):
    """Injury tracking model.

    Records injuries and their resolution status.
    Supports ongoing and resolved injuries.
    """

    __tablename__ = "injuries"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="User this injury belongs to",
    )
    injury_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Date and time when injury occurred",
    )
    full_resolution: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Date and time when injury was fully resolved",
    )
    title: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        doc="Injury title or description",
    )

    # Relationship to journal notes via join table
    journal_notes: Mapped[list["InjuryNote"]] = relationship(
        "InjuryNote",
        back_populates="injury",
        cascade="all, delete-orphan",
        doc="Journal notes associated with this injury",
    )

    __table_args__ = (
        CheckConstraint(
            "injury_date IS NULL OR full_resolution IS NULL OR full_resolution >= injury_date",
            name="dates_ck",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Injury(id={self.id!r}, user_id={self.user_id!r}, title={self.title!r}, "
            f"injury_date={self.injury_date!r}, full_resolution={self.full_resolution!r})"
        )
