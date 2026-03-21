"""Integration tests for GET /auth/me (auth dependency)."""

import os
from datetime import UTC, datetime, timedelta

os.environ["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-characters-long-for-testing"
)

from jose import jwt

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from the_lab.db.session import get_db
from the_lab.main import create_app


def _make_client(db_session: Session) -> TestClient:
    """Create a test client with the DB session overridden."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


def _register_user(client: TestClient, username: str = "authuser", password: str = "securepass123") -> None:
    """Register a user via the API so they have a real bcrypt hash."""
    response = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 201


def _login_user(client: TestClient, username: str = "authuser", password: str = "securepass123") -> dict:
    """Login and return the token response."""
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    return response.json()


class TestAuthDependency:
    """Tests for GET /auth/me (get_current_user dependency)."""

    def test_me_with_valid_token(self, db_session: Session) -> None:
        """Valid access token returns 200 and user data."""
        client = _make_client(db_session)
        _register_user(client)
        tokens = _login_user(client)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "authuser"
        assert "id" in data
        assert "created_at" in data

    def test_me_without_auth_header(self, db_session: Session) -> None:
        """Missing Authorization header returns 401."""
        client = _make_client(db_session)

        response = client.get("/auth/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_me_with_invalid_token(self, db_session: Session) -> None:
        """Invalid token returns 401."""
        client = _make_client(db_session)

        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer totally-invalid-token"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"

    def test_me_with_expired_token(self, db_session: Session) -> None:
        """Expired token returns 401."""
        client = _make_client(db_session)
        _register_user(client)

        # Create a manually expired token
        secret = os.environ["JWT_SECRET_KEY"]
        expired_token = jwt.encode(
            {
                "sub": "1",
                "username": "authuser",
                "role": None,
                "type": "access",
                "iat": datetime.now(UTC) - timedelta(hours=2),
                "exp": datetime.now(UTC) - timedelta(hours=1),
            },
            secret,
            algorithm="HS256",
        )

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"

    def test_me_with_refresh_token(self, db_session: Session) -> None:
        """Refresh token (wrong type) returns 401."""
        client = _make_client(db_session)
        _register_user(client)
        tokens = _login_user(client)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"
