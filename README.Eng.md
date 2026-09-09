# DSAN Core

## The Verifiable Execution Kernel of the DSAN Network

`dsan-core` is a reference implementation of core mechanisms for **verifiable, governed digital execution** within the Decentralized Sovereign Agent Network (DSAN).

The project provides executable mechanisms for:

* cryptographic identity and signatures;
* canonical event representation;
* event validation;
* policy-based authorization;
* execution decision processing;
* signed event submission;
* ledger persistence;
* deterministic replay;
* Merkle-root generation;
* state reconstruction;
* state-root verification;
* independent auditing;
* ledger synchronization.

`dsan-core` is an **implementation of selected DSAN mechanisms**. It is not, by itself, the complete definition of the DSAN architecture.

The architectural definition of DSAN is maintained by the **DSAN-Ecosystem** repository and its associated architectural specifications.

---

## 1. Relationship to DSAN Architecture

DSAN is an architectural framework in which sovereignty belongs to a sovereign entity and is manifested operationally through appropriate computational mechanisms.

Within this architecture:

```text
Sovereign Entity
       │
       ▼
    Guardian
       │
 ┌─────┴─────┐
 ▼           ▼
GuardianOS   Totem
       │      │
       └──┬───┘
          ▼
      DSAN Core
          │
          ▼
     DSAN Network
```

The components have distinct responsibilities:

| Component           | Primary responsibility                                |
| ------------------- | ----------------------------------------------------- |
| Sovereign Entity    | Source of sovereignty                                 |
| Guardian            | Operational manifestation of the sovereign entity     |
| GuardianOS          | Protected computational environment of the Guardian   |
| Totem               | Optional physical sovereignty or authorization anchor |
| DSAN Core           | Verifiable execution and protocol mechanisms          |
| DSAN Network        | Distributed interaction                               |
| Domain Applications | Application-specific use of DSAN mechanisms           |

`dsan-core` must therefore not be interpreted as redefining the ontology of Guardian, GuardianOS, Totem, or sovereign entities.

---

## 2. What This Repository Implements

The current implementation concentrates on the verifiability of digital execution.

Its principal mechanisms include:

### Identity

Cryptographic identities are used to attribute events and verify signatures.

### Events

Execution-relevant events are represented in a canonical form suitable for hashing, signing, storage, replay, and verification.

### Authorization

Execution decisions are evaluated against applicable policies and authorization conditions.

Authorization is treated as a **decision or verifiable condition for execution**, not as the source of sovereign authority.

### Ledger

Validated events can be recorded in an append-oriented ledger structure.

### Replay

The system supports deterministic reconstruction of state from recorded events.

### State Root

A resulting state can be represented by a cryptographically derived state root, allowing an independent observer to verify whether a reconstructed state corresponds to the expected state.

### Audit

The repository includes mechanisms for independent validation of event integrity, signatures, ledger structure, replay results, and state roots.

---

## 3. Reference Execution Flow

The current implementation provides a concrete execution flow that can be summarized as:

```text
Agent
  │
  ▼
Policy Validation
  │
  ▼
Consensus / Validation
  │
  ▼
Authorization
  │
  ├───────────────┐
  │               │
  ▼               ▼
Execution       Rejection
  │
  ▼
Ledger
  │
  ▼
Deterministic Replay
  │
  ▼
State
  │
  ▼
State Root
  │
  ▼
Independent Audit
```

This diagram describes the **current reference implementation**.

It is not intended to prescribe a mandatory execution pipeline for every DSAN deployment.

Different deployments may use different authorization mechanisms, trust models, execution environments, or governance constraints.

---

## 4. Physical Authorization and the Totem

The current `dsan-core` implementation includes support for a **Totem authorization gate** in selected execution flows.

This is an implementation mechanism.

It should not be interpreted as meaning that every DSAN operation requires a physical Totem.

The architectural model distinguishes:

```text
Sovereign Authority
        ≠
Authorization
        ≠
Execution
```

and:

```text
Totem
        ≠
Guardian
        ≠
GuardianOS
        ≠
Sovereign Entity
```

The Totem may provide a physical anchor or participate in authorization when required by the applicable policy or execution context.

The current Core implementation therefore demonstrates one concrete form of physical authorization while remaining compatible with a broader architecture in which authorization mechanisms are contextual.

---

## 5. Verifiability

A central objective of `dsan-core` is that execution history should not depend exclusively on the trustworthiness of the component that originally performed the execution.

The implementation therefore supports a chain of verification:

```text
Signed Event
     │
     ▼
Canonical Representation
     │
     ▼
Hash
     │
     ▼
Ledger
     │
     ▼
Replay
     │
     ▼
Reconstructed State
     │
     ▼
State Root
     │
     ▼
Independent Verification
```

This allows an independent auditor to reconstruct and verify relevant portions of system state without simply trusting the original executor.

---

## 6. Independent Auditor

The repository includes an auditor-oriented model for independent verification.

An auditor can evaluate, according to the mechanisms implemented by this repository:

* event structure;
* cryptographic signatures;
* event hashes;
* ledger integrity;
* validator information;
* Merkle roots;
* deterministic replay;
* reconstructed state;
* state roots.

The auditor is not an additional source of sovereignty.

Its role is **verification and evidence production**.

---

## 7. Deterministic Replay

Deterministic replay is an important property of the reference implementation.

Given the same valid event history and the same applicable deterministic rules, independent nodes should be able to reconstruct equivalent state.

Conceptually:

```text
Event History
      │
      ▼
   Replay
      │
      ▼
  State S
      │
      ▼
 State Root
```

This provides a basis for:

* reproducibility;
* audit;
* integrity verification;
* state comparison;
* recovery;
* synchronization.

---

## 8. Security Model

`dsan-core` uses cryptographic mechanisms to provide verifiability and integrity.

These mechanisms may include:

* public-key signatures;
* event hashing;
* canonical serialization;
* authenticated state representations;
* Merkle structures;
* deterministic replay;
* independent verification.

Cryptographic verification does not, by itself, establish that an action is legitimate.

Legitimacy depends on the applicable:

* identity;
* context;
* policy;
* authorization;
* state;
* delegation;
* trust relationships;
* governance rules.

Therefore:

> **Cryptographic validity is evidence of integrity and attribution; it is not equivalent to authorization or sovereignty.**

---

## 9. Consensus

The current implementation contains mechanisms for peer validation and majority-style approval.

These mechanisms are part of the current reference implementation.

They should not be interpreted as a claim that DSAN requires one universal consensus algorithm.

A particular deployment may use:

* peer validation;
* quorum-based mechanisms;
* centralized validation;
* federated validation;
* application-specific authorization;
* other appropriate mechanisms.

The architectural requirement is not a particular consensus algorithm.

The requirement is that the deployment's relevant decisions and state transitions remain **appropriately verifiable and governed**.

---

## 10. Offline and Local Operation

The Core may operate with locally available state and information.

However:

> **offline operation does not imply unrestricted autonomy.**

An implementation must preserve applicable authorization, delegation, expiration, revocation, and state constraints while operating without continuous network connectivity.

When connectivity is restored, synchronization must not automatically resurrect authority that has expired or been revoked.

Offline behavior is therefore an implementation and policy concern rather than a universal authorization rule.

---

## 11. Protocol Scope

The protocols implemented by this repository describe mechanisms used by `dsan-core`.

They include mechanisms related to:

* event submission;
* validation;
* ledger operations;
* synchronization;
* replay;
* state reconstruction;
* auditing.

These protocols should be understood as **implementation-level protocols**.

They do not constitute the complete architectural specification of DSAN.

Architectural concepts and invariants are maintained separately in the DSAN-Ecosystem documentation.

---

## 12. Experimental and Reference Status

Unless explicitly stated otherwise, this repository should be considered a **reference and experimental implementation**.

It is intended for:

* research;
* architectural validation;
* protocol experimentation;
* interoperability experiments;
* educational use;
* development of domain-specific applications.

The presence of a working implementation does not imply production readiness, formal certification, regulatory compliance, or security certification.

Security properties should be evaluated against explicit threat models and implementation evidence.

---

## 13. Repository Structure

The repository is organized around implementation concerns:

```text
dsan-core/
├── api/
├── cli/
├── docs/
├── dsan/
│   ├── agent/
│   ├── auditor/
│   ├── core/
│   ├── crypto/
│   ├── epl/
│   ├── network/
│   └── totem/
├── ledgers/
├── tests/
├── README.md
├── README.pt-BR.md
└── requirements.txt
```

The internal structure may evolve as the implementation matures.

Architectural responsibilities should not be inferred solely from directory names.

---

## 14. Relationship with Other DSAN Repositories

`dsan-core` is one component of a larger ecosystem.

| Repository                   | Role                                                                     |
| ---------------------------- | ------------------------------------------------------------------------ |
| `DSAN-Ecosystem`             | Architecture, principles, governance and public documentation            |
| `dsan-core`                  | Verifiable execution kernel and reference mechanisms                     |
| `dsan-guardian` / GuardianOS | Guardian computational environment and physical reference implementation |
| `DSAN-simulator`             | Simulation, experimentation and education                                |
| `DSAN-DREX-ENTERPRISE`       | Enterprise/domain application                                            |
| `radsecure-framework`        | Healthcare/domain application                                            |

The repositories should remain independently understandable while preserving architectural consistency.

---

## 15. Architectural Boundaries

The following distinctions are intentionally preserved:

```text
Entity          ≠ Guardian
Guardian        ≠ GuardianOS
GuardianOS      ≠ Totem
Totem           ≠ GuardianRing
Identity        ≠ Presence
Presence        ≠ Intent
Intent          ≠ Authority
Authority       ≠ Authorization
Authorization   ≠ Execution
Execution       ≠ Evidence
Evidence        ≠ Authority
```

These distinctions prevent implementation details from silently becoming architectural definitions.

---

## 16. Design Principle

The central design principle of this repository is:

> **Execution should be attributable, governed, reproducible, and independently verifiable.**

The Core therefore focuses on mechanisms that allow a system to answer questions such as:

* Who originated an event?
* Was the event cryptographically valid?
* Was the event structurally valid?
* Which authorization conditions applied?
* Was the resulting execution recorded?
* Can the resulting state be reconstructed?
* Can another participant independently verify the state?
* Can the evidence be audited later?

---

## 17. Non-Goals

`dsan-core` does not attempt to:

* define sovereignty itself;
* replace the DSAN architectural specification;
* require a physical Totem for every operation;
* define every possible Guardian implementation;
* define GuardianOS hardware universally;
* prescribe one network topology;
* prescribe one consensus mechanism;
* function as a general-purpose blockchain;
* claim universal security guarantees;
* replace domain-specific governance;
* replace applicable legal or regulatory requirements.

---

## 18. Development Direction

Future development may extend the Core toward:

* richer authorization models;
* contextual authorization classes;
* explicit delegation handling;
* stronger revocation semantics;
* recovery mechanisms;
* interoperable event schemas;
* improved synchronization;
* independent verification tooling;
* Guardian/GuardianOS integration;
* configurable physical authorization mechanisms;
* formal protocol testing;
* stronger threat-model validation.

The implementation should evolve without changing the fundamental architectural distinctions defined by DSAN-Ecosystem.

---

## 19. Relationship to the DSAN Architecture

The relationship can be summarized as:

```text
DSAN-Ecosystem
      │
      │ architectural definition
      ▼
   DSAN Core
      │
      │ implementation
      ├── Identity
      ├── Events
      ├── Authorization
      ├── Ledger
      ├── Replay
      ├── State
      ├── State Root
      └── Audit
```

The Core implements mechanisms.

The Ecosystem defines the architectural context in which those mechanisms acquire meaning.

---

## 20. License

See `LICENSE` for the licensing terms applicable to this repository.

---

## 21. Final Principle

`dsan-core` exists to demonstrate that governed execution can be represented through verifiable computational mechanisms.

Its purpose is not to make technology itself sovereign.

Its purpose is to provide mechanisms through which execution, authorization, state and evidence can be represented and independently verified within the DSAN architecture.

**DSAN — Sovereignty by Architecture.**

