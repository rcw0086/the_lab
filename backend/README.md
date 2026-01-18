# The Lab - Backend

Python backend for The Lab platform.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Migrations**: Alembic
- **Validation**: Pydantic
- **Auth**: JWT (python-jose)

## Development Setup

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL (via Docker Compose)

### Installation

```bash
# Install dependencies
uv sync --all-extras

# Activate virtual environment
source .venv/bin/activate

# Run development server
uv run uvicorn the_lab.main:app --reload
```

### Commands

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking
uv run mypy .

# Testing
uv run pytest

# Test with coverage
uv run pytest --cov
```

## Project Structure

```
backend/
├── src/
│   └── the_lab/       # Application package
├── tests/             # Test files
├── alembic/           # Database migrations
├── pyproject.toml     # Project configuration
└── uv.lock           # Dependency lockfile
```
