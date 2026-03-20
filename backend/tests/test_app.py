"""Tests for the FastAPI application initialization."""

import os

os.environ["JWT_SECRET_KEY"] = os.environ.get(
    "JWT_SECRET_KEY", "test-jwt-secret-key-at-least-32-characters-long-for-testing"
)

from fastapi.testclient import TestClient

from the_lab.main import create_app


class TestFastAPIApp:
    """Test FastAPI application setup and configuration."""

    def setup_method(self) -> None:
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_root_endpoint_returns_200(self) -> None:
        response = self.client.get("/")
        assert response.status_code == 200

    def test_root_endpoint_response_body(self) -> None:
        response = self.client.get("/")
        data = response.json()
        assert data["name"] == "The Lab"
        assert data["version"] == "0.1.0"
        assert "environment" in data

    def test_openapi_docs_accessible(self) -> None:
        response = self.client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema_accessible(self) -> None:
        response = self.client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "The Lab"
        assert schema["info"]["version"] == "0.1.0"

    def test_app_has_lifespan(self) -> None:
        assert self.app.router.lifespan_context is not None

    def test_create_app_returns_fastapi_instance(self) -> None:
        from fastapi import FastAPI

        app = create_app()
        assert isinstance(app, FastAPI)
