"""Tests for CORS middleware configuration."""

import os

os.environ["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-characters-long-for-testing"
)

from unittest.mock import patch

from fastapi.testclient import TestClient

from the_lab.main import create_app


class TestCORSMiddleware:
    """Test CORS middleware is properly configured."""

    def setup_method(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_cors_preflight_request(self) -> None:
        """CORS preflight (OPTIONS) returns correct headers for allowed origin."""
        response = self.client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
        assert "GET" in response.headers["access-control-allow-methods"]
        assert response.headers["access-control-allow-credentials"] == "true"

    def test_cors_preflight_post(self) -> None:
        """CORS preflight allows POST method."""
        response = self.client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"

    def test_cors_simple_request(self) -> None:
        """Simple GET request from allowed origin includes CORS headers."""
        response = self.client.get(
            "/",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
        assert response.headers["access-control-allow-credentials"] == "true"

    def test_cors_disallowed_origin(self) -> None:
        """Request from disallowed origin does not include CORS headers."""
        response = self.client.get(
            "/",
            headers={"Origin": "http://evil.example.com"},
        )
        assert "access-control-allow-origin" not in response.headers

    def test_cors_no_origin_header(self) -> None:
        """Request without Origin header works normally (no CORS headers)."""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers


class TestCORSConfiguration:
    """Test CORS settings are configurable via environment variables."""

    def test_default_cors_origins(self) -> None:
        """Default CORS origins include localhost:3000."""
        from the_lab.config import Settings

        settings = Settings(
            jwt_secret_key="test-secret-key-at-least-32-characters-long",
        )
        assert "http://localhost:3000" in settings.cors_origins

    def test_custom_cors_origins(self) -> None:
        """CORS origins can be configured via environment variable."""
        with patch.dict(
            os.environ,
            {"CORS_ORIGINS": '["https://app.example.com","https://staging.example.com"]'},
        ):
            from the_lab.config import Settings

            settings = Settings(
                jwt_secret_key="test-secret-key-at-least-32-characters-long",
            )
            assert "https://app.example.com" in settings.cors_origins
            assert "https://staging.example.com" in settings.cors_origins

    def test_cors_middleware_uses_configured_origins(self) -> None:
        """App uses configured CORS origins from settings."""
        with patch.dict(
            os.environ,
            {"CORS_ORIGINS": '["http://localhost:5173"]'},
        ):
            from the_lab.config import get_settings

            get_settings.cache_clear()
            try:
                app = create_app()
                client = TestClient(app)
                response = client.options(
                    "/",
                    headers={
                        "Origin": "http://localhost:5173",
                        "Access-Control-Request-Method": "GET",
                    },
                )
                assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
            finally:
                get_settings.cache_clear()
