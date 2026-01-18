<!-- filepath: /Users/rob/dev/projects/python/the_lab/docs/adr/adr-009-development-tooling.md -->

## ADR-009: Development Tooling

**Status:** Accepted

**Decision**
Standardize on the following toolchain for development, testing, and CI.

---

### Python Backend

| Concern | Tool | Notes |
|---------|------|-------|
| Package management | **uv** | Fast, modern, lockfile-based |
| Linting | **Ruff** | Replaces flake8, isort, pyupgrade |
| Formatting | **Ruff** (format) | Black-compatible, single tool |
| Type checking | **mypy** | Strict mode enabled |
| Testing | **pytest** | With pytest-asyncio for async tests |
| Settings/env | **pydantic-settings** | Typed config from env vars |
| Logging | **structlog** | Structured JSON logs for analysis |

### TypeScript Frontend

| Concern | Tool | Notes |
|---------|------|-------|
| Package management | **pnpm** | Fast, disk-efficient |
| Linting | **ESLint** | With TypeScript plugin |
| Formatting | **Prettier** | Integrated with ESLint |
| Testing | **Jest** | With React Testing Library |
| Server state | **React Query (TanStack Query)** | Caching, refetching, mutations |
| Client state | **React Context** or **Zustand** | Only if needed beyond React Query |

### Authentication

| Concern | Tool | Notes |
|---------|------|-------|
| Token type | **JWT** | Access + refresh token pattern |
| Storage | HttpOnly cookies | Refresh token; access token in memory |
| Library (BE) | **python-jose** or **PyJWT** | Standard JWT handling |

### CI/CD

| Concern | Tool | Notes |
|---------|------|-------|
| CI platform | **GitHub Actions** | Integrated with repo |
| Workflows | Lint → Type check → Test → Build | Fail fast ordering |
| DB for tests | Postgres service container | Real DB, no mocks |

### Local Development

| Concern | Tool | Notes |
|---------|------|-------|
| Containerization | **Docker Compose** | Postgres + optional services |
| DB admin | **pgAdmin** or CLI | Optional, developer preference |
| API docs | **FastAPI /docs** | Auto-generated OpenAPI |

---

**Rationale**

- **uv**: 10-100x faster than pip/Poetry; handles venvs and lockfiles; Astral (Ruff creators) backed
- **pnpm**: Strict dependency resolution, disk-efficient, faster than npm/yarn
- **Ruff**: Single tool for linting+formatting; extremely fast; reduces config sprawl
- **Jest**: Mature ecosystem, excellent React Testing Library integration, familiar to most FE devs
- **React Query**: Eliminates boilerplate for server state; built-in caching, background refetch, optimistic updates
- **JWT**: Stateless auth scales horizontally; no session store required; standard approach
- **GitHub Actions**: Zero additional infrastructure; native repo integration; generous free tier
- **structlog**: Analysis-friendly JSON output aligns with data-first philosophy

**Consequences**

- Team must learn uv (minimal friction; pip-compatible commands)
- JWT requires careful refresh token handling (httpOnly cookies mitigate XSS)
- React Query has learning curve but reduces total code
- Ruff is newer; some legacy docs reference flake8/black separately

**Alternatives Considered**

| Choice | Alternative | Why not |
|--------|-------------|---------|
| uv | Poetry | Slower, more complex resolver |
| pnpm | yarn | Less strict, larger node_modules |
| Jest | Vitest | Jest ecosystem more mature; Vitest viable if we switch to Vite |
| React Query | Redux Toolkit Query | More boilerplate; Redux not needed for this app |
| JWT | Session cookies | Requires session store; complicates horizontal scaling |
