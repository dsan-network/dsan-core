# DSAN-core Protocol

## Scope

This document describes the currently implemented protocol behavior of `dsan-core` at the recovered execution-kernel stage.

It documents:

* packet structures;
* event representation;
* cryptographic signatures;
* node endpoints;
* validation rules;
* authorization behavior;
* ledger semantics;
* replay semantics;
* Merkle-root verification;
* state-root verification;
* synchronization behavior;
* independent audit behavior.

It does **not** describe a finalized DSAN network standard, universal consensus protocol, or production security protocol.

The protocol documented here is an **implementation-level protocol of `dsan-core`**.

The broader architectural definition of DSAN is maintained separately by the DSAN-Ecosystem specifications.

---

# Core Principle

The `dsan-core` protocol is built around the following rule:

> **A recorded execution must be replayable into a verifiable derived state.**

A node therefore does not merely store execution history.

It also exposes sufficient structure for an independent verifier to:

1. validate the recorded history;
2. verify cryptographic evidence;
3. replay the history;
4. reconstruct the resulting state;
5. calculate the corresponding state root;
6. compare the result with published commitments.

---

# 1. Data Model

## 1.1 Event

An Event is the canonical action payload created by an Agent.

### Event fields

```json
{
  "sender": "alice",
  "payload": {
    "type": "transfer",
    "from": "alice",
    "to": "bob",
    "amount": 10
  },
  "nonce": "1777403064009",
  "prev_hash": "03a0b3ee8285e7ed54acd453500037761c50af596d27814755024e3e34032d7d"
}
```

### Field meanings

* `sender`: logical sender identifier.
* `payload`: action body interpreted by execution and state logic.
* `nonce`: replay-protection value.
* `prev_hash`: expected hash of the previous ledger entry.

### Event hashing

Events are serialized using canonical JSON rules:

* keys sorted;
* compact separators;
* deterministic byte representation.

The event hash is:

```text
sha256(canonical_json(event))
```

The canonical representation is part of the verification process and must remain deterministic for equivalent protocol versions.

---

# 2. Submission Packet

A Submission Packet is the structure sent by an Agent to a Node.

### Submission packet fields

```json
{
  "event": {
    "sender": "alice",
    "payload": {
      "type": "transfer",
      "from": "alice",
      "to": "bob",
      "amount": 10
    },
    "nonce": "1777403064009",
    "prev_hash": "03a0b3ee8285e7ed54acd453500037761c50af596d27814755024e3e34032d7d"
  },
  "hash": "52072be32edc0d1589941c49216312dcee9fda0ba07844c18e4a551e3f661cc9",
  "signature": "...",
  "sender_sig_pub": "..."
}
```

### Field meanings

* `event`: canonical event body.
* `hash`: SHA-256 hash of canonical event JSON.
* `signature`: sender signature over canonical event bytes.
* `sender_sig_pub`: sender public key used for signature verification.

The Submission Packet provides the cryptographic evidence required for the receiving Node to validate attribution and integrity before further processing.

---

# 3. Ledger Packet

A Ledger Packet is the persisted execution record stored by the Node.

### Ledger packet fields

```json
{
  "event": {},
  "hash": "...",
  "validators": [
    {
      "node": "node1",
      "pub": "...",
      "sig": "..."
    }
  ],
  "result": "[EXECUTED] ...",
  "state_root": "..."
}
```

### Field meanings

* `event`: original event body.
* `hash`: canonical event hash.
* `validators`: validator signatures over the event hash.
* `result`: execution result or output summary.
* `state_root`: derived state commitment after replay through this entry.

The Ledger Packet is an **evidence-bearing execution record**.

It does not itself constitute sovereign authority.

---

# 4. Cryptographic Behavior

## 4.1 Sender Signature

The sender signs the canonical event bytes using Ed25519.

### Verified object

```text
canonical_json(event).encode()
```

### Verification inputs

* public key: `sender_sig_pub`;
* signature: `signature`.

If verification fails, the event is rejected.

---

## 4.2 Validator Signature

A validator signs the event hash after the applicable approval and execution flow.

### Verified object

```text
entry["hash"].encode()
```

Each validator record contains:

* `node`;
* `pub`;
* `sig`.

If a required validator signature fails verification during synchronization validation, the packet may be rejected.

---

## 4.3 Auditor-Side Validator Verification

The Auditor Node verifies validator signatures against the event hash recorded in each Ledger Packet.

### Verified object

```text
entry["hash"].encode()
```

### Verification inputs

* validator public key: `validators[i]["pub"]`;
* validator signature: `validators[i]["sig"]`.

If validator signatures fail verification, the ledger is treated as invalid for audit purposes.

---

# 5. Node Validation Rules

When a Node receives a Submission Packet for execution, the current implementation applies the following checks.

## 5.1 Replay Check

The Node rejects events whose `nonce` has already been seen.

### Failure reason

```json
{
  "vote": "NO",
  "reason": "replay"
}
```

---

## 5.2 Sender Signature Check

The Node verifies the sender signature over the canonical event bytes.

### Failure effect

The event is rejected.

---

## 5.3 Hash Integrity Check

The Node recomputes the event hash from canonical JSON and compares it with `data["hash"]`.

### Failure reason

```json
{
  "vote": "NO",
  "reason": "tamper"
}
```

---

## 5.4 Chain Continuity Check

The Node checks:

```text
event["prev_hash"] == last_hash()
```

### Failure reason

```json
{
  "vote": "NO",
  "reason": "chain_mismatch"
}
```

---

## 5.5 Policy Check

The Node evaluates the event through the applicable policy layer.

### Failure reason

```json
{
  "vote": "NO",
  "reason": "policy_block"
}
```

---

## 5.6 Vote Aggregation

The current implementation uses a majority-style approval flow involving:

* self vote;
* peer vote requests;
* approval when votes exceed half of the configured participants.

This mechanism is a lightweight coordination mechanism.

It is **not a Byzantine fault-tolerant consensus protocol**.

### Failure reason

```json
{
  "status": "consensus_failed"
}
```

The current mechanism should therefore be understood as an implementation-stage validation mechanism rather than a finalized DSAN consensus standard.

---

# 6. Authorization

Authorization is evaluated after the applicable validation stages.

The protocol intentionally distinguishes:

```text
Authority
    ≠
Authorization
    ≠
Execution
```

A valid cryptographic signature does not automatically mean that the corresponding action is authorized.

Authorization may depend on the applicable:

* policy;
* context;
* state;
* delegation;
* trust conditions;
* physical authorization;
* temporal validity;
* other execution constraints.

---

# 7. Totem Authorization

The current implementation includes a Totem authorization gate after local validation and vote approval.

### Current implementation behavior

```text
Validation
    ↓
Vote Approval
    ↓
Totem Authorization
    ↓
Execution
```

### Failure reason

```json
{
  "status": "totem_denied"
}
```

The Totem gate is an implementation-level authorization mechanism.

It must not be interpreted as a universal requirement of the DSAN architecture.

The architectural model permits physical authorization to be required only when applicable to the operation, policy, context, or deployment.

Therefore:

```text
Totem
    ≠
Sovereignty
```

and:

```text
Physical Authorization
    ≠
Sovereign Authority
```

The current Core implementation demonstrates one concrete physical-authorization mechanism.

---

# 8. Execution Semantics

If an event passes the applicable validation and authorization conditions, the current implementation:

1. executes the action;
2. constructs an execution result;
3. computes a progressive `state_root`;
4. collects validator signatures;
5. appends the Ledger Packet;
6. persists ledger state;
7. may broadcast synchronization information to peers.

The exact execution behavior depends on the state model and implementation currently deployed.

Execution therefore represents the transition from an authorized request to an actual system operation.

---

# 9. Replay Semantics

Replay is deterministic and sequential.

## Replay rule

For each Ledger Packet in order:

1. extract `entry["event"]`;
2. apply the event to the state model;
3. continue through the ledger;
4. serialize the resulting state;
5. calculate the state root.

### Replay result

```text
state_root = sha256(serialized_state)
```

The resulting state root is the **cryptographic commitment to the replay-derived state** for the current protocol implementation.

It is not, by itself, a claim about sovereign authority or legitimacy.

---

# 10. Roots

## 10.1 Merkle Root

The Merkle root is computed from the list of Ledger Packet hashes.

### Input

```text
[entry["hash"] for entry in ledger]
```

### Purpose

* compact commitment over recorded ledger hashes;
* integrity summary of event history.

### Endpoint

```text
GET /root
```

### Example response

```json
{
  "root": "...",
  "size": 3
}
```

---

## 10.2 State Root

The `state_root` is computed from replay of the ledger history.

### Purpose

* commitment to the derived execution state;
* independent verification target for auditors;
* consistency check between recorded history and published state.

### Endpoint

```text
GET /state_root
```

### Example response

```json
{
  "state_root": "..."
}
```

---

## 10.3 Auditor Commitment Checks

The Auditor Node currently verifies both commitment classes exposed by the Executor Node:

### Merkle root check

The Auditor recalculates the ledger root from entry hashes and compares it with:

```text
GET /root
```

### State root check

The Auditor replays the ledger and compares the derived result with:

```text
GET /state_root
```

and with the `state_root` contained in the last Ledger Packet.

A Node should be considered consistent only when the applicable structural, cryptographic, Merkle, and state-root checks succeed.

---

# 11. Endpoints

## 11.1 `GET /`

Returns basic Node liveness.

### Example

```json
{
  "status": "node1 online"
}
```

---

## 11.2 `GET /state`

Returns ledger size and last hash.

### Example

```json
{
  "ledger_size": 3,
  "last_hash": "52072be32edc0d1589941c49216312dcee9fda0ba07844c18e4a551e3f661cc9"
}
```

---

## 11.3 `GET /root`

Returns the Merkle root and ledger size.

---

## 11.4 `GET /state_root`

Returns the replay-derived final state root.

---

## 11.5 `GET /ledger`

Returns the full ledger JSON currently loaded by the Node.

---

## 11.6 `POST /vote`

Used by Nodes to evaluate whether an event should receive approval.

### Expected input

Submission Packet.

### Example success

```json
{
  "vote": "YES"
}
```

### Example failure

```json
{
  "vote": "NO",
  "reason": "tamper"
}
```

---

## 11.7 `POST /receive`

Primary execution endpoint.

### Expected input

Submission Packet.

### Success response

```json
{
  "status": "executed",
  "hash": "...",
  "state_root": "..."
}
```

### Possible failure responses

```json
{
  "status": "duplicate"
}
```

```json
{
  "status": "rejected_local"
}
```

```json
{
  "status": "consensus_failed"
}
```

```json
{
  "status": "totem_denied"
}
```

```json
{
  "status": "error",
  "error": "..."
}
```

---

## 11.8 `POST /sign`

Returns a validator signature over a provided hash.

### Expected input

```json
{
  "hash": "..."
}
```

### Response

```json
{
  "node": "node1",
  "pub": "...",
  "sig": "..."
}
```

---

## 11.9 `POST /sync`

Receives a remote ledger and validates it structurally and cryptographically according to the current implementation.

### Current synchronization checks

* incoming ledger is non-empty;
* incoming root differs from local root when synchronization is required;
* validator signatures are valid;
* event hashes are correct;
* `prev_hash` continuity is valid;
* required `state_root` values are present;
* replay-derived final state root matches the last packet `state_root`;
* the applicable longer-ledger replacement rule is satisfied.

### Possible failure responses

```json
{
  "status": "empty"
}
```

```json
{
  "status": "already_synced"
}
```

```json
{
  "status": "invalid_validators"
}
```

```json
{
  "status": "invalid_hash"
}
```

```json
{
  "status": "fork_detected"
}
```

```json
{
  "status": "missing_state_root"
}
```

```json
{
  "status": "invalid_state"
}
```

```json
{
  "status": "error",
  "error": "..."
}
```

Synchronization is an implementation-level protocol behavior.

It should not be interpreted as a finalized distributed-consensus specification.

---

# 12. Auditor Endpoint

The Auditor Node exposes an endpoint for remote verification.

## `GET /audit?target=<node_url>`

The Auditor retrieves the target Node's ledger and verification endpoints and performs independent validation.

### Current checks

* ledger structure validation;
* canonical event hash validation;
* `prev_hash` continuity validation;
* validator signature verification;
* Merkle root recomputation and comparison;
* replay-derived state-root recomputation;
* comparison between remote and locally reconstructed commitments.

### Example response

```json
{
  "target": "http://127.0.0.1:5001",
  "ledger_size": 3,
  "last_hash": "...",
  "remote_merkle_root": "...",
  "recalculated_merkle_root": "...",
  "merkle_root_match": true,
  "remote_state_root": "...",
  "replayed_state_root": "...",
  "packet_state_root": "...",
  "state_root_match": true,
  "structure_valid": true,
  "structure_reason": "ok",
  "audit_result": "CONSISTENT"
}
```

The `CONSISTENT` result means that the currently implemented verification checks agree.

It does not constitute a universal security certification of the target system.

---

# 13. Historical Normalization

Earlier recovered Ledger Packets may exist without `state_root`.

A normalization step can recompute and attach progressive `state_root` values to legacy entries.

This improves:

* ledger consistency;
* synchronization compatibility;
* audit traceability;
* per-entry verification readiness.

Historical normalization is a **migration behavior**, not a separate authorization or consensus mechanism.

---

# 14. Trust Assumptions

The current protocol stage assumes:

* deterministic replay implementation;
* honest local test/development execution;
* valid cryptographic libraries;
* non-Byzantine peer behavior;
* controlled environment operation.

These assumptions are acceptable for the current experimental kernel stage.

They are insufficient to establish production-grade security under unrestricted adversarial conditions.

---

# 15. Security Interpretation

The protocol provides cryptographic and structural evidence.

It does not automatically establish:

* legal authority;
* sovereign authority;
* correctness of an external policy;
* correctness of human intent;
* legitimacy of an organization;
* security against all possible attacks.

The following distinction is therefore fundamental:

```text
Cryptographic Validity
        ≠
Authorization
        ≠
Legitimacy
        ≠
Sovereignty
```

The protocol should be evaluated according to the exact threat model, deployment assumptions, cryptographic primitives, implementation correctness, and governance model in use.

---

# 16. Architectural Relationship

The `dsan-core` protocol is an implementation-level protocol within the larger DSAN architecture.

Conceptually:

```text
DSAN Architecture
        │
        ▼
Sovereign Entity
        │
        ▼
Guardian
        │
        ▼
GuardianOS / applicable authorization mechanisms
        │
        ▼
DSAN Core
        │
 ┌──────┼─────────────────┐
 ▼      ▼                 ▼
Events Authorization     State
        │                 │
        ▼                 ▼
     Execution ───────► Ledger
                           │
                           ▼
                         Replay
                           │
                           ▼
                       State Root
                           │
                           ▼
                    Independent Audit
```

The Core therefore provides computational mechanisms for execution, evidence and verification.

It does not define the complete DSAN ontology.

---

# 17. Protocol Boundaries

The following distinctions are intentionally preserved:

```text
Sovereign Entity ≠ Guardian
Guardian ≠ GuardianOS
GuardianOS ≠ Totem

Identity ≠ Presence
Presence ≠ Intent
Intent ≠ Authority
Authority ≠ Authorization
Authorization ≠ Execution
Execution ≠ Evidence
Evidence ≠ Authority
```

The protocol may represent evidence associated with these concepts without collapsing them into one another.

---

# 18. Offline and Revocation Considerations

The current protocol supports local operation and synchronization.

However:

```text
Offline Operation
        ≠
Unrestricted Authority
```

A future protocol version must explicitly address:

* authorization expiration;
* delegation expiration;
* revocation;
* synchronization after revocation;
* stale state;
* recovery;
* conflicting histories.

Reconnection must not automatically restore authority that has expired or been revoked.

These behaviors are part of the protocol evolution roadmap and are not yet fully specified by the current implementation.

---

# 19. Non-Goals at Current Stage

The current protocol does **not** yet provide:

* Byzantine fault-tolerant consensus;
* finalized validator governance;
* stable network-membership semantics;
* production-grade proof packaging;
* a finalized EPL standard;
* production-ready secure peer transport;
* universal physical-authorization requirements;
* a finalized cross-deployment authorization protocol.

These limitations describe the current implementation stage.

They are not architectural impossibilities.

---

# 20. Protocol Status

This protocol description reflects a **recovered and validated implementation stage**.

The following behaviors have been demonstrated locally:

* Node startup;
* event submission;
* ledger growth;
* per-entry `state_root`;
* deterministic replay;
* consistent local audit;
* normalized historical ledger entries;
* dedicated Auditor Node startup;
* validator-signature verification by a separate verifier;
* Merkle-root verification by a separate verifier;
* remote consistency reporting with `CONSISTENT`.

These observations describe implementation behavior under the tested conditions.

They should not be interpreted as a universal security guarantee or production-readiness certification.

---

# 21. Future Protocol Evolution

Future protocol versions may introduce:

* explicit protocol-version identifiers;
* versioned event schemas;
* stronger authorization artifacts;
* contextual authorization classes;
* explicit delegation semantics;
* expiration and revocation semantics;
* recovery protocols;
* stronger synchronization rules;
* validator identity persistence;
* formalized network membership;
* improved transport security;
* stronger evidence packaging;
* interoperability mechanisms;
* formal protocol testing.

Future extensions should preserve the architectural separation between:

```text
Identity
Presence
Intent
Authority
Authorization
Execution
State
Evidence
Governance
```

---

# 22. Final Principle

The `dsan-core` protocol exists to make execution history **recordable, replayable and independently verifiable**.

Its central proposition is:

```text
Recorded History
       ↓
Deterministic Replay
       ↓
Derived State
       ↓
Cryptographic Commitment
       ↓
Independent Verification
```

The protocol therefore provides a computational foundation for governed execution.

It does not make the protocol itself sovereign.

It provides mechanisms through which execution and its resulting state can be represented and verified within the broader DSAN architecture.

**DSAN — Sovereignty by Architecture.**
