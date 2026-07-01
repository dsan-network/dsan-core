# 🛡️ DSAN-core

**The Verifiable Execution Kernel of the DSAN Network**

[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

# Why DSAN-core Exists

Modern distributed systems have become increasingly capable of making autonomous decisions.

They can authenticate identities, exchange encrypted messages, interact with external systems and execute actions automatically.

However, one architectural problem remains largely unresolved:

> **Who governs execution?**

Most systems implicitly assume:

```
Decision → Execution
```

As intelligent systems become more autonomous, this assumption becomes increasingly unsafe.

DSAN-core was created to introduce an explicit execution-governance layer between decision and execution.

Instead of automatically executing every valid request, DSAN-core requires that execution be:

- cryptographically attributable,
- policy validated,
- consensus approved,
- physically authorized,
- replayable,
- independently auditable.

Rather than functioning as another blockchain, DSAN-core is designed as a **verifiable execution kernel**, capable of reconstructing its execution state entirely from recorded history.

---

# What DSAN-core Does

DSAN-core currently implements:

- Digital identity based on Ed25519
- Canonical event hashing
- Signed event submission
- Policy-based execution validation
- Majority-style peer approval
- Totem-gated execution authorization
- Local append-only ledger
- Merkle Root computation
- Deterministic replay engine
- Derived `state_root`
- Independent audit through replay
- Ledger synchronization with structural validation

The objective is not merely to record events, but to ensure that executed history can always be reconstructed into an independently verifiable state.

---

# Architectural Overview

The current architecture is organized into six logical layers.

```
Agent
   │
   ▼
Policy Validation (EPL)
   │
   ▼
Consensus
   │
   ▼
Totem Authorization
   │
   ▼
Execution
   │
   ▼
Ledger
   │
   ▼
Replay Engine
   │
   ▼
State Root
   │
   ▼
Independent Audit
```

Every executed action follows this deterministic verification pipeline.

---

# Core Components

## Agent Layer

Agents are responsible for creating signed execution requests.

Each event contains:

- sender identity
- payload
- nonce
- previous ledger hash

The event is canonically serialized, signed using Ed25519 and hashed before submission.

---

## Policy Layer (EPL)

The Execution Policy Layer evaluates whether an action is admissible before execution.

Policy validation occurs before consensus and before any state transition.

Current implementations include simple rule evaluation, while future versions will support formal policy definitions.

---

## Consensus Layer

Nodes exchange approval votes before execution.

The current implementation uses a lightweight majority-based coordination mechanism suitable for development and experimentation.

This layer is intentionally separated from execution itself.

---

## Totem Layer

The Totem represents the physical authorization boundary of the DSAN architecture.

While cryptography proves identity, the Totem proves execution control.

Execution only proceeds after explicit authorization through the Totem.

Current implementations support manual authorization during development, while future versions will integrate dedicated hardware (DSAN Guardian), biometrics and secure cryptographic elements.

The Totem transforms execution from a purely digital operation into a physically accountable action.

---

## Ledger Layer

Each executed event is stored as an immutable ledger entry containing:

- original event
- event hash
- validator signatures
- execution result
- replay-derived state root

The ledger serves simultaneously as execution history and replay substrate.

---

## Replay Layer

The replay engine reconstructs system state exclusively from ledger history.

Events are applied deterministically in sequence.

The resulting state is serialized canonically and hashed, producing the final `state_root`.

Because replay is deterministic, any third party can independently verify the resulting state.

---

# Why Replay Matters

Traditional systems require trusting the current state maintained by a running server.

DSAN-core removes that dependency.

Instead, any verifier can rebuild the complete execution state directly from ledger history.

This enables:

- deterministic verification
- historical reproducibility
- state commitments
- independent auditing
- replay consistency validation

---

# Why Totem Exists

Most distributed systems treat cryptographic identity as sufficient authorization.

DSAN separates these concepts.

A valid signature proves **who requested** an action.

The Totem proves **that execution was intentionally authorized**.

This additional authorization boundary significantly reduces the risk of uncontrolled remote execution in sensitive environments.

---

# Repository Structure

```
dsan/
├── agent/
├── core/
│   ├── context.py
│   ├── replay.py
│   └── state.py
├── crypto/
├── epl/
├── network/
└── totem/

docs/
├── ARCHITECTURE.md
├── PROTOCOL.md
└── ROADMAP.md

clisend.py
cliaudit.py
migrate_state_roots.py
```

---

# Typical Execution Flow

1. An Agent creates a signed event.
2. The Node validates the sender signature.
3. The event hash is recomputed.
4. Replay protection is checked.
5. Policy rules are evaluated.
6. Peer approval is requested.
7. The Totem authorizes execution.
8. The action is executed.
9. Validators sign the event.
10. A new ledger packet is persisted.
11. The `state_root` is updated.
12. The node exposes the new state for independent verification.

---

# Getting Started

## Start a local node

```bash
python -m dsan.network.node node1 5001
```

---

## Submit an event

```bash
python clisend.py
```

---

## Authorize execution

When prompted by the node:

```
🔐 Totem gesture:
```

perform the requested authorization.

Current development versions use manual confirmation.

Future versions will use the DSAN Guardian hardware device.

---

## Audit the node

```bash
python cliaudit.py
```

The auditor independently reconstructs the state from ledger history and verifies consistency.

---

# Current Status

The current implementation successfully demonstrates:

- deterministic event execution
- append-only ledger persistence
- replay-based state reconstruction
- derived state verification
- per-entry `state_root`
- independent local audit
- structural ledger synchronization

The repository currently represents a recovered and stabilized execution kernel suitable for further protocol evolution.

---

# Current Limitations

DSAN-core remains experimental.

The current implementation does **not** yet provide:

- Byzantine Fault Tolerant consensus
- production-grade network transport
- persistent validator identity
- finalized governance model
- production Totem hardware integration
- complete Execution Policy Language (EPL)

These capabilities are planned in future development stages.

---

# Documentation

Additional documentation is available in the `docs/` directory.

- **ARCHITECTURE.md** — System architecture
- **PROTOCOL.md** — Packet structure and protocol behavior
- **ROADMAP.md** — Planned evolution of the project

---

# Positioning

DSAN-core should not be understood as another blockchain implementation.

Its primary purpose is to provide a **verifiable execution kernel** where execution becomes:

- cryptographically attributable,
- policy governed,
- physically authorizable,
- replayable,
- independently auditable.

Execution itself becomes a verifiable system primitive.

---

# Part of the DSAN Ecosystem

DSAN-core is one component of the broader **DSAN Network**.

The ecosystem includes:

- **DSAN Ecosystem** — Architectural framework
- **DSAN-core** — Verifiable execution kernel
- **DSAN Guardian** — Physical authorization layer
- Domain-specific systems such as **RadSecure**

Together these components establish an architecture for governed execution in autonomous and distributed systems.

---

# Intellectual Property Notice

DSAN-core is released under the Apache 2.0 License.

Certain implementation details, hardware designs, execution models and domain-specific applications may be subject to ongoing intellectual property protection and are intentionally omitted from the public implementation.

---

# Research Vision

As autonomous systems become increasingly capable of acting without human intervention, execution itself must become accountable.

DSAN-core explores a future in which every executed action can be independently verified, contextually governed and physically authorized.

Its long-term objective is to establish execution as a first-class, auditable and sovereign capability of distributed intelligent systems.

