"""The Lab — FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from the_lab.config import get_settings
from the_lab.db.session import engine
from the_lab.logging import get_logger, setup_logging
from the_lab.middleware import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup and shutdown."""
    settings = get_settings()
    setup_logging(settings)
    logger = get_logger(__name__)
    logger.info(
        "application_started",
        environment=settings.environment,
        host=settings.api_host,
        port=settings.api_port,
    )
    yield
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="The Lab",
        description="A data-intensive platform for training, health, and decision tracking",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "name": "The Lab",
            "version": "0.1.0",
            "environment": settings.environment,
        }

    @app.get("/health")
    async def health() -> Any:
        """Health check endpoint with database connectivity verification."""
        db_healthy = True
        db_error = None
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
        except Exception as exc:
            db_healthy = False
            db_error = str(exc)

        status = "healthy" if db_healthy else "degraded"
        payload: dict[str, Any] = {
            "status": status,
            "version": "0.1.0",
            "database": {"connected": db_healthy},
        }
        if db_error:
            payload["database"]["error"] = db_error

        status_code = 200 if db_healthy else 503
        return JSONResponse(content=payload, status_code=status_code)

    return app


app = create_app()
