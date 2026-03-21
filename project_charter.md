---

## Product Mission and Scope

This project (“The Lab”) exists as a long-lived, evolving system that:
- can be owned personally and used daily,
- serves as a portfolio-grade demonstration of production-quality architecture,
- supports iterative growth into multiple modules without re-platforming.

### Planned Modules (Build Order)
1. Training / health data platform
2. Decision-tracking system with feedback loops
3. Personal knowledge system with retrieval + synthesis
4. Workflow automation to reduce real life friction

**Note:** Each module should be independently valuable but designed to compose into a coherent whole.

---

## Architecture Defaults

These are _defaults_, not dogma. Deviations are allowed only with an ADR documenting tradeoffs.

### Architecture Style

- **Modular monolith** by default (single repo, clear module boundaries)
- Extract services only when justified (scaling, isolation, throughput, security boundaries, team boundaries)

### Backend Defaults

- Python + FastAPI
- Postgres
- SQLAlchemy 2.0 + Alembic
- Pydantic
- Redis only when caching/queues become justified (not as premature complexity)

### UI Defaults

- TypeScript
- Start Web (mobile-first)
- Later: React Native for best voice/mobile UX

### Data Posture Defaults

- “Data-first” thinking: schema and invariants are first-class
- Favor explicit, queryable representations over opaque blobs when it affects analytics, integrity, or evolvability
- Migration hygiene is non-negotiable (forward + rollback considerations documented)

---

## Engineering Standards and Quality Bar

These apply across all modules unless explicitly overridden via ADR.

### Data Integrity and Modeling

- Prefer explicit constraints (FKs, uniqueness, check constraints) when appropriate
- Treat migrations as production artifacts: review them carefully, avoid destructive changes without clear plan
- All important invariants must be encoded either:
  - in the database (preferred where feasible), or
  - in application-level validation with tests and documented rationale

### API and Contract Discipline

- Define API contracts intentionally (request/response shapes, error model, pagination/filtering rules)
- Changes to externally-consumed contracts require explicit versioning strategy or compatibility plan
- Avoid “guessable” behavior: document expectations and edge cases

### Security Baseline

- Assume untrusted clients and hostile inputs
- Secrets never committed; `.env.example` is required for configuration shape
- Authentication/authorization rules must be explicit and tested where critical
- New dependencies require a basic security review (license + known vuln posture)

### Observability Baseline

- Structured logging conventions
- Health checks / readiness signals where applicable
- Clear runbooks for common failure modes as the system grows

### Testing Baseline

- Critical paths must have tests (unit/integration as appropriate)
- Each feature must show verification evidence (commands run, what passed)
- Bugs found by QA should become regression tests when feasible

---

## Decision Discipline (ADRs)

Architectural and high-impact technical decisions must be recorded as ADRs, including:

- alternatives considered,
- explicit tradeoffs,
- why one choice was selected,
- follow-up implications (migration plan, risks, future constraints).

---

## Source of Truth Hierarchy

When there is ambiguity, interpret and resolve using this precedence:

1. `project_charter.md` (product-level constraints and architecture defaults)
2. Requirements docs (e.g. `docs/reqs.md`)
3. ADRs (decision history and tradeoffs)
4. Implementation (code + migrations), as validated by tests and reviews
