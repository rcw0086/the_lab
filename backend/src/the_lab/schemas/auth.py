"""Authentication request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from the_lab.schemas.base import CreateSchema, ReadSchema


class RegisterRequest(CreateSchema):
    """Schema for POST /auth/register."""

    username: str = Field(min_length=3, max_length=128)
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(CreateSchema):
    """Schema for POST /auth/login."""

    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    """Schema for token responses."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserRead(ReadSchema):
    """Schema for user responses (excludes password_hash)."""

    username: str
    role: str | None = None
    created_at: datetime
