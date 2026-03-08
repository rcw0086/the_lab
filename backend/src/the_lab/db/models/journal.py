"""Journal notes system models.

This module defines models for the journal notes system:
- Note: Base note entity with user and date
- GoalNote: Many-to-many join table between goals and notes
- CycleNote: Many-to-many join table between cycles and notes
- InjuryNote: Many-to-many join table between injuries and notes

Reference:
- Schema: docs/the_lab_v0_5.sql lines 144-171
- Indexes: docs/the_lab_v0_5.sql lines 365-368
"""

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from the_lab.db.base import Base

if TYPE_CHECKING:
    from the_lab.db.models.core import Cycle, Goal, Injury


class Note(Base):
    """Journal note model.

    Represents a user's journal entry with a date and text content.
    Can be linked to multiple entities (goals, cycles, injuries) via join tables.
    """

    __tablename__ = "notes"

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
        doc="User who created this note",
    )
    entry_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        doc="Date of the journal entry",
    )
    title: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Optional note title",
    )
    body: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Note content",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        doc="Record creation timestamp",
    )

    # Relationships to associated entities via join tables
    goals: Mapped[list["GoalNote"]] = relationship(
        "GoalNote",
        back_populates="note",
        cascade="all, delete-orphan",
        doc="Goals associated with this note",
    )
    cycles: Mapped[list["CycleNote"]] = relationship(
        "CycleNote",
        back_populates="note",
        cascade="all, delete-orphan",
        doc="Cycles associated with this note",
    )
    injuries: Mapped[list["InjuryNote"]] = relationship(
        "InjuryNote",
        back_populates="note",
        cascade="all, delete-orphan",
        doc="Injuries associated with this note",
    )

    __table_args__ = (
        CheckConstraint(
            "entry_date >= DATE '1900-01-01'",
            name="entry_date_ck",
        ),
        # Index for chronological queries by user
        Index("idx_notes_user_date", "user_id", "entry_date"),
    )

    def __repr__(self) -> str:
        return (
            f"Note(id={self.id!r}, user_id={self.user_id!r}, "
            f"entry_date={self.entry_date!r}, title={self.title!r})"
        )


class GoalNote(Base):
    """Goal-to-note join table.

    Many-to-many relationship between goals and notes.
    Allows linking journal entries to specific goals.
    """

    __tablename__ = "goal_notes"

    goal_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("goals.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Goal being annotated",
    )
    note_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Note associated with the goal",
    )

    # Relationships for bidirectional navigation
    note: Mapped["Note"] = relationship(
        "Note",
        back_populates="goals",
        doc="Note associated with this goal",
    )
    goal: Mapped["Goal"] = relationship(
        "Goal",
        back_populates="journal_notes",
        doc="Goal associated with this note",
    )

    __table_args__ = (
        # Index for reverse lookups (find all goals for a note)
        Index("idx_goal_notes_note", "note_id"),
    )

    def __repr__(self) -> str:
        return f"GoalNote(goal_id={self.goal_id!r}, note_id={self.note_id!r})"


class CycleNote(Base):
    """Cycle-to-note join table.

    Many-to-many relationship between cycles and notes.
    Allows linking journal entries to specific training cycles.
    """

    __tablename__ = "cycle_notes"

    cycle_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("cycles.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Cycle being annotated",
    )
    note_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Note associated with the cycle",
    )

    # Relationships for bidirectional navigation
    note: Mapped["Note"] = relationship(
        "Note",
        back_populates="cycles",
        doc="Note associated with this cycle",
    )
    cycle: Mapped["Cycle"] = relationship(
        "Cycle",
        back_populates="journal_notes",
        doc="Cycle associated with this note",
    )

    __table_args__ = (
        # Index for reverse lookups (find all cycles for a note)
        Index("idx_cycle_notes_note", "note_id"),
    )

    def __repr__(self) -> str:
        return f"CycleNote(cycle_id={self.cycle_id!r}, note_id={self.note_id!r})"


class InjuryNote(Base):
    """Injury-to-note join table.

    Many-to-many relationship between injuries and notes.
    Allows linking journal entries to specific injuries.
    """

    __tablename__ = "injury_notes"

    injury_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("injuries.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Injury being annotated",
    )
    note_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("notes.id", ondelete="CASCADE"),
        primary_key=True,
        doc="Note associated with the injury",
    )

    # Relationships for bidirectional navigation
    note: Mapped["Note"] = relationship(
        "Note",
        back_populates="injuries",
        doc="Note associated with this injury",
    )
    injury: Mapped["Injury"] = relationship(
        "Injury",
        back_populates="journal_notes",
        doc="Injury associated with this note",
    )

    __table_args__ = (
        # Index for reverse lookups (find all injuries for a note)
        Index("idx_injury_notes_note", "note_id"),
    )

    def __repr__(self) -> str:
        return f"InjuryNote(injury_id={self.injury_id!r}, note_id={self.note_id!r})"
