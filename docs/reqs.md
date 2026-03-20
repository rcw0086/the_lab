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

### Epic: API Development - REST Endpoints

Build a production-grade FastAPI REST API layer to expose the complete database schema (19 tables across core, catalog, session, journal, and sets domains). This epic establishes the full HTTP interface for creating, reading, updating, and deleting all entity types.

---

#### User Story: FastAPI Application Setup

**As a** developer
**I want** a properly initialized FastAPI application with middleware and documentation
**So that** I have a production-ready foundation for building API endpoints

**Acceptance Criteria:**
- [ ] FastAPI app instance is created with proper configuration
- [x] CORS middleware is configured for frontend integration
- [x] Request logging middleware captures all HTTP traffic
- [ ] Swagger/OpenAPI documentation is accessible at `/docs`
- [ ] Health check endpoint returns 200 OK with system status
- [ ] Application starts via `uv run` command
- [ ] All middleware is tested

**Tasks:**

1. **@DO — FastAPI App Setup — Initialize FastAPI application**
   - Completion: `main.py` or `app.py` exists with FastAPI app instance; `uv run` starts the server

2. **@DO — FastAPI App Setup — Configure CORS middleware**
   - Completion: CORS middleware added with appropriate origins; tested with preflight requests

3. **@BE — FastAPI App Setup — Add request logging middleware**
   - Completion: Middleware logs request/response details via structlog; verified in test

4. **@BE — FastAPI App Setup — Create health check endpoint**
   - Completion: `GET /health` returns 200 with JSON status; includes DB connectivity check

5. **@BE — FastAPI App Setup — Configure OpenAPI documentation**
   - Completion: `/docs` accessible; includes title, description, version; all endpoints documented

---

#### User Story: Authentication & Authorization

**As a** user
**I want** secure authentication and authorization
**So that** my data is protected and only I can access it

**Acceptance Criteria:**
- [ ] Users can register with username and password
- [ ] Passwords are hashed using bcrypt
- [ ] Users can log in and receive a JWT token
- [ ] JWT tokens include user_id and expiration
- [ ] Protected endpoints reject requests without valid tokens
- [ ] Token validation middleware extracts user context
- [ ] Invalid tokens return 401 Unauthorized
- [ ] Expired tokens return 401 with appropriate message

**Tasks:**

1. **@AR — Auth & Authorization — Design auth flow and token structure**
   - Completion: ADR or design doc covers JWT structure, token expiration, refresh strategy

2. **@BE — Auth & Authorization — Implement password hashing**
   - Completion: `hash_password()` and `verify_password()` functions using bcrypt; tested

3. **@BE — Auth & Authorization — Create JWT token generation/validation**
   - Completion: `create_access_token()` and `verify_token()` functions; includes expiration; tested

4. **@BE — Auth & Authorization — Build registration endpoint**
   - Completion: `POST /auth/register` creates user with hashed password; validates uniqueness

5. **@BE — Auth & Authorization — Build login endpoint**
   - Completion: `POST /auth/login` validates credentials and returns JWT; handles invalid credentials

6. **@BE — Auth & Authorization — Create auth dependency for protected routes**
   - Completion: `get_current_user()` dependency extracts and validates JWT; tested

---

#### User Story: API Response Schemas

**As a** developer
**I want** Pydantic schemas for all API requests and responses
**So that** data is validated automatically and API contracts are clear

**Acceptance Criteria:**
- [ ] Pydantic schemas exist for all 19 database models
- [ ] Each entity has Create, Read, and Update schemas
- [ ] Schemas enforce validation rules matching DB constraints
- [ ] Error responses follow consistent format
- [ ] Pagination schemas support offset/limit queries
- [ ] All schemas are tested for validation behavior

**Tasks:**

1. **@BE — API Schemas — Create base schema classes**
   - Completion: Base classes for Create, Read, Update patterns; error response schema defined

2. **@BE — API Schemas — Create User schemas**
   - Completion: UserCreate, UserRead, UserUpdate schemas; validated against DB constraints

3. **@BE — API Schemas — Create core entity schemas**
   - Completion: Schemas for Daily, Cycle, Goal, Injury (Create/Read/Update each)

4. **@BE — API Schemas — Create catalog schemas**
   - Completion: Schemas for Movement, Implement, VariationType, Variation

5. **@BE — API Schemas — Create session schemas**
   - Completion: Schemas for Session and Module with nested relationships

6. **@BE — API Schemas — Create sets schemas**
   - Completion: Schemas for Set, StrengthSetDetails, EnduranceSetDetails, SetVariation

7. **@BE — API Schemas — Create journal schemas**
   - Completion: Schemas for Note and join tables (GoalNote, CycleNote, InjuryNote)

8. **@BE — API Schemas — Create pagination schemas**
   - Completion: PaginationParams and PaginatedResponse schemas; tested

---

#### User Story: Service Layer

**As a** developer
**I want** a service layer that encapsulates business logic
**So that** API routes are thin and domain logic is reusable

**Acceptance Criteria:**
- [ ] Service classes exist for each entity domain
- [ ] Services handle CRUD operations with proper error handling
- [ ] Services enforce business rules beyond schema validation
- [ ] Services manage database transactions
- [ ] Services validate cross-entity constraints
- [ ] All service methods are unit tested

**Tasks:**

1. **@AR — Service Layer — Design service layer architecture**
   - Completion: Architecture doc or ADR defines service boundaries, error handling, transaction patterns

2. **@BE — Service Layer — Create base service class**
   - Completion: Base service with common CRUD patterns; session management; error handling

3. **@BE — Service Layer — Implement User service**
   - Completion: UserService with CRUD + authentication logic; tested

4. **@BE — Service Layer — Implement core entity services**
   - Completion: Services for Daily, Cycle, Goal, Injury; enforce business rules; tested

5. **@BE — Service Layer — Implement catalog services**
   - Completion: Services for Movement, Implement, VariationType, Variation; tested

6. **@BE — Service Layer — Implement session services**
   - Completion: SessionService and ModuleService; handle nested creation; tested

7. **@BE — Service Layer — Implement sets services**
   - Completion: SetService with support for strength/endurance details; tested

8. **@BE — Service Layer — Implement journal services**
   - Completion: NoteService with support for entity linking; tested

---

#### User Story: Core API Endpoints

**As a** user
**I want** REST endpoints for core entities
**So that** I can manage my daily tracking, cycles, goals, and injuries

**Acceptance Criteria:**
- [ ] User endpoints: GET (list/detail), POST, PUT, DELETE
- [ ] Daily endpoints: CRUD with user_id + date uniqueness
- [ ] Cycle endpoints: CRUD with date validation
- [ ] Goal endpoints: CRUD with achievement tracking
- [ ] Injury endpoints: CRUD with resolution tracking
- [ ] All endpoints enforce authentication
- [ ] All endpoints return appropriate status codes
- [ ] All endpoints have integration tests

**Tasks:**

1. **@BE — Core API — Create User endpoints**
   - Completion: `/users` routes with CRUD operations; tested

2. **@BE — Core API — Create Daily endpoints**
   - Completion: `/dailies` routes; enforce unique per user/date; tested

3. **@BE — Core API — Create Cycle endpoints**
   - Completion: `/cycles` routes; validate date ranges; tested

4. **@BE — Core API — Create Goal endpoints**
   - Completion: `/goals` routes; support achievement updates; tested

5. **@BE — Core API — Create Injury endpoints**
   - Completion: `/injuries` routes; validate resolution dates; tested

---

#### User Story: Training API Endpoints

**As a** user
**I want** REST endpoints for training sessions and workouts
**So that** I can log and query my training data

**Acceptance Criteria:**
- [ ] Session endpoints: CRUD with nested modules
- [ ] Module endpoints: CRUD with ordering validation
- [ ] Set endpoints: CRUD with type-specific details
- [ ] Movement catalog endpoints: CRUD for reference data
- [ ] Endpoints support creating complex nested structures
- [ ] Endpoints support querying sessions by date range
- [ ] All endpoints have integration tests

**Tasks:**

1. **@BE — Training API — Create Session endpoints**
   - Completion: `/sessions` routes; support nested module creation; tested

2. **@BE — Training API — Create Module endpoints**
   - Completion: `/modules` routes; enforce ordering constraints; tested

3. **@BE — Training API — Create Set endpoints**
   - Completion: `/sets` routes; handle strength/endurance details; tested

4. **@BE — Training API — Create Movement endpoints**
   - Completion: `/movements` routes; CRUD for movement catalog; tested

5. **@BE — Training API — Create Implement endpoints**
   - Completion: `/implements` routes; CRUD for implement catalog; tested

6. **@BE — Training API — Create Variation endpoints**
   - Completion: `/variations` and `/variation-types` routes; tested

---

#### User Story: Journal API Endpoints

**As a** user
**I want** REST endpoints for journal notes
**So that** I can create notes and link them to goals, cycles, and injuries

**Acceptance Criteria:**
- [ ] Note endpoints: CRUD operations
- [ ] Endpoints support linking notes to goals
- [ ] Endpoints support linking notes to cycles
- [ ] Endpoints support linking notes to injuries
- [ ] Query endpoints filter notes by entity
- [ ] Query endpoints support date range filtering
- [ ] All endpoints have integration tests

**Tasks:**

1. **@BE — Journal API — Create Note endpoints**
   - Completion: `/notes` routes; CRUD with user filtering; tested

2. **@BE — Journal API — Create note linking endpoints**
   - Completion: Routes to link/unlink notes to goals, cycles, injuries; tested

3. **@BE — Journal API — Create note query endpoints**
   - Completion: Routes to query notes by entity type and date range; tested

---
