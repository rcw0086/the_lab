"""Test-specific settings configuration.

This module provides test settings that override production settings
to use a separate test database and appropriate test configurations.
"""

from pydantic_settings import SettingsConfigDict

from the_lab.config import Settings


class TestSettings(Settings):
    """Test-specific settings that override default settings.

    Key differences from production settings:
    - Uses separate test database (the_lab_test)
    - Debug mode enabled for detailed error messages
    - Reduced token expiration for faster testing
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Override database to use test database
    postgres_db: str = "the_lab_test"

    # Enable debug mode for tests
    debug: bool = True

    # Test JWT secret key (override the required field with a test value)
    jwt_secret_key: str = "test-jwt-secret-key-at-least-32-characters-long-for-testing"

    # Use shorter token expiration for faster tests
    jwt_access_token_expire_minutes: int = 5
    jwt_refresh_token_expire_days: int = 1

    # Use console logging format for test output
    log_format: str = "console"
    log_level: str = "DEBUG"


def get_test_settings() -> TestSettings:
    """Get test settings instance.

    Returns:
        TestSettings: Test configuration instance
    """
    return TestSettings()
