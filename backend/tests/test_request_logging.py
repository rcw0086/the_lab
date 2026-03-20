"""Tests for request logging middleware."""

import os

os.environ["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-characters-long-for-testing"
)

from unittest.mock import patch

from fastapi.testclient import TestClient

from the_lab.main import create_app


class TestRequestLoggingMiddleware:
    """Test that request logging middleware captures HTTP traffic details."""

    def setup_method(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_logs_request_method_and_path(self) -> None:
        """Middleware logs HTTP method and path."""
        with patch("the_lab.middleware.structlog.stdlib.get_logger") as mock_get:
            mock_logger = mock_get.return_value
            self.client.get("/")
            mock_logger.info.assert_called()
            call_kwargs = mock_logger.info.call_args
            assert call_kwargs[0][0] == "http_request"
            assert call_kwargs[1]["method"] == "GET"
            assert call_kwargs[1]["path"] == "/"

    def test_logs_status_code(self) -> None:
        """Middleware logs response status code."""
        with patch("the_lab.middleware.structlog.stdlib.get_logger") as mock_get:
            mock_logger = mock_get.return_value
            self.client.get("/")
            call_kwargs = mock_logger.info.call_args
            assert call_kwargs[1]["status_code"] == 200

    def test_logs_duration(self) -> None:
        """Middleware logs request duration in milliseconds."""
        with patch("the_lab.middleware.structlog.stdlib.get_logger") as mock_get:
            mock_logger = mock_get.return_value
            self.client.get("/")
            call_kwargs = mock_logger.info.call_args
            assert "duration_ms" in call_kwargs[1]
            assert isinstance(call_kwargs[1]["duration_ms"], float)
            assert call_kwargs[1]["duration_ms"] >= 0

    def test_logs_query_params(self) -> None:
        """Middleware logs query parameters when present."""
        with patch("the_lab.middleware.structlog.stdlib.get_logger") as mock_get:
            mock_logger = mock_get.return_value
            self.client.get("/?foo=bar")
            call_kwargs = mock_logger.info.call_args
            assert call_kwargs[1]["query"] is not None
            assert "foo=bar" in call_kwargs[1]["query"]

    def test_no_query_params_logs_none(self) -> None:
        """Middleware logs None for query when no query params."""
        with patch("the_lab.middleware.structlog.stdlib.get_logger") as mock_get:
            mock_logger = mock_get.return_value
            self.client.get("/")
            call_kwargs = mock_logger.info.call_args
            assert call_kwargs[1]["query"] is None

    def test_excludes_docs_paths(self) -> None:
        """Middleware does not log requests to documentation endpoints."""
        with patch("the_lab.middleware.structlog.stdlib.get_logger") as mock_get:
            mock_logger = mock_get.return_value
            self.client.get("/docs")
            mock_logger.info.assert_not_called()

    def test_excludes_openapi_path(self) -> None:
        """Middleware does not log requests to OpenAPI schema endpoint."""
        with patch("the_lab.middleware.structlog.stdlib.get_logger") as mock_get:
            mock_logger = mock_get.return_value
            self.client.get("/openapi.json")
            mock_logger.info.assert_not_called()

    def test_does_not_log_sensitive_headers(self) -> None:
        """Middleware does not include authorization headers in logs."""
        with patch("the_lab.middleware.structlog.stdlib.get_logger") as mock_get:
            mock_logger = mock_get.return_value
            self.client.get("/", headers={"Authorization": "Bearer secret-token"})
            call_kwargs = mock_logger.info.call_args
            # Verify no logged kwarg values contain the secret token
            for value in call_kwargs[1].values():
                if isinstance(value, str):
                    assert "secret-token" not in value

    def test_logs_404_status(self) -> None:
        """Middleware correctly logs non-200 status codes."""
        with patch("the_lab.middleware.structlog.stdlib.get_logger") as mock_get:
            mock_logger = mock_get.return_value
            self.client.get("/nonexistent")
            call_kwargs = mock_logger.info.call_args
            assert call_kwargs[1]["status_code"] == 404
