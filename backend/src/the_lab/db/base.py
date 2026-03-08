"""SQLAlchemy declarative base class.

All ORM models should inherit from the Base class defined here.
This enables Alembic to auto-generate migrations by detecting model changes.
"""

from datetime import datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

# Naming convention for constraints to ensure consistent migration generation
# See: https://alembic.sqlalchemy.org/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models.

    Provides:
    - Consistent naming convention for constraints
    - Common timestamp columns (created_at, updated_at) via mixin
    """

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models.

    Usage:
        class MyModel(Base, TimestampMixin):
            __tablename__ = "my_table"
            id: Mapped[int] = mapped_column(primary_key=True)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="Timestamp when record was created",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="Timestamp when record was last updated",
    )

    def __repr__(self) -> str:
        """Generate a helpful repr string for debugging."""
        attrs = []
        for column in self.__mapper__.c:  # type: ignore[attr-defined]
            value = getattr(self, column.key, None)
            attrs.append(f"{column.key}={value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"
