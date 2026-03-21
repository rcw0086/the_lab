"""
Pydantic schemas for The Lab API.

Provides request/response schemas organized by domain:
- base: Base schema classes for Create, Read, Update patterns
"""

from the_lab.schemas.base import (
    CreateSchema,
    ErrorDetail,
    ErrorResponse,
    ReadSchema,
    UpdateSchema,
)

__all__ = [
    "CreateSchema",
    "ErrorDetail",
    "ErrorResponse",
    "ReadSchema",
    "UpdateSchema",
]
