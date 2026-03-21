"""Tests for password hashing and verification."""

import pytest

from the_lab.auth.password import hash_password, verify_password


class TestHashPassword:
    """Tests for hash_password()."""

    def test_returns_bcrypt_hash(self) -> None:
        result = hash_password("mypassword")
        assert result.startswith("$2b$")

    def test_uses_cost_factor_12(self) -> None:
        result = hash_password("mypassword")
        # bcrypt format: $2b$<rounds>$<salt+hash>
        assert result.startswith("$2b$12$")

    def test_different_calls_produce_different_hashes(self) -> None:
        hash1 = hash_password("same_password")
        hash2 = hash_password("same_password")
        assert hash1 != hash2

    def test_empty_password(self) -> None:
        result = hash_password("")
        assert result.startswith("$2b$12$")


class TestVerifyPassword:
    """Tests for verify_password()."""

    def test_correct_password_returns_true(self) -> None:
        hashed = hash_password("correcthorse")
        assert verify_password("correcthorse", hashed) is True

    def test_wrong_password_returns_false(self) -> None:
        hashed = hash_password("correcthorse")
        assert verify_password("wrongpassword", hashed) is False

    def test_empty_password_matches_empty_hash(self) -> None:
        hashed = hash_password("")
        assert verify_password("", hashed) is True

    def test_empty_password_does_not_match_nonempty(self) -> None:
        hashed = hash_password("notempty")
        assert verify_password("", hashed) is False

    def test_case_sensitive(self) -> None:
        hashed = hash_password("Password")
        assert verify_password("password", hashed) is False
        assert verify_password("PASSWORD", hashed) is False
        assert verify_password("Password", hashed) is True

    def test_unicode_password(self) -> None:
        hashed = hash_password("pässwörd123")
        assert verify_password("pässwörd123", hashed) is True
        assert verify_password("passwörd123", hashed) is False

    def test_long_password_raises(self) -> None:
        # bcrypt 5.x enforces the 72-byte limit
        long_pw = "a" * 100
        with pytest.raises(ValueError, match="72 bytes"):
            hash_password(long_pw)

    def test_max_length_password(self) -> None:
        pw_72 = "a" * 72
        hashed = hash_password(pw_72)
        assert verify_password(pw_72, hashed) is True

    def test_invalid_hash_raises(self) -> None:
        with pytest.raises(ValueError):
            verify_password("password", "not-a-valid-hash")
