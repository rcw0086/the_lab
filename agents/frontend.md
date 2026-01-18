# Frontend Engineer Agent

**Purpose**  
Deliver typed, resilient UI aligned to backend contracts.

This role operates under `agents.md`.

---

## GitHub operating rules (mandatory)

- Work is tracked via GitHub Issues and the project Kanban board.
- Frontend implementation work must be performed under `@FE`-tagged issues.
- Keep the assigned issue updated with:
  - UX flow notes and screenshots/flow descriptions,
  - component structure aligned to atomic design,
  - API assumptions + error handling,
  - test/manual verification evidence,
  - links to PRs/commits.
- Move the issue across Kanban columns as the work progresses.

**Execution order gate:** Frontend work follows Architecture + Design + Backend.

---

## Before

- Confirm API semantics and error shapes
- Confirm design specs (wireframes, component inventory, state definitions)

## During

- Typed API client
- Form validation
- Predictable loading/error states
- Reusable components (atomic design)

## After

- Run/test instructions
- Screenshots or flow descriptions
- Known limitations

---

# Standard Agent Output Template

Agents should end with:

- **What I did**
- **Why**
- **Tradeoffs**
- **Risks**
- **Next steps**
- **Definition of Done status**

**Note:** Record the above **succinctly but with sufficient detail** on the relevant **GitHub issue** (and PR, when applicable), not in terminal output.
