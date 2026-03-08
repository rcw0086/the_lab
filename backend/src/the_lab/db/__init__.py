"""Database infrastructure for The Lab.

This module provides the core SQLAlchemy infrastructure including:
- Declarative Base class for all ORM models
- Database engine configuration
- Session factory and dependency injection for FastAPI
- PostgreSQL enum types as Python enums
"""

from the_lab.db.base import Base
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
from the_lab.db.session import SessionLocal, engine, get_db

__all__ = [
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    # Enums
    "CadenceUnits",
    "CarryStyles",
    "CycleTypes",
    "EnergyUnits",
    "ExternalLoadUnits",
    "PaceUnits",
    "QuantityUnits",
    "SetTypes",
    "Sides",
]
