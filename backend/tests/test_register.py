"""Integration tests for POST /auth/register."""

import os

os.environ["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-characters-long-for-testing"
)

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from the_lab.db.models.core import User
from the_lab.db.session import get_db
from the_lab.main import create_app


def _make_client(db_session: Session) -> TestClient:
    """Create a test client with the DB session overridden."""
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session
    return TestClient(app)


class TestRegisterEndpoint:
    """Tests for POST /auth/register."""

    def test_register_success(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post(
            "/auth/register",
            json={"username": "newuser", "password": "securepass123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] is None
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_stores_hashed_password(self, db_session: Session) -> None:
        client = _make_client(db_session)
        client.post(
            "/auth/register",
            json={"username": "hashcheck", "password": "mypassword"},
        )
        user = db_session.query(User).filter(User.username == "hashcheck").first()
        assert user is not None
        assert user.password_hash.startswith("$2b$12$")
        assert user.password_hash != "mypassword"

    def test_register_duplicate_username_returns_409(self, db_session: Session) -> None:
        client = _make_client(db_session)
        client.post(
            "/auth/register",
            json={"username": "dupeuser", "password": "password123"},
        )
        response = client.post(
            "/auth/register",
            json={"username": "dupeuser", "password": "otherpass123"},
        )
        assert response.status_code == 409
        assert "already taken" in response.json()["detail"]

    def test_register_username_too_short(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post(
            "/auth/register",
            json={"username": "ab", "password": "password123"},
        )
        assert response.status_code == 422

    def test_register_password_too_short(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post(
            "/auth/register",
            json={"username": "validuser", "password": "short"},
        )
        assert response.status_code == 422

    def test_register_password_too_long(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post(
            "/auth/register",
            json={"username": "validuser", "password": "a" * 73},
        )
        assert response.status_code == 422

    def test_register_missing_username(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post(
            "/auth/register",
            json={"password": "password123"},
        )
        assert response.status_code == 422

    def test_register_missing_password(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post(
            "/auth/register",
            json={"username": "validuser"},
        )
        assert response.status_code == 422

    def test_register_empty_body(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post("/auth/register", json={})
        assert response.status_code == 422

    def test_register_strips_whitespace(self, db_session: Session) -> None:
        client = _make_client(db_session)
        response = client.post(
            "/auth/register",
            json={"username": "  spaceduser  ", "password": "password123"},
        )
        assert response.status_code == 201
        assert response.json()["username"] == "spaceduser"
