"""Training session models.

This module defines models for training sessions and their structure:
- Session: A training session with metadata (zeal, fatigue, timing)
- Module: Ordered segments within a session (supports mixed-modality training)

Reference:
- Schema: docs/the_lab_v0_5.sql lines 178-218
- ADR-008: Support for non-linear training structures
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from the_lab.db.base import Base

if TYPE_CHECKING:
    from the_lab.db.models.sets import Set


class Session(Base):
    """Training session model.

    Represents a single training session with timing, subjective metrics,
    and contextual information. Contains multiple ordered modules.
    """

    __tablename__ = "sessions"

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
        doc="User who performed this session",
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Session start timestamp",
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Session end timestamp",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
        doc="Record creation timestamp",
    )
    training_zeal: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Subjective training intensity (1-10 scale)",
    )
    fatigue_concluding: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Subjective fatigue at session end (1-10 scale)",
    )
    fed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        doc="Whether athlete was fed before session",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Session notes and observations",
    )

    # Relationships
    modules: Mapped[list["Module"]] = relationship(
        "Module",
        back_populates="session",
        order_by="Module.order_in_session",
        cascade="all, delete-orphan",
        doc="Ordered modules within this session",
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "start_time IS NULL OR end_time IS NULL OR end_time >= start_time",
            name="times_ck",
        ),
        CheckConstraint(
            "training_zeal IS NULL OR (training_zeal >= 1 AND training_zeal <= 10)",
            name="training_zeal_ck",
        ),
        CheckConstraint(
            "fatigue_concluding IS NULL OR (fatigue_concluding >= 1 AND fatigue_concluding <= 10)",
            name="fatigue_ck",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Session(id={self.id!r}, user_id={self.user_id!r}, "
            f"start_time={self.start_time!r}, module_count={len(self.modules)})"
        )


class Module(Base):
    """Training module model.

    Represents an ordered segment within a training session.
    Supports mixed-modality sessions (e.g., strength + endurance).
    """

    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(start=1, increment=1),
        primary_key=True,
        doc="Primary key",
    )
    session_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        doc="Parent session",
    )
    order_in_session: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Order of this module within the session (1-based)",
    )
    start_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Module start timestamp",
    )
    end_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Module end timestamp",
    )
    hr_avg: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Average heart rate during module (bpm)",
    )
    hr_max: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Maximum heart rate during module (bpm)",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Module notes and observations",
    )

    # Relationships
    session: Mapped["Session"] = relationship(
        "Session",
        back_populates="modules",
        doc="Parent session",
    )
    sets: Mapped[list["Set"]] = relationship(
        "Set",
        back_populates="module",
        order_by="Set.order_in_module",
        cascade="all, delete-orphan",
        doc="Ordered sets within this module",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("session_id", "order_in_session", name="session_order_uk"),
        CheckConstraint(
            "order_in_session >= 1",
            name="order_ck",
        ),
        CheckConstraint(
            "start_time IS NULL OR end_time IS NULL OR end_time >= start_time",
            name="times_ck",
        ),
        CheckConstraint(
            "(hr_avg IS NULL OR hr_avg > 0) AND (hr_max IS NULL OR hr_max > 0)",
            name="hr_ck",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"Module(id={self.id!r}, session_id={self.session_id!r}, "
            f"order_in_session={self.order_in_session!r})"
        )
