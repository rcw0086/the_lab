"""The Lab — FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from the_lab.config import get_settings
from the_lab.logging import get_logger, setup_logging


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

    @app.get("/")
    async def root() -> dict[str, str]:
        return {
            "name": "The Lab",
            "version": "0.1.0",
            "environment": settings.environment,
        }

    return app


app = create_app()
