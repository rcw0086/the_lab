"""Tests for JWT token generation and validation."""

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from the_lab.auth.jwt import (
    TokenError,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from the_lab.config import get_settings


class TestCreateAccessToken:
    """Tests for create_access_token()."""

    def test_returns_string(self) -> None:
        token = create_access_token(user_id=1, username="alice")
        assert isinstance(token, str)

    def test_contains_expected_claims(self) -> None:
        settings = get_settings()
        token = create_access_token(user_id=42, username="alice", role="athlete")
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        assert payload["sub"] == "42"
        assert payload["username"] == "alice"
        assert payload["role"] == "athlete"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_sub_is_string(self) -> None:
        settings = get_settings()
        token = create_access_token(user_id=7, username="bob")
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "7"

    def test_role_defaults_to_none(self) -> None:
        settings = get_settings()
        token = create_access_token(user_id=1, username="alice")
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["role"] is None

    def test_expiration_is_set(self) -> None:
        settings = get_settings()
        before = datetime.now(UTC)
        token = create_access_token(user_id=1, username="alice")
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        exp = datetime.fromtimestamp(payload["exp"], tz=UTC)
        expected = before + timedelta(minutes=settings.jwt_access_token_expire_minutes)
        # Allow 5 seconds of drift
        assert abs((exp - expected).total_seconds()) < 5


class TestCreateRefreshToken:
    """Tests for create_refresh_token()."""

    def test_returns_string(self) -> None:
        token = create_refresh_token(user_id=1)
        assert isinstance(token, str)

    def test_contains_expected_claims(self) -> None:
        settings = get_settings()
        token = create_refresh_token(user_id=42)
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        assert payload["sub"] == "42"
        assert payload["type"] == "refresh"
        assert "exp" in payload
        assert "iat" in payload
        assert "username" not in payload
        assert "role" not in payload

    def test_expiration_is_longer_than_access(self) -> None:
        settings = get_settings()
        access = create_access_token(user_id=1, username="alice")
        refresh = create_refresh_token(user_id=1)

        access_payload = jwt.decode(access, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        refresh_payload = jwt.decode(refresh, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

        assert refresh_payload["exp"] > access_payload["exp"]


class TestVerifyToken:
    """Tests for verify_token()."""

    def test_valid_access_token(self) -> None:
        token = create_access_token(user_id=1, username="alice", role="admin")
        payload = verify_token(token, expected_type="access")

        assert payload["sub"] == "1"
        assert payload["username"] == "alice"
        assert payload["role"] == "admin"

    def test_valid_refresh_token(self) -> None:
        token = create_refresh_token(user_id=1)
        payload = verify_token(token, expected_type="refresh")

        assert payload["sub"] == "1"
        assert payload["type"] == "refresh"

    def test_defaults_to_access_type(self) -> None:
        token = create_access_token(user_id=1, username="alice")
        payload = verify_token(token)
        assert payload["type"] == "access"

    def test_wrong_type_raises(self) -> None:
        token = create_access_token(user_id=1, username="alice")
        with pytest.raises(TokenError, match="Invalid token type"):
            verify_token(token, expected_type="refresh")

    def test_refresh_as_access_raises(self) -> None:
        token = create_refresh_token(user_id=1)
        with pytest.raises(TokenError, match="Invalid token type"):
            verify_token(token, expected_type="access")

    def test_expired_token_raises(self) -> None:
        settings = get_settings()
        claims = {
            "sub": "1",
            "username": "alice",
            "type": "access",
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "exp": datetime.now(UTC) - timedelta(hours=1),
        }
        token = jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

        with pytest.raises(TokenError, match="Invalid or expired token"):
            verify_token(token)

    def test_invalid_signature_raises(self) -> None:
        settings = get_settings()
        claims = {
            "sub": "1",
            "username": "alice",
            "type": "access",
            "iat": datetime.now(UTC),
            "exp": datetime.now(UTC) + timedelta(hours=1),
        }
        token = jwt.encode(claims, "wrong-secret-key", algorithm=settings.jwt_algorithm)

        with pytest.raises(TokenError, match="Invalid or expired token"):
            verify_token(token)

    def test_malformed_token_raises(self) -> None:
        with pytest.raises(TokenError, match="Invalid or expired token"):
            verify_token("not.a.valid.token")

    def test_empty_token_raises(self) -> None:
        with pytest.raises(TokenError, match="Invalid or expired token"):
            verify_token("")
