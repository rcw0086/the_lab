"""Tests for the health check endpoint."""

import os

os.environ["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-characters-long-for-testing"
)

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from the_lab.main import create_app


class TestHealthEndpoint:
    """Test GET /health endpoint."""

    def setup_method(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_health_returns_200_when_db_connected(self) -> None:
        """Health endpoint returns 200 when database is reachable."""
        mock_conn = MagicMock()
        mock_connect = MagicMock()
        mock_connect.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.__exit__ = MagicMock(return_value=False)

        with patch("the_lab.main.engine") as mock_engine:
            mock_engine.connect.return_value = mock_connect
            response = self.client.get("/health")

        assert response.status_code == 200

    def test_health_returns_healthy_status(self) -> None:
        """Health endpoint returns status=healthy when DB is up."""
        mock_conn = MagicMock()
        mock_connect = MagicMock()
        mock_connect.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.__exit__ = MagicMock(return_value=False)

        with patch("the_lab.main.engine") as mock_engine:
            mock_engine.connect.return_value = mock_connect
            response = self.client.get("/health")

        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"
        assert data["database"]["connected"] is True

    def test_health_returns_503_when_db_unavailable(self) -> None:
        """Health endpoint returns 503 when database is unreachable."""
        with patch("the_lab.main.engine") as mock_engine:
            mock_engine.connect.side_effect = Exception("Connection refused")
            response = self.client.get("/health")

        assert response.status_code == 503

    def test_health_returns_degraded_when_db_unavailable(self) -> None:
        """Health endpoint returns status=degraded when DB is down."""
        with patch("the_lab.main.engine") as mock_engine:
            mock_engine.connect.side_effect = Exception("Connection refused")
            response = self.client.get("/health")

        data = response.json()
        assert data["status"] == "degraded"
        assert data["database"]["connected"] is False
        assert "Connection refused" in data["database"]["error"]

    def test_health_executes_select_1(self) -> None:
        """Health endpoint runs SELECT 1 to verify DB connectivity."""
        mock_conn = MagicMock()
        mock_connect = MagicMock()
        mock_connect.__enter__ = MagicMock(return_value=mock_conn)
        mock_connect.__exit__ = MagicMock(return_value=False)

        with patch("the_lab.main.engine") as mock_engine:
            mock_engine.connect.return_value = mock_connect
            self.client.get("/health")

        mock_conn.execute.assert_called_once()
        call_args = mock_conn.execute.call_args[0][0]
        assert str(call_args) == "SELECT 1"
