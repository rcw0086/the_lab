# ADR-008: Training / Workout Data Domain Philosophy (v1.1)

**Status:** Proposed  
**Date:** 2026-01-17  
**Updated:** 2026-01-18  
**Context:** Training & Health Data Platform (Module 1)

---

## Decision

The training domain will be modeled using a **fact-first, event-oriented data model** that preserves _what actually happened_ during training, while allowing flexible derivation of summaries, interpretations, and analytics over time.

The system will prioritize:

- **Fidelity to performed work**
- **Flexibility of expression**
- **Analytical clarity**
- **Future reinterpretation**

---

## Core Principles

### 1. Record What Happened, Not What Was Planned

The primary unit of truth is **performed training**, not intended programming.

- Planned workouts are optional metadata and (if introduced) will live in a separate bounded context
- Performed sets/efforts, reps, load, duration, intensity, and notes are facts
- Deviations are expected and preserved

> Reality beats intent. Always.

---

### 2. Favor Atomic, Composable Facts

Training data should be stored in **small, composable units**, rather than large, pre-aggregated records.

Examples:

- A set/effort is a fact
- A heart-rate trace is a fact
- A time interval is a fact
- A subjective RPE entry is a fact

Aggregates such as:

- volume
- tonnage
- density
- intensity distribution
- zone time

are **derived**, not stored.

#### Clarification: Canonical Set + Modality-Specific Details

A single “set/effort” record may act as the **canonical ordered anchor** for performed work, while **modality-specific attributes** (e.g., strength vs endurance) may be stored in dedicated detail tables.

This:

- prevents the canonical fact record from becoming bloated
- preserves atomicity and queryability
- keeps interpretation and aggregation outside the base fact layer

---

### 3. Support Non-Linear and Irregular Training Structures

The domain must support real-world complexity, including but not limited to:

- Supersets
- Circuits
- EMOMs
- AMRAPs
- Myo-reps
- Cluster sets
- Drop sets
- Interval-based endurance work
- Mixed-modality sessions

This implies:

- No assumption of linear “Exercise → Sets → Reps”
- Relationships between efforts may be hierarchical, graph-like, or temporal
- Structure may be inferred from ordering, grouping, and rest/interval metadata

---

### 4. Preserve Context, Subjective Data, and Narrative Journaling

Training is not purely mechanical.

The system should allow capturing:

- Notes (free-form)
- RPE / RIR
- Perceived difficulty
- Pain or limitation flags
- Environmental context (time of day, location, equipment constraints)

Subjective and narrative data is:

- First-class
- Timestamped
- Attributed to the athlete

#### Clarification: Journal Notes are First-Class Artifacts

Beyond mechanical facts, the system supports **training journaling**: free-form narrative entries recorded over time and linked to relevant entities (e.g., cycles, goals, injuries, sessions).

Notes are stored independently (as durable journal artifacts) and associated via relationships, enabling:

- longitudinal review
- reflection and synthesis
- future retrieval workflows

---

### 5. Time Is a First-Class Dimension

All training facts must be interpretable in time.

This includes:

- Absolute timestamps
- Relative ordering
- Durations
- Rest intervals (explicit or inferred)

Time enables:

- Density analysis
- Fatigue modeling
- Interval alignment
- Trend analysis across sessions

---

### 6. Do Not Overfit to Any One Training Philosophy

The model must not assume:

- Powerlifting
- Bodybuilding
- CrossFit
- Endurance
- Block or concurrent periodization

Instead, it should remain **expressive enough** to model all of them.

Interpretation lives in:

- Queries
- Views
- Analysis layers
  —not in the base schema.

---

### 7. Performed-Only Data in the Fact Layer

The training fact layer stores **performed work only**.

- It does not store planned targets as sibling columns to performed values
- If “planned/prescribed/template” concepts are introduced, they will live in separate tables or bounded contexts
- The performed layer remains stable and audit-friendly even as planning features evolve

This prevents ambiguity such as:

- “which fields are performed vs planned?”
- “which value should analytics trust?”

---

### 8. Immutability by Default, Correction by Addition

Training facts should be:

- Append-only where possible
- Corrected via superseding records, not destructive edits

This supports:

- Auditability
- Historical reinterpretation
- Trust in longitudinal analysis

---

## Non-Goals (Explicitly Out of Scope)

The v1 training domain does **not** aim to:

- Automatically prescribe workouts
- Enforce “correct” technique or programming
- Optimize training plans
- Act as a coaching authority

Those may emerge later as **derived intelligence**, not baked-in assumptions.

---

## Consequences

### Positive

- High-fidelity data capture
- Excellent support for analysis and visualization
- Future-proof against changing training beliefs
- Suitable for ML or advanced analytics later
- Unified journaling supports review and synthesis

### Negative

- Schema is more complex than naïve workout logs
- Requires thoughtful querying and derived views
- UI must guide users without oversimplifying reality
- Modality detail tables require careful consistency rules

---

## Implications for Implementation

- Expect a **core set/effort table** representing ordered performed facts
- Expect grouping/structure constructs (explicit or inferred)
- Expect derived metrics to live outside base tables
- Expect modality-specific details in dedicated tables
- Notes/journaling are first-class and linkable to key entities

---

## Follow-Ups

- Define **Training Log v1 Bounded Context**
- Draft initial schema proposals (sets/efforts, sessions, modules, groupings)
- Identify minimum viable UI flows for accurate data capture
- Create ADR-009: Derived Metrics & Analytics Strategy
- Consider ADR-010: Narrative Notes vs Structured Observations (pain, fatigue, adherence)

---
