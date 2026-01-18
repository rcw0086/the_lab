<!-- filepath: /Users/rob/dev/projects/python/the_lab/docs/adr/adr-007.md -->

## ADR-007: Avoid Premature Distributed Systems

**Decision**  
No queues, caches, or microservices until justified.

**Rationale**

- Complexity tax is real
- Personal scale does not justify it yet

**Consequences**

- Some synchronous operations initially
