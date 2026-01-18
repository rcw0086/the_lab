<!-- filepath: /Users/rob/dev/projects/python/the_lab/docs/adr/adr-001.md -->

# Starter ADR Set

The following ADRs should be created early to lock in architectural intent and prevent drift.

---

## ADR-001: Modular Monolith Architecture

**Decision**  
Use a modular monolith with strict internal boundaries.

**Rationale**

- Lower operational complexity
- Easier refactoring
- Stronger data consistency

**Consequences**

- Requires discipline around boundaries
- Enforced via code review initially
