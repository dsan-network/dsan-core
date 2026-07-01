# DSAN-core Roadmap

## Overview

This roadmap describes the expected evolution of DSAN-core from a recovered and stabilized execution kernel into a more formal verifiable execution infrastructure.

The project has already demonstrated:
- local governed execution,
- ledger persistence,
- deterministic replay,
- `state_root` verification,
- independent local audit,
- historical normalization of ledger entries.

The next stages focus on stabilization, formalization, and stronger network trust assumptions.

---

## Stage 1 — Stabilization

### Goal
Consolidate the recovered branch into a reliable development baseline.

### Priorities
- clean and freeze core packet structure,
- stabilize local node behavior,
- keep ledger persistence predictable,
- preserve replay determinism,
- eliminate ad hoc inconsistencies between legacy and current entries,
- improve repository structure and documentation.

### Deliverables
- stable `README.md`,
- `ARCHITECTURE.md`,
- normalized ledger history,
- reproducible local startup flow,
- reproducible local send/audit flow.

### Exit criteria
- node startup is reliable,
- local execution flow works repeatedly,
- local audit consistently returns `CONSISTENT`,
- all persisted entries carry `state_root`.

---

## Stage 2 — Auditor Node

### Goal
Separate execution from verification more clearly.

### Priorities
- create a dedicated auditor mode or auditor node,
- fetch and verify ledger without participating in execution,
- validate `state_root` independently,
- reject inconsistent histories,
- expose structured audit reports.

### Deliverables
- standalone auditor-node script or service,
- audit report schema,
- automated comparison between node-published state and replay-derived state,
- clearer separation of executor and verifier roles.

### Exit criteria
- an auditor can verify a node without executing actions,
- audit output is structured and reproducible,
- replay mismatch is detected and reported clearly.

---

## Stage 3 — Persistent Validator Identity

### Goal
Move from ephemeral validator signatures to stable validator identity.

### Priorities
- persist validator keys across restarts,
- define validator identity lifecycle,
- distinguish node identity from validator identity,
- prepare membership-aware validation,
- reduce ambiguity in multi-node verification.

### Deliverables
- persistent validator key material,
- validator identity registry model,
- stable public identity references in ledger packets,
- validator bootstrapping rules.

### Exit criteria
- validator identity survives node restart,
- validator signatures can be attributed consistently over time,
- ledger verification can reason about validator continuity.

---

## Stage 4 — Formal Policy Layer

### Goal
Strengthen execution governance through explicit policy definitions.

### Priorities
- formalize EPL or JSON policy format,
- define admissibility semantics,
- define action classes and constraints,
- define Totem requirements per action class,
- document policy evaluation behavior.

### Deliverables
- policy schema,
- example policy files,
- deterministic policy evaluation rules,
- documentation for allowed, blocked, and gated actions.

### Exit criteria
- policy behavior is explicit and testable,
- actions are admitted or denied based on documented rules,
- execution governance no longer depends on implicit code assumptions.

---

## Stage 5 — Network Hardening

### Goal
Make synchronization and multi-node behavior structurally stronger.

### Priorities
- stricter sync validation,
- packet version awareness,
- clearer chain-choice rules,
- stronger treatment of inconsistent histories,
- safer peer communication,
- better distinction between offline, degraded, and healthy network states.

### Deliverables
- improved `/sync` validation rules,
- packet schema versioning,
- conflict-handling logic,
- stronger replay validation during synchronization,
- network state diagnostics.

### Exit criteria
- nodes reject malformed or inconsistent histories predictably,
- sync behavior is version-aware,
- state verification remains valid across node-to-node exchange.

---

## Stage 6 — Execution Semantics Hardening

### Goal
Clarify what execution means and how state transitions must behave.

### Priorities
- formalize event classes,
- refine deterministic state transitions,
- reject non-deterministic execution paths,
- separate event record from execution result semantics,
- improve reproducibility of state derivation.

### Deliverables
- documented execution semantics,
- stricter state model,
- deterministic payload constraints,
- tests for replay equivalence.

### Exit criteria
- replay from identical ledger always yields identical state,
- execution classes are documented,
- state transition logic is explicit and testable.

---

## Stage 7 — Protocol Documentation

### Goal
Turn the recovered implementation into a publishable protocol baseline.

### Priorities
- define packet schema formally,
- document trust assumptions,
- document validator role,
- document Totem role,
- document replay and audit model,
- document synchronization semantics.

### Deliverables
- protocol draft,
- packet reference,
- verification model description,
- trust and threat assumptions section,
- glossary of DSAN-core terms.

### Exit criteria
- external readers can understand the system without reading code first,
- protocol semantics are stable enough for review,
- repository documentation matches implementation behavior.

---

## Stage 8 — DSAN Network Integration

### Goal
Connect DSAN-core to broader DSAN Network services and identity infrastructure.

### Priorities
- integrate with higher-level DSAN services,
- connect execution core to identity and governance layers,
- prepare service-to-core interaction patterns,
- define how DSAN-core fits the wider network architecture.

### Deliverables
- integration contracts,
- service/core interaction model,
- DSAN-core positioning inside DSAN Network,
- network-level execution architecture documentation.

### Exit criteria
- DSAN-core operates as a clearly defined kernel inside the broader ecosystem,
- upper layers can rely on stable execution and verification interfaces.

---

## Cross-cutting work

These areas should progress throughout all stages:

### Testing
- replay tests,
- node execution tests,
- sync validation tests,
- audit consistency tests,
- migration regression tests.

### Observability
- clearer logs,
- better error classification,
- execution tracing,
- audit diagnostics.

### Security review
- signature verification review,
- replay protection review,
- sync validation review,
- validator identity review,
- Totem interaction review.

### Documentation
- keep docs aligned with implementation,
- avoid overstating features not yet stabilized,
- record architectural decisions as the protocol evolves.

---

## Guiding principle

DSAN-core should evolve by preserving one core property above all others:

> executed history must remain replayable into independently verifiable state

If a future feature weakens replayability, auditability, or deterministic state derivation, it should not be considered an architectural improvement.

---

## Current status marker

The repository currently stands between **Stage 1** and **Stage 2**:

- Stage 1 is largely validated locally.
- Stage 2 is the next most valuable milestone.