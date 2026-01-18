# The Lab — Agent Charter & Role Playbooks

**Version:** 0.2  
**Owner:** You  
**Status:** Living document

---

Thes agent instructions function under the authority of the readme.md and project_charter.md documents.

## 1. Mission

Build **The Lab**: a data-intensive system that begins as a **training & health data platform** and expands into:

1. Training / health data platform
2. Decision-tracking system with feedback loops
3. Personal knowledge system (retrieval + synthesis)
4. Workflow automation to reduce real-world friction

This project is a **production-grade, scalable application**. The fact that it is initially used by the founder does not relax requirements for:

- Security
- Data modeling
- Scalability
- Maintainability

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
- ReactJS
- Component-first approach
- Storybook for component documentation
- Web-first (mobile-oriented UX)
- Later: React Native for voice/mobile-first workflows

### Style

- Domain-oriented modules (bounded contexts)
- Thin API adapters, rich domain/services
- REST first; eventing later if justified

---

## 4. GitHub as the Source of Truth (All Agents, Including Claude Code)

**Everything is documented in GitHub.** Terminal output should be minimal.

### 4.1 Issue-first workflow

- **Every unit of work is tracked by a GitHub Issue.**
- All agents **must**:
  - work from an assigned issue,
  - keep the issue up to date with progress and decisions,
  - link related PRs/commits,
  - record what was verified (tests, manual checks, etc.).

### 4.2 Kanban board

Use the GitHub Issues Project board as the status system.

**Board columns (in order):**

1. Backlog
2. Refined
3. In-Progress
4. Review
5. QA
6. Done
7. Deployed

Rules:

- An issue must always be in exactly **one** column.
- Move issues immediately when state changes.
- If a review fails, move the issue back to the appropriate implementation lane (Design/FE/BE/DevOps) and note why.

### 4.3 Requirement format and where it lives

All requirements are written as:

- **Epic** → implemented by **User Stories**
- **User Story** → implemented by **Tasks**

Documentation source:

- `docs/reqs.md` is the canonical requirements document.
- Organize `docs/reqs.md` as an outline:
  - App
    - Epic
      - User Story + Acceptance Criteria
        - Tasks + Completion Criteria

GitHub tracking:

- **Every User Story and every Task is a GitHub issue**.
- Epic tracking may be:
  - a GitHub issue with a checklist of user stories, or
  - a GitHub milestone (either is acceptable),
  - but **User Stories and Tasks are mandatory as issues**.

### 4.4 Issue naming and work-type tags

All work issues must include:

1. the **User Story name** (verbatim), and
2. exactly one **work-type @tag** indicating the nature of the work:

- `@FE` Frontend
- `@BE` Backend
- `@AR` Architecture
- `@DE` Design
- `@DO` DevOps

Recommended title format:

- `@TAG — <User Story Name> — <Task Name>`

Examples:

- `@BE — Log a workout — Create workout + set endpoints`
- `@FE — Log a workout — Build workout entry form`

Notes:

- Only the above tags are used.
- Non-tagged agents (Planner/Reviewer/QA/Security) still work via issues, but do not introduce new work-type tags.

### 4.5 Agent lanes and execution order

Agents work through each Epic/User Story in this order:

1. **Architect** (`@AR`)
2. **Designer** (`@DE`)
3. **DevOps** (`@DO`)
4. **Backend** (`@BE`)
5. **Frontend** (`@FE`)

Quality gates:

- **Reviewer** (code + architecture + OWASP/security best practices) must approve before QA.
- **QA Specialist** validates the user experience against Acceptance Criteria and design specs.

---

## 5. Definition of Done (Applies to All Work)

A task or PR is **not done** unless:

- Scope and assumptions are documented
- Code matches existing architecture and conventions
- DB migrations included (if schema changed)
- Tests exist (happy path + ≥1 edge case)
- Security implications noted (even “none”)
- Logs/observability hooks added where appropriate
- Docs updated (README, module docs, ADRs, and/or `docs/reqs.md`)
- Rollback considerations stated

---

## 6. Cross-Agent Conventions

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

## 7. Role Playbooks

The specific role playbooks live in the `agents/` folder as individual files. See:

- `agents/architect.md`
- `agents/planner.md`
- `agents/designer.md`
- `agents/backend.md`
- `agents/frontend.md`
- `agents/code_reviewer.md`
- `agents/security_reviewer.md`
- `agents/qa_specialist.md`
- `agents/devops.md`

For role-specific guidance, open the corresponding file in `agents/`.

---

## 8. Standard Agent Output Template

Agents should end with:

- **What I did**
- **Why**
- **Tradeoffs**
- **Risks**
- **Next steps**
- **Definition of Done status**

**Important:** this template content should be recorded **succinctly but with sufficient detail** as a comment/update on the relevant **GitHub issue** (and PR, when applicable) — **not** as terminal chatter.

---
