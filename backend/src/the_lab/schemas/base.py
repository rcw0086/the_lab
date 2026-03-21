"""
Base Pydantic schema classes for API request/response patterns.

Provides foundational schemas that domain-specific schemas inherit from:
- CreateSchema: Base for POST request bodies (no id, no timestamps)
- ReadSchema: Base for API responses (includes id)
- UpdateSchema: Base for PATCH/PUT request bodies (all fields optional)
- ErrorResponse: Standardized error response format
"""

from pydantic import BaseModel, ConfigDict


class CreateSchema(BaseModel):
    """Base schema for resource creation requests.

    Subclasses define the fields required to create a new resource.
    Excludes id and timestamp fields, which are set server-side.

    Usage:
        class DailyCreate(CreateSchema):
            date: date
            user_id: int
            protein: int | None = None
            sleep: float | None = None
    """

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


class ReadSchema(BaseModel):
    """Base schema for API responses representing a resource.

    Includes the resource id. Subclasses add timestamp fields as needed,
    since not all models share the same timestamp columns.
    Uses ``from_attributes=True`` so ORM model instances can be passed directly.

    Usage:
        class DailyRead(ReadSchema):
            date: date
            user_id: int
            protein: int | None = None
            sleep: float | None = None
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int


class UpdateSchema(BaseModel):
    """Base schema for resource update requests.

    Subclasses should declare all mutable fields as optional (with a default
    of ``None``) so that clients can send partial updates. Fields not included
    in the request body remain unchanged.

    Usage:
        class DailyUpdate(UpdateSchema):
            protein: int | None = None
            sleep: float | None = None
    """

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )


class ErrorDetail(BaseModel):
    """Individual error detail within an error response.

    Attributes:
        field: The request field that caused the error, if applicable.
        message: Human-readable description of the error.
    """

    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    """Standardized API error response.

    Provides a consistent structure for all error responses returned by the API.

    Attributes:
        error: Short error type identifier (e.g. "validation_error", "not_found").
        detail: List of individual error details.
    """

    error: str
    detail: list[ErrorDetail]
