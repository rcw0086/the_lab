"""Integration tests for POST /auth/login."""

import os

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


def _register_user(client: TestClient, username: str = "loginuser", password: str = "securepass123") -> None:
    """Register a user via the API so they have a real bcrypt hash."""
    response = client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )
    assert response.status_code == 201


class TestLoginEndpoint:
    """Tests for POST /auth/login."""

    def test_login_success(self, db_session: Session) -> None:
        client = _make_client(db_session)
        _register_user(client)
        response = client.post(
            "/auth/login",
            json={"username": "loginuser", "password": "securepass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, db_session: Session) -> None:
        client = _make_client(db_session)
        _register_user(client)
        response = client.post(
            "/auth/login",
            json={"username": "nonexistent", "password": "securepass123"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_login_invalid_password(self, db_session: Session) -> None:
        client = _make_client(db_session)
        _register_user(client)
        response = client.post(
            "/auth/login",
            json={"username": "loginuser", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_login_missing_username(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post(
            "/auth/login",
            json={"password": "securepass123"},
        )
        assert response.status_code == 422

    def test_login_missing_password(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post(
            "/auth/login",
            json={"username": "loginuser"},
        )
        assert response.status_code == 422

    def test_login_empty_body(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post("/auth/login", json={})
        assert response.status_code == 422

    def test_login_returns_valid_jwt(self, db_session: Session) -> None:
        client = _make_client(db_session)
        _register_user(client)
        response = client.post(
            "/auth/login",
            json={"username": "loginuser", "password": "securepass123"},
        )
        assert response.status_code == 200
        data = response.json()
        secret = os.environ["JWT_SECRET_KEY"]
        decoded = jwt.decode(data["access_token"], secret, algorithms=["HS256"])
        assert decoded["username"] == "loginuser"
        assert decoded["type"] == "access"
        assert "sub" in decoded
        assert "exp" in decoded
