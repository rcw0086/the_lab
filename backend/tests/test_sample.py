"""Sample test to verify pytest configuration."""

from the_lab import __version__


def test_version() -> None:
    """Test that version is defined."""
    assert __version__ == "0.1.0"


async def test_async_works() -> None:
    """Test that async tests work with pytest-asyncio."""
    result = await async_function()
    assert result == "async works"


async def async_function() -> str:
    """Sample async function."""
    return "async works"
