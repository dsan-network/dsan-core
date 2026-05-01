# DSAN-core Architecture

## Overview

DSAN-core is a verifiable execution kernel for governed event processing. Its current architecture combines event admission, policy checks, execution authorization, ledger persistence, deterministic replay, and local auditability.

The core principle is simple: **an executed action must be reproducible from ledger history**.  
A node should not only say that something happened; it should expose enough structure for a third party to verify the resulting state independently.

---

## Architectural goals

The current architecture is designed to support:

- governed event execution,
- append-only local ledger persistence,
- canonical event hashing,
- validator signatures,
- replay-based state reconstruction,
- externally checkable `state_root`,
- historical normalization of ledger entries,
- independent audit without trusting the executor alone.

---

## Core components

### 1. Agent

The agent creates signed events.

**Responsibilities**
- build an event payload,
- attach sender identity,
- attach `nonce`,
- attach `prev_hash`,
- serialize canonically,
- sign with Ed25519,
- compute event hash.

**Output structure**
```json
{
  "event": {
    "sender": "alice",
    "payload": {...},
    "nonce": "...",
    "prev_hash": "..."
  },
  "hash": "...",
  "signature": "...",
  "sender_sig_pub": "..."
}
```

---

### 2. Node

The node is the execution coordinator.

**Responsibilities**
- receive events,
- verify sender signature,
- validate event hash,
- reject replayed nonces,
- check chain continuity through `prev_hash`,
- evaluate policy rules,
- gather votes,
- require Totem authorization,
- execute the event,
- compute `state_root`,
- collect validator signatures,
- persist the final packet,
- expose verification endpoints.

**Relevant endpoints**
- `/state`
- `/root`
- `/state_root`
- `/ledger`
- `/vote`
- `/receive`
- `/sign`
- `/sync`

---

### 3. Policy layer

The policy layer decides whether an event is admissible before execution.

**Current role**
- evaluate event permission,
- block invalid or disallowed actions before execution.

This is the beginning of the DSAN execution-governance model.

---

### 4. Totem layer

The Totem layer represents execution authorization beyond logical validation.

**Current role**
- gate execution after consensus/policy validation,
- simulate or abstract a stronger authorization boundary.

In the current recovered stage, Totem is part of the execution flow but not yet a finalized hardware-backed trust anchor.

---

### 5. Ledger

The ledger is the persistent execution history.

Each persisted entry may contain:

```json
{
  "event": {...},
  "hash": "...",
  "validators": [...],
  "result": "...",
  "state_root": "..."
}
```

**Ledger properties**
- append-oriented,
- locally persisted as JSON,
- replayable in sequence,
- normalizable across legacy entries.

---

### 6. Replay engine

The replay engine reconstructs state by reapplying ledger events in order.

**Responsibilities**
- iterate through ledger history,
- apply each event to the state model,
- compute final derived state,
- produce deterministic `state_root`.

This is what turns the ledger from a passive event log into a verifiable execution record.

---

### 7. State model

The state model is the deterministic state-transition layer.

**Responsibilities**
- receive an event,
- interpret the payload,
- mutate the state deterministically,
- expose a hashed representation of the resulting state.

The current implementation already supports deterministic application of transfer-like events and a generic fallback path for non-typed payloads.

---

### 8. Validator layer

Validators sign event hashes after execution approval.

**Responsibilities**
- sign the event hash,
- expose validator public key,
- contribute to packet verifiability,
- support later sync validation.

This is currently a lightweight validation layer, not a full validator governance framework.

---

### 9. Auditor

The auditor is an independent verifier.

**Responsibilities**
- fetch ledger from node,
- fetch node-reported `state_root`,
- replay ledger locally,
- compare local replay result with published state,
- report consistency or mismatch.

This separates **execution** from **verification**, which is the key architectural leap of DSAN-core.

### 10. Auditor Node

The Auditor Node is a dedicated verification service separated from execution.

**Responsibilities**
- fetch remote ledger data from executor nodes,
- validate ledger packet structure,
- verify canonical event hashes,
- verify `prev_hash` chain continuity,
- verify validator signatures,
- recompute the Merkle root,
- replay ledger history locally,
- compare derived state against the remote node’s published `state_root`,
- emit a structured audit result.

This creates an explicit architectural split between:
- execution authority,
- verification authority.

That separation is central to DSAN-core’s current evolution from executed ledger toward verifiable execution infrastructure.

---

## Data flow

Current high-level flow:

1. Agent creates a signed event.
2. Node receives packet.
3. Node validates signature, hash, nonce, and `prev_hash`.
4. Policy layer decides whether the event is allowed.
5. Node gathers votes.
6. Totem authorizes execution.
7. Node executes the event.
8. Replay-derived `state_root` is computed.
9. Validator signatures are attached.
10. Packet is written to the ledger.
11. Auditor can later replay the ledger and verify the published state.

## Auditor flow

The current auditor flow is:

1. Auditor fetches `/ledger`, `/state`, `/root`, and `/state_root` from a target node.
2. Auditor validates packet structure and hash integrity.
3. Auditor checks `prev_hash` continuity across the ledger.
4. Auditor verifies validator signatures.
5. Auditor recalculates the Merkle root from ledger hashes.
6. Auditor replays the ledger locally to recompute `state_root`.
7. Auditor compares local results with the node’s published commitments.
8. Auditor emits `CONSISTENT` or `MISMATCH`.

---

## Verification model

DSAN-core currently exposes two distinct verification views:

### Ledger root view
The Merkle root summarizes the ledger hashes.

**Purpose**
- compact integrity commitment over recorded entries.

### State root view
The `state_root` summarizes the derived execution state after replay.

**Purpose**
- verify the resulting state of execution,
- allow independent recomputation,
- detect divergence between published state and actual ledger history.

These two views are complementary:
- **Merkle root** answers: “What history was recorded?”
- **State root** answers: “What state does that history produce?”

---

## Current trust model

At the current stage, DSAN-core assumes:

- local or small-scale controlled environments,
- honest execution within a developer/test setup,
- structurally valid peer messages,
- deterministic replay code path,
- no Byzantine adversary model.

This is sufficient for validating the execution-verification architecture, but not enough for production-grade adversarial deployment.

---

## Current limitations

The current architecture still lacks:

- Byzantine fault tolerant consensus,
- persistent validator identity governance,
- formal network membership model,
- asynchronous consensus protocol,
- strict packet schema versioning,
- finalized EPL specification,
- production-grade auditor-node separation,
- cryptographic proof packaging beyond local replay checks.

---

## Historical normalization

A key architectural transition already validated in the recovered branch is ledger normalization.

Earlier entries existed without per-entry `state_root`.  
A migration step was introduced to recompute and attach progressive `state_root` values across legacy history.

This matters because homogeneous historical packets improve:
- audit consistency,
- sync validation,
- replay traceability,
- future protocol versioning.

---

## Current validated stage

The current recovered stage has already demonstrated:

- successful node startup,
- ledger loading from disk,
- event submission and execution,
- ledger growth,
- deterministic replay,
- state-root publication,
- independent local audit with `CONSISTENT` result,
- migration of historical entries to include `state_root`.
- dedicated Auditor Node execution,
- remote Merkle root verification,
- validator-signature verification by the auditor,
- remote audit result with `CONSISTENT`.

---

## Architectural direction

The next major architectural moves are:

1. **Auditor node mode**  
   A dedicated verifier process that does not execute actions, only validates history and state.

2. **Persistent validator identity**  
   Stable cryptographic identities for validator roles across sessions and nodes.

3. **Formal EPL/policy semantics**  
   Stronger declarative governance rules for admissibility and execution constraints.

4. **Stricter synchronization model**  
   Ledger sync with stronger packet validation and version-aware normalization rules.

5. **Protocol documentation**  
   Stable description of packet schema, execution semantics, replay expectations, and trust assumptions.

---

## Positioning

DSAN-core should be understood as a **verifiable execution architecture**.

Its central claim is not simply:
> “events are stored”

but rather:
> “executed events can be replayed into state, and that state can be independently verified.”