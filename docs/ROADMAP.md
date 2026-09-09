# DSAN-core Roadmap

## 1. Purpose

This roadmap describes the evolution of **DSAN-core** as a reference implementation of mechanisms for verifiable and governed digital execution within the broader DSAN architecture.

DSAN-core is not the complete DSAN architecture. The architectural definitions of sovereign entities, Guardians, GuardianOS, Totems, sovereign presence, authority, delegation, communication, governance, and the DSAN Network are defined at the ecosystem level.

The purpose of DSAN-core is to provide an executable and verifiable implementation of selected mechanisms, including:

* event admission and validation;
* cryptographic verification;
* policy evaluation;
* authorization;
* execution;
* state transition;
* ledger persistence;
* deterministic replay;
* state-root derivation;
* Merkle-root verification;
* validator evidence;
* independent auditing;
* synchronization.

The implementation may evolve without redefining the fundamental concepts of the DSAN architecture.

---

# 2. Current Position

The current repository represents a **recovered and stabilized experimental execution kernel**.

The implementation has demonstrated, at local or controlled-network scale:

* signed event submission;
* canonical event hashing;
* policy-based validation;
* lightweight validator voting;
* authorization gating;
* append-only ledger persistence;
* deterministic replay;
* `state_root` derivation;
* Merkle-root calculation;
* independent audit;
* historical ledger normalization;
* validator signature verification;
* basic synchronization.

These capabilities should not be interpreted as evidence of production readiness, Byzantine fault tolerance, or a finalized distributed consensus protocol.

The current development position is approximately:

**Stage 1 — Stabilization → Stage 2 — Independent Verification**

---

# 3. Development Principles

Future development should preserve the following properties:

1. **Deterministic behavior**
2. **Replayability**
3. **Verifiable state derivation**
4. **Cryptographic integrity**
5. **Explicit authorization**
6. **Auditable execution**
7. **Bounded autonomy**
8. **Clear separation of responsibilities**
9. **Implementation transparency**
10. **Architectural compatibility with the wider DSAN ecosystem**

A new feature should not be considered an architectural improvement if it makes execution history less reproducible, less auditable, or less independently verifiable.

---

# 4. Stage 1 — Stabilization

## Goal

Consolidate the recovered implementation into a reproducible and maintainable development baseline.

## Priorities

* stabilize current packet structures;
* remove obsolete implementation inconsistencies;
* preserve deterministic replay;
* stabilize ledger persistence;
* document current execution behavior;
* normalize historical entries;
* establish reproducible development and testing procedures;
* clean repository artifacts and accidental generated files;
* separate implementation details from architectural definitions.

## Deliverables

* stable `README.md`;
* stable `README.pt-BR.md`;
* updated `docs/ARCHITECTURE.md`;
* updated `docs/PROTOCOL.md`;
* normalized ledger representation;
* reproducible local startup procedure;
* reproducible event submission procedure;
* reproducible audit procedure;
* repository hygiene baseline.

## Exit Criteria

* node startup is reproducible;
* execution can be repeated under equivalent conditions;
* replay produces deterministic results;
* audit consistently detects valid and invalid histories;
* persisted execution records contain sufficient information for verification.

---

# 5. Stage 2 — Independent Verification

## Goal

Strengthen the separation between execution and verification.

The verifier must be capable of evaluating execution history without becoming an execution authority.

## Priorities

* maintain a dedicated Auditor Node;
* retrieve execution history independently;
* verify cryptographic integrity;
* reconstruct state through replay;
* compare published and derived state roots;
* detect inconsistent histories;
* generate structured audit results.

## Deliverables

* standalone auditor service or mode;
* formal audit result structure;
* automated replay comparison;
* structured verification diagnostics;
* clear executor/verifier separation.

## Exit Criteria

An independent auditor must be able to:

1. obtain an execution history;
2. verify its integrity;
3. replay the history;
4. derive the resulting state;
5. compare the derived state with the recorded commitment;
6. identify inconsistencies without executing the original actions.

---

# 6. Stage 3 — Persistent Validator Identity

## Goal

Replace ephemeral validator attribution with persistent validator identity.

## Priorities

* persistent validator key material;
* validator identity lifecycle;
* separation between node identity and validator identity;
* stable validator references;
* validator continuity across restarts;
* preparation for membership-aware validation.

## Deliverables

* persistent validator identity model;
* validator identity registry;
* stable public-key references;
* validator lifecycle rules;
* validator bootstrapping procedure.

## Exit Criteria

Validator signatures must be attributable to a stable identity across node restarts and successive verification operations.

---

# 7. Stage 4 — Formal Policy and Authorization Layer

## Goal

Make execution governance explicit rather than dependent on implicit implementation behavior.

## Priorities

* formalize policy representation;
* define admissibility rules;
* define action classes;
* define contextual constraints;
* define authorization requirements;
* define optional physical authorization requirements;
* distinguish authority, authorization, and execution.

The Totem must be treated as one possible authorization or physical-presence mechanism rather than a universal architectural prerequisite.

## Deliverables

* policy schema;
* deterministic policy evaluation;
* authorization model;
* action classification;
* examples of allowed, denied, and gated actions;
* documentation of contextual authorization requirements.

## Exit Criteria

The system must be able to explain why an action was:

* admitted;
* denied;
* authorized;
* physically gated;
* executed;
* or prevented from execution.

---

# 8. Stage 5 — Execution Semantics Hardening

## Goal

Formalize how accepted events become state transitions.

## Priorities

* define event classes;
* define execution semantics;
* define deterministic state transitions;
* constrain non-deterministic inputs;
* distinguish event records from execution results;
* strengthen replay equivalence.

## Deliverables

* execution semantics specification;
* formal state model;
* deterministic transition rules;
* replay-equivalence tests;
* execution-result schema.

## Exit Criteria

Equivalent execution histories must produce equivalent derived state.

The relationship must remain:

**History → Replay → State → Verification**

---

# 9. Stage 6 — Network and Synchronization Hardening

## Goal

Strengthen multi-node behavior without prematurely claiming production-grade consensus.

## Priorities

* strict synchronization validation;
* packet versioning;
* malformed-history rejection;
* conflict detection;
* chain-selection rules;
* replay validation during synchronization;
* peer communication hardening;
* explicit network-state classification.

## Deliverables

* versioned packet schemas;
* improved `/sync` validation;
* conflict-handling rules;
* synchronization diagnostics;
* replay validation during synchronization;
* documented degraded/offline/healthy states.

## Exit Criteria

Nodes must reject malformed or internally inconsistent histories predictably while preserving the ability to verify valid histories exchanged between nodes.

---

# 10. Stage 7 — Protocol Maturation

## Goal

Transform the implementation protocol into a sufficiently stable technical reference.

## Priorities

* formal packet schemas;
* protocol versioning;
* validation rules;
* validator semantics;
* authorization semantics;
* replay semantics;
* audit semantics;
* synchronization semantics;
* trust assumptions;
* threat model.

## Deliverables

* protocol specification;
* packet reference;
* verification model;
* trust model;
* threat model;
* protocol glossary;
* compatibility rules.

## Exit Criteria

An external technical reader should be able to understand the protocol without first reading the implementation source code.

---

# 11. Stage 8 — DSAN Ecosystem Integration

## Goal

Position DSAN-core as an execution and verification component within the broader DSAN architecture.

Integration should preserve the architectural separation between:

* Sovereign Entity;
* Guardian;
* GuardianOS;
* Totem;
* DSAN-core;
* DSAN Network;
* domain applications.

## Priorities

* define service/core interfaces;
* integrate sovereign identity mechanisms;
* integrate sovereign state mechanisms;
* integrate presence and authority representations;
* integrate authorization artifacts;
* support bounded delegation;
* define communication patterns;
* establish network-level evidence exchange.

## Deliverables

* integration contracts;
* service/core interaction model;
* identity integration model;
* authorization integration model;
* evidence exchange model;
* DSAN Network integration documentation.

## Exit Criteria

DSAN-core operates as a clearly bounded kernel within the DSAN ecosystem rather than as an independent definition of the entire architecture.

---

# 12. Stage 9 — Security Maturation

## Goal

Increase assurance through evidence, testing, and formal analysis rather than unsupported security claims.

## Priorities

* cryptographic implementation review;
* replay-protection analysis;
* authorization analysis;
* synchronization security;
* validator security;
* key-management review;
* threat-model refinement;
* penetration/security testing where applicable;
* formal verification of selected critical mechanisms where justified.

## Deliverables

* security review reports;
* threat-model updates;
* key-management procedures;
* security regression tests;
* documented security assumptions.

## Exit Criteria

Security claims made by the project must be traceable to documented mechanisms, tests, analyses, or independent review.

---

# 13. Stage 10 — Production Readiness Assessment

## Goal

Determine whether specific components are suitable for deployment in production environments.

Production readiness must be evaluated independently from architectural maturity.

## Assessment Areas

* cryptography;
* key management;
* persistence;
* networking;
* consensus or validation;
* authorization;
* availability;
* observability;
* recovery;
* upgrade procedures;
* incident response;
* security review;
* operational governance.

## Important Constraint

Completion of the DSAN architectural roadmap does not automatically imply that DSAN-core is production-ready.

Production readiness is an engineering and operational assessment.

---

# 14. Cross-Cutting Work

The following activities continue across all stages.

## Testing

* unit tests;
* integration tests;
* replay tests;
* ledger integrity tests;
* state-root tests;
* Merkle-root tests;
* synchronization tests;
* audit tests;
* authorization tests;
* migration regression tests.

## Observability

* structured logs;
* execution tracing;
* error classification;
* state diagnostics;
* synchronization diagnostics;
* audit diagnostics.

## Documentation

Documentation must remain synchronized with implementation behavior.

When implementation and documentation diverge, the discrepancy must be explicitly resolved rather than silently ignored.

## Repository Hygiene

The repository must not contain:

* private keys;
* production credentials;
* accidental secrets;
* generated Python bytecode;
* obsolete temporary artifacts;
* undocumented experimental remnants.

Experimental or historical material should be explicitly classified rather than silently mixed with the active implementation.

---

# 15. Architectural Boundaries

DSAN-core should not become responsible for concepts belonging to other architectural layers.

| Concept                | Primary architectural responsibility           |
| ---------------------- | ---------------------------------------------- |
| Sovereign Entity       | DSAN architecture                              |
| Guardian               | Guardian architecture                          |
| GuardianOS             | GuardianOS implementation                      |
| Totem                  | Physical sovereignty / authorization mechanism |
| Sovereign Identity     | DSAN architecture                              |
| Sovereign Presence     | DSAN architecture                              |
| Sovereign Authority    | DSAN architecture                              |
| Authorization          | DSAN architecture + implementation             |
| Authorization Artifact | DSAN protocol/implementation                   |
| Execution              | DSAN-core                                      |
| State                  | DSAN-core / DSAN state model                   |
| Ledger                 | DSAN-core                                      |
| Replay                 | DSAN-core                                      |
| Audit                  | DSAN-core                                      |
| Network transport      | DSAN Network                                   |
| Governance             | DSAN ecosystem                                 |
| Domain workflows       | Domain applications                            |

This separation prevents implementation evolution from causing architectural drift.

---

# 16. Totem and Physical Authorization

DSAN-core may implement a Totem-based authorization gate where the execution environment requires one.

This implementation behavior must not be interpreted as establishing a universal DSAN rule that every sovereign execution requires physical authorization.

The architectural distinction is:

**Authority ≠ Authorization ≠ Execution**

and:

**Totem ≠ Sovereignty**

The Totem may provide a physical security boundary, presence signal, authorization factor, or hardware-backed control depending on the implementation context.

---

# 17. Offline and Degraded Operation

Offline operation must remain bounded.

A node operating without network connectivity may continue executing previously permitted operations according to its local state and authorization rules.

However:

**offline ≠ unrestricted autonomy**

In particular, loss of connectivity must not automatically create new authority or permanently bypass revocation, policy, or governance mechanisms.

Future work should explicitly distinguish:

* connected operation;
* degraded operation;
* offline operation;
* recovery;
* synchronization;
* revocation reconciliation.

---

# 18. Guiding Verification Property

The central technical property of DSAN-core remains:

> **Executed history must remain replayable into independently verifiable state.**

This property connects the main mechanisms of the repository:

**Execution History → Deterministic Replay → Derived State → State Root → Independent Verification**

Cryptographic signatures, validator evidence, Merkle roots, authorization records, and audit mechanisms should reinforce this property rather than obscure it.

---

# 19. Current Status

| Stage                                      | Status                                               |
| ------------------------------------------ | ---------------------------------------------------- |
| Stage 1 — Stabilization                    | Largely validated locally                            |
| Stage 2 — Independent Verification         | Implemented in experimental form; maturation ongoing |
| Stage 3 — Persistent Validator Identity    | Planned                                              |
| Stage 4 — Formal Policy and Authorization  | Partially implemented; formalization ongoing         |
| Stage 5 — Execution Semantics Hardening    | Planned                                              |
| Stage 6 — Network Hardening                | Planned                                              |
| Stage 7 — Protocol Maturation              | Documentation baseline established                   |
| Stage 8 — DSAN Ecosystem Integration       | Planned                                              |
| Stage 9 — Security Maturation              | Planned                                              |
| Stage 10 — Production Readiness Assessment | Future                                               |

---

# 20. Final Principle

DSAN-core should evolve without losing the property that makes the implementation independently meaningful:

> **A system that executes governed actions must preserve sufficient evidence for another process to independently determine what happened and what state resulted from that history.**

The implementation may become more distributed, more secure, more autonomous, or more sophisticated.

The verification property must remain.

**DSAN-core — Verifiable Execution Kernel.**
