<!-- filepath: /Users/rob/dev/projects/python/the_lab/docs/adr/adr-002.md -->

## ADR-002: Data Modeling Philosophy

**Decision**  
Prefer immutable “fact” records with derived views.

**Rationale**

- Enables auditing and historical analysis
- Reduces accidental data loss

**Consequences**

- Slightly more complex schema
- Requires explicit derivation logic
