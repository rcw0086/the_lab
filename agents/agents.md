# Agent Charter & Delivery Workflow

## Purpose

This document defines the **agent operating model** for building and shipping this project: authority, workflow, handoffs, and quality gates.

This file is **not** the project/product charter.

---

## Canonical References

Project-level intent, constraints, and architecture defaults live elsewhere:

- `project_charter.md` — **Project mission, non-negotiables, architecture defaults**
- `docs/reqs.md` — **Epics, user stories, acceptance criteria (AC)**
- `docs/adr/` — **Architectural Decision Records (ADRs)**
- `agents/github-workflow.md` — **GitHub project/board operations (source-of-truth mechanics)**

If there is a conflict:

1. `project_charter.md`
2. `docs/reqs.md`
3. ADRs
4. `agents.md` + role playbooks
5. code (as validated by tests/reviews)

---

## Process Authority

### Orchestrator owns execution flow

The **Orchestrator** is the single authority that sequences work across lanes and enforces stage gates.

- No specialist agent may begin work unless the Orchestrator confirms **Entry Criteria** are satisfied.
- No lane is considered complete unless the Orchestrator accepts the **Handoff**.
- If an agent detects missing inputs, ambiguity, or contradictions: stop and return to Orchestrator.

Orchestrator playbook: `agents/orchestrator.md`

---

## Workflow Phases

1. **Planning / Refinement**
   - Planner decomposes work (Epic → Story → Tasks), ensures AC + completion criteria exist.
2. **Execution**
   - Specialists implement per lane order (below), producing artifacts and handoffs.
3. **Review**
   - Code Review + Security Review gate quality and risk.
4. **QA**
   - QA validates AC with evidence; failures route back to the right lane.
5. **Done / Deployed**
   - Work is complete only when QA passes and artifacts are linked.

---

## Lane Order (Hard Order)

The Orchestrator sequences agents through each unit of work in this order:

1. **Planner** (pre-execution readiness only)
2. **Architect (@AR)**
3. **Designer (@DE)**
4. **DevOps (@DO)**
5. **Backend (@BE)**
6. **Frontend (@FE)**
7. **Code Reviewer**
8. **Security Reviewer**
9. **QA Specialist**
10. **Done / Deployed**

---

## Issue Taxonomy & Tags

Work-type tags (implementation lanes):

- `@AR` Architect
- `@DE` Designer
- `@DO` DevOps
- `@BE` Backend
- `@FE` Frontend

Governance roles (no tag required):

- Planner
- Orchestrator
- Code Reviewer
- Security Reviewer
- QA Specialist

**Rule:** the tag (or lane assignment) indicates **who owns the next action**.

---

## Stage Gates (Hard Gates)

Each lane must obey **Entry / Exit / Validation / Failure Handling** gates (defined in each role playbook).

Global gate rule:

- If Entry Criteria are not met → **do not start** → comment what’s missing → return to Orchestrator.
- If Exit Criteria are not met → **do not claim completion** → fix gaps or escalate to Orchestrator.

---

## Required Handoff Contract (Mandatory)

A lane is not complete until a **handoff comment** exists on the GitHub issue and includes:

- **Outputs produced:** (bullets)
- **Artifacts:** (links)
- **Decisions:** (what changed / what was chosen, plus rationale)
- **Constraints / non-negotiables:** (bullets)
- **Risks:** (bullets; include “None identified” if none)
- **Ready for:** (next agent/lane)
- **Blocked items:** (bullets; include “None” if none)
- **Completion status:** (map to completion criteria + Definition of Done)

Next lane may not begin until the Orchestrator validates this handoff.

---

## Assumption Rule (No Silent Assumptions)

If a required input is missing, ambiguous, or conflicts with another artifact:

- do **not** invent silently,
- record the ambiguity on the GitHub issue,
- propose a bounded recommendation,
- route to the correct authority (Planner / Architect / Designer / Orchestrator),
- do not advance the issue until resolved or explicitly accepted as risk.

---

## GitHub as Source of Truth

All work is tracked through GitHub Issues + PRs, with state reflected on the project board.

Operational details (commands, field IDs, status transitions) live in:

- `agents/github-workflow.md`

---

## Definition of Done (DoD)

Work is only “Done” when:

- Acceptance Criteria (AC) are verified by QA (with evidence).
- Code review is complete (approved or explicitly waived with rationale).
- Security review is complete (or waivers recorded with severity + rationale).
- Migrations are safe and documented (if applicable).
- Verification steps are recorded (commands run, what passed).
- Docs/reqs/ADRs are updated as needed and linked.

---

## Standard Agent Output (Required)

Every agent response (and/or issue comment) must end with:

- **Current state:** (what is true now)
- **Actions taken:** (what you changed/produced)
- **Artifacts:** (links)
- **Decisions / assumptions:** (explicit)
- **Risks / blockers:** (explicit)
- **Next recommended lane:** (who should act next)
- **Workflow status:**
  - Lane complete: Yes/No
  - Ready for next: [Agent]
  - Blockers: [None/List]

---

## Role Playbooks

- `agents/orchestrator.md`
- `agents/planner.md`
- `agents/architect.md`
- `agents/designer.md`
- `agents/devops.md`
- `agents/backend.md`
- `agents/frontend.md`
- `agents/code_reviewer.md`
- `agents/security_reviewer.md`
- `agents/qa_specialist.md`
- `agents/github-workflow.md`
