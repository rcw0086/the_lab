# The Lab — Requirements

This document is the canonical source for requirements. All User Stories and Tasks are tracked as GitHub Issues.

---

## App: The Lab

### Epic: Project Infrastructure Setup

Establish the development environment, tooling, and CI/CD pipeline per ADR-009.

---

#### User Story: Backend Development Environment

**As a** developer
**I want** a fully configured Python backend environment
**So that** I can write, lint, test, and run backend code with consistent tooling

**Acceptance Criteria:**
- [ ] `uv sync` installs all dependencies from lockfile
- [ ] `uv run ruff check .` runs linting with zero config friction
- [ ] `uv run ruff format .` formats code consistently
- [ ] `uv run mypy .` type-checks with strict mode
- [ ] `uv run pytest` runs tests with async support
- [ ] Application loads config from environment via pydantic-settings
- [ ] Logs output as structured JSON via structlog

**Tasks:**

1. **@DO — Backend Dev Environment — Initialize uv project**
   - Completion: `pyproject.toml` exists with project metadata, Python version, and dependency groups (dev, test)

2. **@DO — Backend Dev Environment — Configure Ruff**
   - Completion: `ruff.toml` or `[tool.ruff]` in pyproject.toml with lint + format rules

3. **@DO — Backend Dev Environment — Configure mypy**
   - Completion: `[tool.mypy]` config with strict mode; py.typed marker if needed

4. **@DO — Backend Dev Environment — Set up pytest**
   - Completion: `pytest.ini` or `[tool.pytest]` config; pytest-asyncio installed; sample test passes

5. **@BE — Backend Dev Environment — Configure pydantic-settings**
   - Completion: `Settings` class loads from env; `.env.example` documents required vars

6. **@BE — Backend Dev Environment — Configure structlog**
   - Completion: Logging configured for JSON output; example log statement works

---

#### User Story: Frontend Development Environment

**As a** developer
**I want** a fully configured TypeScript/React frontend environment
**So that** I can write, lint, test, and build frontend code with consistent tooling

**Acceptance Criteria:**
- [ ] `pnpm install` installs all dependencies from lockfile
- [ ] `pnpm lint` runs ESLint with TypeScript rules
- [ ] `pnpm format` runs Prettier
- [ ] `pnpm test` runs Jest with React Testing Library
- [ ] `pnpm build` produces production bundle
- [ ] React Query is installed and provider is configured

**Tasks:**

1. **@DO — Frontend Dev Environment — Initialize pnpm project**
   - Completion: `package.json` exists with scripts; `pnpm-lock.yaml` committed

2. **@DO — Frontend Dev Environment — Configure TypeScript**
   - Completion: `tsconfig.json` with strict mode; compiles without errors

3. **@DO — Frontend Dev Environment — Configure ESLint + Prettier**
   - Completion: `.eslintrc.*` and `.prettierrc` exist; `pnpm lint` and `pnpm format` work

4. **@DO — Frontend Dev Environment — Set up Jest + React Testing Library**
   - Completion: `jest.config.*` exists; sample component test passes

5. **@FE — Frontend Dev Environment — Set up React Query**
   - Completion: `QueryClientProvider` wraps app; example query hook works

---

#### User Story: Local Development Infrastructure

**As a** developer
**I want** one-command local environment setup
**So that** I can start developing without manual database configuration

**Acceptance Criteria:**
- [ ] `docker compose up -d` starts Postgres
- [ ] Database is accessible at documented connection string
- [ ] `.env.example` documents all required environment variables
- [ ] README includes setup instructions

**Tasks:**

1. **@DO — Local Dev Infrastructure — Create Docker Compose for Postgres**
   - Completion: `docker-compose.yml` with Postgres service; healthcheck configured

2. **@DO — Local Dev Infrastructure — Document environment variables**
   - Completion: `.env.example` with all required vars; README setup section updated

---

#### User Story: CI/CD Pipeline

**As a** developer
**I want** automated quality checks on every push
**So that** code quality issues are caught before merge

**Acceptance Criteria:**
- [ ] Push to any branch triggers CI
- [ ] Backend: lint, type check, test run in sequence
- [ ] Frontend: lint, type check, test, build run in sequence
- [ ] CI fails fast on first error
- [ ] PR cannot merge with failing CI (branch protection)

**Tasks:**

1. **@DO — CI/CD Pipeline — Create backend CI workflow**
   - Completion: `.github/workflows/backend.yml` runs ruff, mypy, pytest on push

2. **@DO — CI/CD Pipeline — Create frontend CI workflow**
   - Completion: `.github/workflows/frontend.yml` runs lint, tsc, jest, build on push

3. **@DO — CI/CD Pipeline — Configure branch protection**
   - Completion: `main` branch requires CI pass; documented in README

---
