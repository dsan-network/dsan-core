# DSAN Core Architecture

## 1. Overview

`dsan-core` is a reference implementation of mechanisms for **verifiable and governed digital execution** within the DSAN architecture.

Its current implementation combines:

* event admission;
* cryptographic validation;
* policy evaluation;
* execution authorization;
* ledger persistence;
* deterministic replay;
* state reconstruction;
* state-root generation;
* Merkle-root verification;
* validator signatures;
* independent auditing;
* ledger synchronization.

The central principle of the implementation is:

> **An executed action should be reproducible and independently verifiable from its recorded history.**

A node should not merely state that an action occurred. It should expose sufficient evidence for another participant to reconstruct the relevant state and verify the resulting commitments independently.

This document describes the **internal architecture of the current `dsan-core` implementation**.

It does not replace the architectural definition maintained by `DSAN-Ecosystem`.

---

# 2. Relationship to the DSAN Architecture

The DSAN architecture distinguishes between the sovereign entity, its operational manifestation, its computational environment, physical anchoring mechanisms, execution mechanisms, and the distributed network.

Conceptually:

```text
Sovereign Entity
       │
       │ operational manifestation
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

These components have different responsibilities.

| Component           | Architectural role                                    |
| ------------------- | ----------------------------------------------------- |
| Sovereign Entity    | Source of sovereignty                                 |
| Guardian            | Operational manifestation of the sovereign entity     |
| GuardianOS          | Protected computational environment                   |
| Totem               | Optional physical sovereignty or authorization anchor |
| DSAN Core           | Verifiable execution and protocol mechanisms          |
| DSAN Network        | Distributed interaction                               |
| Domain Applications | Context-specific applications                         |

`dsan-core` implements mechanisms within this architecture.

It does not define the meaning of sovereignty itself.

---

# 3. Scope of This Architecture

This document describes the architecture of the current Core implementation, including:

```text
Agent
  │
  ▼
Event
  │
  ▼
Validation
  │
  ▼
Policy
  │
  ▼
Authorization
  │
  ▼
Execution
  │
  ▼
Ledger
  │
  ▼
Replay
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

This is an **implementation flow**, not a universal DSAN execution pipeline.

A different DSAN deployment may use different combinations of:

* authorization mechanisms;
* validators;
* consensus mechanisms;
* physical authorization;
* execution environments;
* trust relationships;
* network topology.

---

# 4. Core Architectural Principle

The primary architectural concern of `dsan-core` is the relationship between **execution and verifiability**.

The implementation is designed around the following chain:

```text
Event
  ↓
Validation
  ↓
Execution
  ↓
Recorded History
  ↓
Deterministic Replay
  ↓
Reconstructed State
  ↓
State Root
  ↓
Independent Verification
```

This transforms the ledger from a passive record into a basis for reproducible state reconstruction.

The objective is not merely to preserve historical records, but to make relevant execution results independently checkable.

---

# 5. Agent

The Agent creates and submits events to the Core.

### Responsibilities

* construct event payloads;
* associate the event with a cryptographic identity;
* assign a `nonce`;
* reference previous history through `prev_hash`;
* serialize the event canonically;
* sign the event using Ed25519;
* calculate the event hash.

A representative event structure is:

```json
{
  "event": {
    "sender": "alice",
    "payload": {},
    "nonce": "...",
    "prev_hash": "..."
  },
  "hash": "...",
  "signature": "...",
  "sender_sig_pub": "..."
}
```

The Agent provides event attribution and cryptographic evidence.

It does not, by itself, establish authorization to execute the event.

---

# 6. Node

The Node is the primary execution coordinator of the current implementation.

### Responsibilities

* receive events;
* verify sender signatures;
* validate event hashes;
* reject replayed nonces;
* verify `prev_hash` continuity;
* evaluate applicable policies;
* coordinate validation or voting;
* evaluate execution authorization;
* execute authorized events;
* compute resulting state;
* compute `state_root`;
* collect validator signatures;
* persist execution packets;
* expose verification and synchronization endpoints.

Relevant endpoints include:

```text
/state
/root
/state_root
/ledger
/vote
/receive
/sign
/sync
```

The Node therefore combines several implementation responsibilities that may be separated differently in future deployments.

---

# 7. Policy Layer

The Policy Layer determines whether an event satisfies the applicable execution rules.

Its current responsibilities include:

* evaluating event permissions;
* rejecting invalid or disallowed actions;
* contributing to execution governance.

The Policy Layer does not create sovereign authority.

It evaluates whether a particular operation satisfies the rules applicable to the execution context.

Conceptually:

```text
Authority
    │
    │ contextualized by
    ▼
Policy
    │
    ▼
Authorization Decision
```

---

# 8. Authorization

Authorization is the mechanism through which the implementation determines whether an otherwise valid event may proceed to execution.

The architecture deliberately distinguishes:

```text
Authority
    ≠
Authorization
    ≠
Execution
```

The Core therefore treats authorization as a verifiable condition or decision associated with an execution request.

Authorization may depend on:

* identity;
* state;
* policy;
* context;
* delegation;
* trust;
* physical authorization;
* other deployment-specific constraints.

---

# 9. Totem Authorization

The current implementation includes a Totem authorization gate in selected execution flows.

The Totem is therefore represented in the Core as an **authorization mechanism**, not as the source of sovereignty.

```text
Sovereign Entity
       │
       ▼
    Guardian
       │
       ├───────────────┐
       ▼               ▼
 GuardianOS          Totem
       │               │
       └───────┬───────┘
               ▼
           Execution
```

The current implementation uses the Totem gate as part of its reference execution model.

This does not imply:

> every DSAN operation requires a Totem.

Instead:

> **physical authorization may be required when the applicable policy, context, or deployment demands it.**

The current implementation represents one concrete realization of this mechanism.

---

# 10. Ledger

The Ledger provides persistent execution history.

A representative persisted entry may contain:

```json
{
  "event": {},
  "hash": "...",
  "validators": [],
  "result": "...",
  "state_root": "..."
}
```

### Ledger properties

* append-oriented;
* locally persistent;
* replayable;
* cryptographically referenced;
* suitable for synchronization;
* suitable for independent verification.

The Ledger is evidence of recorded execution history.

It is not itself the source of authority.

---

# 11. Replay Engine

The Replay Engine reconstructs state by applying valid historical events in sequence.

### Responsibilities

* iterate through ledger history;
* apply events according to deterministic state-transition rules;
* reconstruct resulting state;
* calculate the corresponding `state_root`.

Conceptually:

```text
Ledger History
      │
      ▼
    Replay
      │
      ▼
 Reconstructed State
      │
      ▼
  State Root
```

Replay is fundamental to the Core's verification model.

---

# 12. State Model

The State Model represents the deterministic state resulting from execution history.

Its responsibilities include:

* receiving an event;
* interpreting its payload;
* applying the corresponding state transition;
* maintaining deterministic state;
* exposing a representation suitable for hashing.

The current implementation supports transfer-like events and a generic fallback path for non-typed payloads.

The state model is an implementation mechanism and should not be confused with the broader concept of **Sovereign State** in the DSAN architecture.

---

# 13. State Root

The `state_root` is a cryptographic commitment to the resulting state reconstructed by the Core.

Its purpose is to allow an independent participant to determine whether its own replay produces the same state commitment.

Conceptually:

```text
Recorded Events
      │
      ▼
Deterministic Replay
      │
      ▼
     State
      │
      ▼
  state_root
```

The state root therefore provides evidence about the resulting computational state.

It does not itself establish sovereignty, authority, or legitimacy.

---

# 14. Validator Layer

Validators provide additional cryptographic evidence associated with execution packets.

### Responsibilities

* sign event hashes;
* expose validator public keys;
* contribute signatures to packet verification;
* support later synchronization validation.

The current implementation provides a lightweight validator model.

It is not yet a complete validator-governance framework.

Future deployments may implement different validator selection and governance mechanisms.

---

# 15. Consensus and Validation

The current Core includes peer validation and majority-style approval mechanisms.

These mechanisms are implementation choices.

They should not be interpreted as the universal consensus architecture of DSAN.

Possible deployment models include:

* peer validation;
* quorum mechanisms;
* federated validation;
* centralized validation;
* application-specific validation;
* other appropriate mechanisms.

The architectural objective is that relevant decisions and state transitions remain appropriately **governed and verifiable**.

---

# 16. Auditor

The Auditor is an independent verification mechanism.

Its fundamental architectural purpose is to separate:

```text
Execution
    ≠
Verification
```

The Auditor may:

* retrieve ledger data;
* retrieve published state information;
* verify event structure;
* verify event hashes;
* verify `prev_hash` continuity;
* verify signatures;
* replay the ledger;
* reconstruct state;
* recompute the state root;
* compare independent results.

This allows the system to evaluate execution evidence without requiring the auditor to reproduce the original execution process.

---

# 17. Auditor Node

The Auditor Node is a dedicated verification service.

It is intentionally separated from the execution role.

### Responsibilities

* retrieve ledger data from execution nodes;
* validate ledger packet structure;
* verify canonical event hashes;
* verify `prev_hash` continuity;
* verify validator signatures;
* recompute the Merkle root;
* replay ledger history;
* recompute the state root;
* compare local results against published commitments;
* produce a structured audit result.

A simplified model is:

```text
Execution Node
      │
      │ ledger + commitments
      ▼
 Auditor Node
      │
 ┌────┼───────────────┐
 ▼    ▼               ▼
Hash  Signatures     Replay
 │    │               │
 └────┴───────┬───────┘
               ▼
        Independent Result
               │
        ┌──────┴──────┐
        ▼             ▼
    CONSISTENT      MISMATCH
```

This separation is one of the central architectural properties of the current Core implementation.

---

# 18. Merkle Root and State Root

The Core exposes two complementary cryptographic views.

### Merkle Root

The Merkle root summarizes the hashes of recorded ledger entries.

It answers approximately:

> **What history was recorded?**

### State Root

The state root summarizes the state derived from replaying that history.

It answers approximately:

> **What state does that history produce?**

Conceptually:

```text
Ledger
 ├──────────────► Merkle Root
 │
 └──► Replay ───► State ───► State Root
```

The two commitments serve different verification purposes.

---

# 19. Data Flow

The current reference implementation can be represented as:

### Execution

```text
1. Agent creates a signed event.
2. Node receives the event.
3. Cryptographic and structural validation occurs.
4. Policy rules are evaluated.
5. Validation or voting mechanisms are applied.
6. Applicable authorization conditions are evaluated.
7. Authorized execution occurs.
8. Resulting state is calculated.
9. State root is generated.
10. Validator signatures are attached.
11. Execution history is persisted.
```

### Verification

```text
12. Auditor retrieves execution history.
13. Auditor validates packet structure.
14. Auditor verifies hashes.
15. Auditor verifies signatures.
16. Auditor verifies chain continuity.
17. Auditor recalculates the Merkle root.
18. Auditor replays the ledger.
19. Auditor reconstructs state.
20. Auditor recalculates the state root.
21. Auditor compares independent commitments.
```

---

# 20. Verification Model

The Core therefore provides multiple layers of evidence:

```text
Cryptographic Identity
        │
        ▼
Event Signature
        │
        ▼
Event Hash
        │
        ▼
Ledger History
        │
        ├──────────────► Merkle Root
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

Each layer answers a different question.

No individual cryptographic mechanism should be interpreted as establishing the complete legitimacy of an action.

---

# 21. Offline and Local Operation

The current Core may operate using locally available state and history.

Offline operation must nevertheless preserve applicable constraints.

In particular:

```text
Offline
  ≠
Unrestricted Autonomy
```

An implementation should account for:

* authorization expiration;
* delegation limits;
* revocation;
* state validity;
* synchronization conflicts;
* recovery procedures.

Reconnection must not automatically restore authority that has expired or been revoked.

---

# 22. Historical Normalization

The current implementation includes normalization of historical ledger entries.

Earlier entries could lack per-entry `state_root` information.

A migration mechanism was introduced to reconstruct and attach progressive state-root information to historical entries.

This improves:

* audit consistency;
* synchronization;
* replay traceability;
* historical uniformity;
* future protocol versioning.

Historical normalization is therefore treated as an implementation migration mechanism rather than an alteration of the underlying architectural model.

---

# 23. Current Trust Model

The current implementation assumes a controlled or small-scale environment.

Its present trust assumptions include:

* controlled development or test environments;
* structurally valid peer messages;
* deterministic replay;
* limited adversarial modeling;
* no complete Byzantine adversary model.

These assumptions are sufficient for validating the current execution-verification architecture.

They are not sufficient to establish production-grade security under unrestricted adversarial conditions.

---

# 24. Current Limitations

The current implementation does not yet provide:

* Byzantine fault-tolerant consensus;
* persistent validator governance;
* a finalized network membership model;
* a complete asynchronous consensus protocol;
* strict packet-schema versioning;
* a finalized EPL specification;
* a fully isolated production auditor architecture;
* generalized cryptographic proof packaging beyond the mechanisms currently implemented.

These limitations are part of the current implementation status and should not be interpreted as architectural impossibilities.

---

# 25. Current Validated Stage

The current recovered implementation has demonstrated:

* successful node startup;
* ledger loading from disk;
* event submission;
* event execution;
* ledger growth;
* deterministic replay;
* state-root publication;
* independent local audit;
* consistent audit results;
* migration of historical entries to include `state_root`;
* dedicated Auditor Node execution;
* remote Merkle-root verification;
* validator-signature verification;
* remote audit results reporting `CONSISTENT`.

These statements describe the current implementation stage.

They should not be interpreted as universal security or production-readiness claims.

---

# 26. Architectural Direction

The next development directions include:

### 26.1 Persistent Validator Identity

Stable cryptographic identities for validator roles across sessions and nodes.

### 26.2 Formal EPL and Policy Semantics

A stronger declarative representation of admissibility and execution constraints.

### 26.3 Contextual Authorization

Support for different authorization requirements depending on operation, context, risk, policy, and deployment.

### 26.4 Revocation and Recovery

Explicit handling of authority expiration, revocation, recovery, and synchronization.

### 26.5 Stricter Synchronization

Version-aware synchronization and stronger validation of historical packets.

### 26.6 Guardian and GuardianOS Integration

Integration with the operational Guardian model while preserving the separation between Guardian, GuardianOS, Totem, and Core.

### 26.7 Independent Verification

Expansion of auditor tooling and evidence formats.

---

# 27. Architectural Boundaries

The Core intentionally preserves the following distinctions:

```text
Sovereign Entity ≠ Guardian
Guardian ≠ GuardianOS
GuardianOS ≠ Totem
Totem ≠ GuardianRing

Identity ≠ Presence
Presence ≠ Intent
Intent ≠ Authority
Authority ≠ Authorization
Authorization ≠ Execution
Execution ≠ Evidence
Evidence ≠ Authority
```

These distinctions prevent implementation mechanisms from silently becoming architectural definitions.

---

# 28. What the Core Does Not Define

`dsan-core` does not independently define:

* the nature of sovereignty;
* the complete DSAN ontology;
* all Guardian implementations;
* all GuardianOS implementations;
* a universal Totem requirement;
* one mandatory consensus algorithm;
* one mandatory network topology;
* one universal trust model;
* domain-specific governance;
* legal authority;
* regulatory compliance.

These concerns belong to the appropriate architectural, governance, implementation, or application layers.

---

# 29. Implementation Independence

The Core should remain independent of a specific hardware platform wherever practical.

The current Totem mechanism may be implemented or simulated through a particular interface, but the architectural concept of physical authorization should not be permanently tied to a specific device.

Likewise, cryptographic libraries, database technologies, transport protocols, or runtime environments are implementation choices.

The architectural principles should survive technological substitution.

---

# 30. Positioning

`dsan-core` should therefore be understood as:

> **a reference implementation of verifiable execution mechanisms within the DSAN architecture.**

Its central proposition is not simply:

> “events are stored.”

It is:

> **“executed events can be reconstructed into state, and the resulting state can be independently verified.”**

This distinction defines the primary architectural identity of the Core.

---

# 31. Final Principle

The purpose of `dsan-core` is to provide computational mechanisms through which execution can become:

* attributable;
* governed;
* reproducible;
* auditable;
* independently verifiable.

The Core does not make technology sovereign.

It provides mechanisms through which sovereign entities and governed systems can operate with verifiable execution evidence within the broader DSAN architecture.

**DSAN — Sovereignty by Architecture.**
