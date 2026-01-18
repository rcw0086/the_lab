# The Lab

## Overview
The Lab is a **production-grade, data-intensive application** focused initially on workout and health data tracking, with a long-term vision of supporting decision tracking, personal knowledge systems, and workflow automation.

Although development begins with a single primary user (the founder), the system is designed as a **multi-user, commercially viable platform** from its inception.

## Project Philosophy
This application is designed as a **production-grade, multi-tenant system** from day one.

Personal use is treated as an **initial onboarding condition**, not an architectural constraint. All decisions assume the application may:
- Serve multiple concurrent users
- Handle growing data volumes
- Be deployed in commercial environments
- Require strong security, observability, and reliability guarantees

## Architectural Intent
- Backend: Python (FastAPI) + PostgreSQL
- Frontend: TypeScript + React + Vite
- Architecture: Modular monolith with clear domain boundaries
- Data-first design suitable for analytics and scale

## Guiding Principle
**The system is designed for scale; it is merely used at small scale initially.**

---

## Getting Started

### Prerequisites

- **Docker** (for PostgreSQL)
- **uv** (Python package manager) - [Install](https://github.com/astral-sh/uv)
- **pnpm** (Node package manager) - [Install](https://pnpm.io/installation)
- **Node.js** 20+
- **Python** 3.11+

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/rcw0086/the_lab.git
cd the_lab

# 2. Copy environment configuration
cp .env.example .env

# 3. Start PostgreSQL
docker compose up -d

# 4. Set up backend
cd backend
uv sync --all-extras
source .venv/bin/activate

# 5. Set up frontend (in a new terminal)
cd frontend
pnpm install

# 6. Run development servers
# Backend (from backend directory):
uv run uvicorn the_lab.main:app --reload --port 8000

# Frontend (from frontend directory):
pnpm dev
```

### Verify Installation

```bash
# Backend
cd backend
uv run ruff check .        # Linting
uv run mypy src            # Type checking
uv run pytest              # Tests

# Frontend
cd frontend
pnpm lint                  # ESLint
pnpm typecheck            # TypeScript
pnpm test                 # Jest
pnpm build                # Production build
```

---

## Project Structure

```
the_lab/
├── backend/               # Python FastAPI backend
│   ├── src/the_lab/      # Application code
│   ├── tests/            # Backend tests
│   └── pyproject.toml    # Python dependencies
├── frontend/             # React TypeScript frontend
│   ├── src/              # Application code
│   └── package.json      # Node dependencies
├── docs/                 # Documentation
│   ├── adr/              # Architecture Decision Records
│   └── reqs.md           # Requirements
├── agents/               # AI agent playbooks
├── docker-compose.yml    # Local development services
└── .env.example          # Environment template
```

---

## Development

### Backend Commands

```bash
cd backend

# Install dependencies
uv sync --all-extras

# Run development server
uv run uvicorn the_lab.main:app --reload

# Linting & formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run mypy src

# Testing
uv run pytest
uv run pytest --cov
```

### Frontend Commands

```bash
cd frontend

# Install dependencies
pnpm install

# Run development server
pnpm dev

# Linting & formatting
pnpm lint
pnpm format

# Type checking
pnpm typecheck

# Testing
pnpm test
pnpm test:coverage

# Build
pnpm build
```

### Database

```bash
# Start PostgreSQL
docker compose up -d

# Start PostgreSQL + pgAdmin
docker compose --profile tools up -d

# Stop services
docker compose down

# Reset database (destroys data)
docker compose down -v
```

**Connection Details:**
- Host: `localhost`
- Port: `5432`
- Database: `the_lab`
- User: `postgres`
- Password: `postgres`

**pgAdmin** (when using `--profile tools`):
- URL: http://localhost:5050
- Email: `admin@localhost.com`
- Password: `admin`

---

## Documentation

- [Project Charter](project_charter.md) - Core principles and constraints
- [Architecture Decision Records](docs/adr/) - Technical decisions
- [Requirements](docs/reqs.md) - Feature requirements
- [Agent Playbooks](agents/) - AI agent guidelines

---

## Branch Protection

The `main` branch requires:
- Passing CI checks (lint, type check, tests)
- Pull request review

---

## Tech Stack

### Backend
- **Runtime:** Python 3.11+
- **Framework:** FastAPI
- **Database:** PostgreSQL 16
- **ORM:** SQLAlchemy 2.0
- **Migrations:** Alembic
- **Validation:** Pydantic
- **Auth:** JWT (python-jose)
- **Logging:** structlog

### Frontend
- **Runtime:** Node.js 20+
- **Framework:** React 19
- **Build:** Vite
- **Language:** TypeScript
- **State:** React Query (TanStack Query)
- **Testing:** Jest + React Testing Library

### Tooling
- **Python Packaging:** uv
- **Python Linting:** Ruff
- **Python Types:** mypy
- **Node Packaging:** pnpm
- **JS Linting:** ESLint
- **JS Formatting:** Prettier
- **CI:** GitHub Actions
