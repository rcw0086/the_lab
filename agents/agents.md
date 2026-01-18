# The Lab — Agent Charter & Role Playbooks

**Version:** 0.1  
**Owner:** You  
**Status:** Living document

---

## 1. Mission

Build **The Lab**: a personal, data-intensive system that begins as a **training & health data platform** and expands into:

1. Training / health data platform
2. Decision-tracking system with feedback loops
3. Personal knowledge system (retrieval + synthesis)
4. Workflow automation to reduce real-world friction

Primary objective:

> **Re-establish confidence as a senior technical IC by building a system you own, evolve, and can reason about deeply.**

This is both:

- a real, daily-use system, and
- a portfolio-grade demonstration of architecture, data modeling, and engineering judgment.

---

## 2. Non-Negotiable Principles (All Agents)

### Data First

- Data correctness, structure, and provenance outrank UI polish.
- Raw facts are preserved; derived views are computed.
- Schema design is a first-class activity.

### Modular Monolith

- One repo, one deployable unit.
- Strong internal module boundaries.
- Services may be extracted later, but **only after pressure appears**.

### Analysis-Oriented Design

- Design for querying, trend analysis, and retrospective reasoning.
- Avoid write-optimized designs that destroy analytical clarity.

### Explicit > Clever

- Prefer clarity, verbosity, and explicitness.
- Optimize for “future me reading this in 18 months.”

### Security Baseline

- Secure by default, even for a personal app.
- No “temporary” shortcuts that become permanent.

### Quality Gates

- Tests, migrations, types, and linting are mandatory.
- “It works locally” is not sufficient.

---

## 3. Architecture Defaults

Unless explicitly overridden via an ADR:

### Backend

- Python + FastAPI
- Postgres
- SQLAlchemy 2.0 + Alembic
- Pydantic

### Frontend

- TypeScript
- Web-first (mobile-oriented UX)
- Later: React Native for voice/mobile-first workflows

### Style

- Domain-oriented modules (bounded contexts)
- Thin API adapters, rich domain/services
- REST first; eventing later if justified

---

## 4. Definition of Done (Applies to All Work)

A task or PR is **not done** unless:

- Scope and assumptions are documented
- Code matches existing architecture and conventions
- DB migrations included (if schema changed)
- Tests exist (happy path + ≥1 edge case)
- Security implications noted (even “none”)
- Logs/observability hooks added where appropriate
- Docs updated (README, module docs, or ADR)
- Rollback considerations stated

---

## 5. Cross-Agent Conventions

### Modules

Each module owns:

- Domain models + invariants
- Persistence mappings
- Service/use-case layer
- API adapters (routes/controllers)

No cross-module reaching into internals.

### Database

- Prefer immutable “facts” tables where possible
- Constraints are mandatory (NOT NULL, CHECK, FK, UNIQUE)
- Indexes based on access paths, not vibes
- Timestamps and provenance included when useful
- Migrations must be reversible or explicitly marked destructive

### APIs

- Consistent error model
- Pagination/filtering from day one
- Idempotent writes where applicable (imports, retries)

### Testing

- Unit tests for domain logic
- Integration tests at DB + API boundaries
- Regression tests for fixed bugs

### Security

- No secrets in repo
- Validate all inputs
- Auth required by default
- Least-privilege authorization

---

## 6. Role Playbooks

The specific role playbooks have been moved to the `agents/` folder as individual files. See:

- `agents/architect.md`
- `agents/planner.md`
- `agents/designer.md`
- `agents/backend.md`
- `agents/frontend.md`
- `agents/code_reviewer.md`
- `agents/security_reviewer.md`
- `agents/qa_specialist.md`
- `agents/devops.md`
- `agents/standard_template.md`

For role-specific guidance, open the corresponding file in `agents/`.

---

## 7. Standard Agent Output Template

Agents should end with:

- **What I did**
- **Why**
- **Tradeoffs**
- **Risks**
- **Next steps**
- **Definition of Done status**

---
