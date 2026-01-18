<!-- filepath: /Users/rob/dev/projects/python/the_lab/docs/adr/adr-006.md -->

## ADR-006: Postgres as System of Record

**Decision**  
Postgres is the authoritative data store.

**Rationale**

- Strong relational guarantees
- Excellent analytical capabilities

**Consequences**

- Schema changes require care
