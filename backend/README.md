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

### Database Migrations

```bash
# Create a new migration
alembic revision -m "description of changes"

# Create a migration with autogenerate (after models are defined)
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1

# View current migration version
alembic current

# View migration history
alembic history
```

**Note**: Database connection is configured via environment variables (see `.env.example`). Alembic automatically uses the application settings.

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
