"""Test configuration security requirements.

This module tests that security-critical configuration values are properly
validated and cannot use insecure defaults.
"""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from the_lab.config import Settings


class TestJWTSecretKeyValidation:
    """Test JWT secret key validation."""

    def test_jwt_secret_key_required(self, tmp_path: any) -> None:  # noqa: ANN401
        """Test that JWT_SECRET_KEY is required and has no default value.

        This test ensures the CRITICAL security fix from issue #25 is maintained:
        - JWT_SECRET_KEY must be set via environment variable
        - No default value like "change-me-in-production" is allowed
        - Settings validation will fail if JWT_SECRET_KEY is not set
        """
        # Create a clean environment without JWT_SECRET_KEY
        # and override the env_file to use a temporary empty file
        clean_env = {k: v for k, v in os.environ.items() if k != "JWT_SECRET_KEY"}

        # Create an empty .env file in tmp_path
        empty_env_file = tmp_path / ".env"
        empty_env_file.write_text("")

        with patch.dict(os.environ, clean_env, clear=True):
            # Attempting to create Settings without JWT_SECRET_KEY should fail
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=str(empty_env_file))

            # Verify the error is about jwt_secret_key being required
            error = exc_info.value
            errors = error.errors()
            assert len(errors) == 1
            assert errors[0]["loc"] == ("jwt_secret_key",)
            assert errors[0]["type"] == "missing"

    def test_jwt_secret_key_works_when_set(self) -> None:
        """Test that Settings loads successfully when JWT_SECRET_KEY is provided."""
        with patch.dict(
            os.environ,
            {"JWT_SECRET_KEY": "test-secret-key-at-least-32-characters-long"},
        ):
            settings = Settings()
            assert settings.jwt_secret_key == "test-secret-key-at-least-32-characters-long"
            assert settings.jwt_algorithm == "HS256"

    def test_jwt_secret_key_no_hardcoded_default(self) -> None:
        """Test that there is no hardcoded default value for jwt_secret_key.

        This prevents regression of the security issue where
        "change-me-in-production" was used as a default value.
        """
        # Verify the Settings class definition has no default
        from pydantic_core import PydanticUndefined
        from the_lab.config import Settings

        field_info = Settings.model_fields["jwt_secret_key"]

        # Check that field is required and has no default value
        assert field_info.is_required()
        assert field_info.default is PydanticUndefined

    def test_other_jwt_settings_have_sensible_defaults(self) -> None:
        """Test that other JWT settings have appropriate defaults."""
        with patch.dict(
            os.environ,
            {"JWT_SECRET_KEY": "test-secret-key-at-least-32-characters-long"},
        ):
            settings = Settings()
            assert settings.jwt_algorithm == "HS256"
            assert settings.jwt_access_token_expire_minutes == 30
            assert settings.jwt_refresh_token_expire_days == 7
