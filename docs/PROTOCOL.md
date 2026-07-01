# DSAN-core Protocol

## Scope

This document describes the currently implemented protocol behavior of DSAN-core at the recovered execution-kernel stage.

It does **not** describe a finalized network standard or production consensus protocol.  
It documents the packet shapes, node endpoints, validation rules, and replay semantics that are already reflected in the current implementation.

---

## Core principle

The DSAN-core protocol is built around this rule:

> a recorded execution must be replayable into a verifiable derived state

This means that a node does not only store execution history.  
It also exposes enough structure for an independent verifier to recompute the resulting state from ledger history.

---

## Data model

## 1. Event

An event is the canonical action payload created by an agent.

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

- `sender`: logical sender identifier.
- `payload`: action body to be interpreted by execution/state logic.
- `nonce`: replay-protection value.
- `prev_hash`: expected hash of the previous ledger entry.

### Event hashing

Events are serialized using canonical JSON rules:
- keys sorted,
- compact separators,
- deterministic byte representation.

The event hash is:

```text
sha256(canonical_json(event))
```

---

## 2. Submission packet

A submission packet is the structure sent by an agent to a node.

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

- `event`: canonical event body.
- `hash`: SHA-256 hash of canonical event JSON.
- `signature`: sender signature over canonical event bytes.
- `sender_sig_pub`: sender public key used for signature verification.

---

## 3. Ledger packet

A ledger packet is the persisted execution record stored by the node.

### Ledger packet fields

```json
{
  "event": {...},
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

- `event`: original event body.
- `hash`: canonical event hash.
- `validators`: validator signatures over the event hash.
- `result`: execution result string or output summary.
- `state_root`: derived state hash after replay up to this entry.

---

## Cryptographic behavior

## 1. Sender signature

The sender signs the canonical event bytes using Ed25519.

### Verified object
```text
canonical_json(event).encode()
```

### Verification input
- public key: `sender_sig_pub`
- signature: `signature`

If verification fails, the event must be rejected.

---

## 2. Validator signature

A validator signs the event hash after approval/execution flow.

### Verified object
```text
entry["hash"].encode()
```

Each validator record contains:
- `node`
- `pub`
- `sig`

If any required validator signature verification fails during sync validation, the packet may be rejected.

## 3. Auditor-side validator verification

The Auditor Node verifies validator signatures against the event hash recorded in each ledger packet.

### Verified object
```text
entry["hash"].encode()
```

### Verification inputs
- validator public key: `validators[i]["pub"]`
- validator signature: `validators[i]["sig"]`

If validator signatures fail verification, the ledger must be treated as invalid for audit purposes.
---

## Node validation rules

When a node receives a submission packet for execution, the following checks apply.

## 1. Replay check

The node rejects events whose `nonce` has already been seen.

### Failure reason
```json
{"vote": "NO", "reason": "replay"}
```

---

## 2. Sender signature check

The node verifies the sender signature over canonical event bytes.

### Failure effect
The event is rejected.

---

## 3. Hash integrity check

The node recomputes the event hash from canonical JSON and compares it to `data["hash"]`.

### Failure reason
```json
{"vote": "NO", "reason": "tamper"}
```

---

## 4. Chain continuity check

The node checks:

```text
event["prev_hash"] == last_hash()
```

### Failure reason
```json
{"vote": "NO", "reason": "chain_mismatch"}
```

---

## 5. Policy check

The node evaluates the event through the policy layer.

### Failure reason
```json
{"vote": "NO", "reason": "policy_block"}
```

---

## 6. Vote aggregation

The current implementation uses a majority-style approval flow:
- self vote,
- peer vote requests,
- approval if votes exceed half of total participants.

This is a lightweight coordination mechanism, not a Byzantine fault tolerant protocol.

### Failure reason
```json
{"status": "consensus_failed"}
```

---

## 7. Totem authorization

After local validation and vote approval, execution still depends on Totem authorization.

### Failure reason
```json
{"status": "totem_denied"}
```

---

## Execution semantics

If an event passes validation and authorization:

1. the node executes the action,
2. constructs a result,
3. computes a progressive `state_root`,
4. collects validator signatures,
5. appends the ledger packet,
6. persists ledger state,
7. may broadcast sync to peers.

---

## Replay semantics

Replay is deterministic and sequential.

### Replay rule

For each ledger entry in order:

1. extract `entry["event"]`,
2. apply the event to the state model,
3. continue until the end of the ledger,
4. hash the final serialized state.

### Replay output

```text
state_root = sha256(serialized_state)
```

This derived `state_root` is the authoritative replay result for verification purposes.

---

## Roots

## 1. Merkle root

The Merkle root is computed from the list of ledger entry hashes.

### Input
```text
[entry["hash"] for entry in ledger]
```

### Purpose
- compact commitment over recorded ledger hashes,
- integrity summary of the event history.

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

## 2. State root

The `state_root` is computed from replay of the ledger history.

### Purpose
- commitment to the derived execution state,
- independent verification target for auditors,
- consistency check between history and published state.

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
## 3. Auditor commitment checks

The Auditor Node currently verifies both commitment classes exposed by the executor node:

- **Merkle root check**: recalculates the ledger root from entry hashes and compares it with `GET /root`.
- **State root check**: replays the ledger and compares the derived result with `GET /state_root` and the last packet `state_root`.

A node should only be considered consistent when both checks succeed.
---

## Endpoints

## 1. `GET /`

Returns basic node liveness.

### Example
```json
{
  "status": "node1 online"
}
```

---

## 2. `GET /state`

Returns ledger size and last hash.

### Example
```json
{
  "ledger_size": 3,
  "last_hash": "52072be32edc0d1589941c49216312dcee9fda0ba07844c18e4a551e3f661cc9"
}
```

---

## 3. `GET /root`

Returns the Merkle root and ledger size.

---

## 4. `GET /state_root`

Returns the replay-derived final state root.

---

## 5. `GET /ledger`

Returns the full ledger JSON currently loaded by the node.

---

## 6. `POST /vote`

Used by nodes to evaluate whether an event should receive approval.

### Expected input
Submission packet.

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

## 7. `POST /receive`

Primary execution endpoint.

### Expected input
Submission packet.

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
{"status": "duplicate"}
{"status": "rejected_local"}
{"status": "consensus_failed"}
{"status": "totem_denied"}
{"status": "error", "error": "..."}
```

---

## 8. `POST /sign`

Returns validator signature over a provided hash.

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

## 9. `POST /sync`

Receives a remote ledger and validates it structurally.

### Current sync checks
- non-empty incoming ledger,
- different root from local root,
- validator signature validity,
- hash correctness for each event,
- `prev_hash` continuity,
- presence of `state_root`,
- replay-derived final state root matches last packet `state_root`,
- longer-ledger replacement rule.

### Possible failure responses
```json
{"status": "empty"}
{"status": "already_synced"}
{"status": "invalid_validators"}
{"status": "invalid_hash"}
{"status": "fork_detected"}
{"status": "missing_state_root"}
{"status": "invalid_state"}
{"status": "error", "error": "..."}
```

## 10. Auditor endpoint

The Auditor Node exposes an audit endpoint for remote verification.

### `GET /audit?target=<node_url>`

Fetches a remote node’s ledger and verification endpoints, then performs independent validation.

### Current checks
- ledger structure validation,
- canonical event hash validation,
- `prev_hash` continuity validation,
- validator signature verification,
- Merkle root recomputation and comparison,
- replay-derived `state_root` recomputation,
- comparison between remote and local commitments.

### Example response
```json
{
  "target": "http://127.0.0.1:5001",
  "ledger_size": 3,
  "last_hash": "52072be32edc0d1589941c49216312dcee9fda0ba07844c18e4a551e3f661cc9",
  "remote_merkle_root": "fd05228b3eb0761d93174a8a0db1cbd3ff44c12c9b2147bad720492718ad9e2b",
  "recalculated_merkle_root": "fd05228b3eb0761d93174a8a0db1cbd3ff44c12c9b2147bad720492718ad9e2b",
  "merkle_root_match": true,
  "remote_state_root": "4bfb09ae336929da8ebe73916ac06db871b81e7fea3a6b7f0537186538cffbad",
  "replayed_state_root": "4bfb09ae336929da8ebe73916ac06db871b81e7fea3a6b7f0537186538cffbad",
  "packet_state_root": "4bfb09ae336929da8ebe73916ac06db871b81e7fea3a6b7f0537186538cffbad",
  "state_root_match": true,
  "structure_valid": true,
  "structure_reason": "ok",
  "audit_result": "CONSISTENT"
}
```

## Historical normalization

Earlier recovered ledger entries may exist without `state_root`.

A normalization step can recompute and attach progressive `state_root` values to legacy entries.  
This improves:
- ledger consistency,
- sync compatibility,
- audit traceability,
- per-entry verification readiness.

This is a migration behavior, not a separate protocol feature.

---

## Trust assumptions

The current protocol stage assumes:

- deterministic replay implementation,
- honest local test/development execution,
- valid cryptographic libraries,
- non-Byzantine peer behavior,
- controlled environment operation.

These assumptions are acceptable for the current experimental kernel stage, but insufficient for production adversarial environments.

---

## Non-goals at current stage

The current protocol does **not** yet provide:
- BFT consensus,
- finalized validator governance,
- stable network membership semantics,
- production-grade proof packaging,
- finalized EPL standard,
- production-ready secure peer transport.

---

## Protocol status

This protocol description reflects a **recovered and validated implementation stage** in which the following behaviors have already been demonstrated locally:

- node startup,
- event submission,
- ledger growth,
- per-entry `state_root`,
- deterministic replay,
- consistent local audit,
- normalized historical ledger entries.
- dedicated Auditor Node startup,
- validator-signature verification by a separate verifier,
- Merkle root verification by a separate verifier,
- remote consistency report with `CONSISTENT`.