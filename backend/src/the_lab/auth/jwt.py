"""JWT token generation and validation."""

from datetime import UTC, datetime, timedelta
from typing import Any, Literal

from jose import JWTError, jwt

from the_lab.config import get_settings
from the_lab.logging import get_logger

logger = get_logger(__name__)


class TokenError(Exception):
    """Raised when a token is invalid or expired."""


def create_access_token(user_id: int, username: str, role: str | None = None) -> str:
    """Create a short-lived JWT access token.

    Args:
        user_id: The user's database ID.
        username: The user's username.
        role: The user's role (e.g. "admin", "athlete").

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }
    result: str = jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return result


def create_refresh_token(user_id: int) -> str:
    """Create a long-lived JWT refresh token.

    Args:
        user_id: The user's database ID.

    Returns:
        Encoded JWT string.
    """
    settings = get_settings()
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=settings.jwt_refresh_token_expire_days),
    }
    result: str = jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return result


def verify_token(token: str, expected_type: Literal["access", "refresh"] = "access") -> dict[str, Any]:
    """Decode and validate a JWT token.

    Args:
        token: The encoded JWT string.
        expected_type: Expected token type ("access" or "refresh").

    Returns:
        The decoded claims dictionary.

    Raises:
        TokenError: If the token is invalid, expired, or has the wrong type.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        logger.warning("token_validation_failed", error=str(exc))
        raise TokenError("Invalid or expired token") from exc

    if payload.get("type") != expected_type:
        logger.warning("token_type_mismatch", expected=expected_type, got=payload.get("type"))
        raise TokenError("Invalid token type")

    result: dict[str, Any] = payload
    return result
