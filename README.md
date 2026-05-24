# DSAN-core
> Also available in Portuguese (Brazil): [README.pt-BR.md](README.pt-BR.md)

**DSAN-core** is the execution and verification kernel of the DSAN Network. It provides governed event execution, ledger persistence, deterministic replay, state-root verification, and local auditability for distributed execution flows.

At its current stage, DSAN-core is not positioned as a production blockchain or Byzantine fault tolerant network. Instead, it is an experimental execution-governance core focused on verifiable action processing, replayable state reconstruction, and audit-oriented ledger design.

## What DSAN-core does

DSAN-core currently supports:

- Signed event creation through DSAN agents.
- Canonical event hashing.
- Policy-based event admission.
- Majority-style peer voting.
- Totem-gated execution authorization.
- Local ledger persistence.
- Merkle root computation over ledger hashes.
- Deterministic replay into derived state.
- `state_root` generation and verification.
- Independent local audit via replay.
- Ledger synchronization with structural validation.

## Current architecture

The current kernel is organized around five logical layers.

## Auditor node

DSAN-core now includes a dedicated **Auditor Node** role, separate from the executor node.

The Auditor Node:
- fetches `/ledger`, `/state`, `/root`, and `/state_root` from a target node,
- validates ledger structure,
- verifies canonical event hashes,
- checks `prev_hash` continuity,
- verifies validator signatures,
- recalculates the Merkle root,
- replays the ledger locally to recompute `state_root`,
- compares local results against the remote node’s published commitments.

This creates a separation between:
- **executor node**, which validates, executes, and persists events,
- **auditor node**, which independently verifies historical integrity and derived state consistency.

At the current validated stage, the Auditor Node has successfully confirmed:
- structural ledger validity,
- Merkle root consistency,
- state root consistency,
- independent replay agreement with the executor node.

### Agent layer

Agents create signed events containing:
- `sender`
- `payload`
- `nonce`
- `prev_hash`

Each event is serialized canonically, signed with Ed25519, and hashed before submission.

### Node layer

A DSAN node:
- receives candidate events,
- verifies sender signature,
- checks replay and chain continuity,
- evaluates policy rules,
- gathers local and peer votes,
- requires Totem authorization,
- executes the action,
- signs the event hash as validator,
- appends the final packet to the ledger.

### Ledger layer

Each persisted packet may contain:
- `event`
- `hash`
- `validators`
- `result`
- `state_root`

The ledger acts as both execution history and replay substrate.

### Replay layer

The replay engine rebuilds state from ledger history by applying all events in sequence. This produces a deterministic `state_root` that can be independently verified.

### Audit layer

An auditor can:
- fetch the ledger,
- recompute the state locally,
- compare the recomputed `state_root` with the node’s published `state_root`,
- verify whether execution history and published state are consistent.

## Execution flow

The current execution flow is:

1. Agent creates a signed event.
2. Node receives the event.
3. Node validates hash, signature, nonce, and chain continuity.
4. Node applies policy checks.
5. Node gathers local and peer votes.
6. Node requests Totem authorization.
7. Node executes the event.
8. Node computes the resulting `state_root`.
9. Node collects validator signatures.
10. Node appends the packet to the ledger.
11. Node exposes ledger, Merkle root, and state root for verification.

## Verified properties

At the current recovered stage, DSAN-core demonstrates:

- **Canonical event hashing**
- **Replayable ledger history**
- **Derived state verification**
- **Per-entry `state_root` normalization**
- **State-root consistency checks**
- **Independent local auditability**

This means a third party can recompute the final state derived from ledger history instead of trusting only the node’s live execution response.

## Repository structure

The repository is currently organized around the DSAN-core execution kernel and its supporting validation tools.

```text
dsan-core/
├── README.md
├── README.pt-BR.md
├── CHANGELOG.md
├── LICENSE
├── RELEASE_CHECKLIST.md
├── KNOWN_ISSUES.md
├── clisend.py
├── cliaudit.py
├── migrate_state_roots.py
├── ledger_node1.json
├── dsan/
├── api/
├── cli/
├── docs/
└── data/
```

Main areas:
- `dsan/` contains the core execution, replay, audit, network, policy, and Totem logic.
- `clisend.py` and `cliaudit.py` provide local helper flows for submission and audit.
- `migrate_state_roots.py` is used to normalize historical ledger entries.
- `ledger_node1.json` is the main local ledger used in validation and replay checks.
- `docs/`, `api/`, `cli/`, and `data/` are support directories for documentation, interface support, command-line utilities, and local data artifacts.

## Quick start

### 1. Start a local node

```bash
python -m dsan.network.node node1 5001
```

This starts a local DSAN node on `127.0.0.1:5001`.

### 2. Check basic endpoints

```bash
curl http://127.0.0.1:5001/state
curl http://127.0.0.1:5001/root
curl http://127.0.0.1:5001/state_root
curl http://127.0.0.1:5001/ledger
```

### 3. Submit an event

Example `clisend.py`:

```python
import requests
from dsan.agent.agent import DSANAgent

NODE_URL = "http://127.0.0.1:5001"

agent = DSANAgent("alice")

state = requests.get(f"{NODE_URL}/state").json()
prev_hash = state["last_hash"]

packet = agent.create_event(
    {
        "type": "transfer",
        "from": "alice",
        "to": "bob",
        "amount": 10
    },
    prev_hash
)

response = requests.post(f"{NODE_URL}/receive", json=packet)

print("status:", response.status_code)
print("body:", response.json())
```

Run:

```bash
python clisend.py
```

### 4. Audit the node independently

Example `cliaudit.py`:

```python
import requests
from dsan.core.replay import replay_ledger

NODE_URL = "http://127.0.0.1:5001"

ledger = requests.get(f"{NODE_URL}/ledger").json()
root_info = requests.get(f"{NODE_URL}/root").json()
state_info = requests.get(f"{NODE_URL}/state_root").json()
state_meta = requests.get(f"{NODE_URL}/state").json()

replayed_state_root = replay_ledger(ledger)
node_state_root = state_info["state_root"]

print("=== DSAN AUDIT REPORT ===")
print("ledger_size:", state_meta["ledger_size"])
print("last_hash:", state_meta["last_hash"])
print("merkle_root:", root_info["root"])
print("node_state_root:", node_state_root)
print("replayed_state_root:", replayed_state_root)

if ledger:
    last_entry = ledger[-1]
    packet_state_root = last_entry.get("state_root")
    print("packet_state_root:", packet_state_root)

    if packet_state_root is None:
        print("packet_state_root_check: MISSING")
    elif packet_state_root == replayed_state_root:
        print("packet_state_root_check: OK")
    else:
        print("packet_state_root_check: MISMATCH")
else:
    print("packet_state_root: EMPTY_LEDGER")

if node_state_root == replayed_state_root:
    print("audit_result: CONSISTENT")
else:
    print("audit_result: MISMATCH")
```

Run:

```bash
python cliaudit.py
```

### 5. Run the Auditor Node

Start the auditor service:

```bash
python -m dsan.auditor.node
```

In another terminal, audit a running executor node:

```bash
curl "http://127.0.0.1:5010/audit?target=http://127.0.0.1:5001"
```

A successful response should include:

- `structure_valid: true`
- `merkle_root_match: true`
- `state_root_match: true`
- `audit_result: CONSISTENT`

This confirms that the remote node’s ledger, Merkle root, and derived state are independently verifiable.

### 6. Manual end-to-end test with Totem

This flow validates event submission, Totem-gated execution, ledger persistence, and independent auditor verification.

#### Start the executor node

```bash
python -m dsan.network.node node1 5001
```

#### Start the auditor node

```bash
python -m dsan.auditor.node
```

#### Generate a signed event

Create `send_event.py`:

```python
import json
import time
import hashlib
import requests
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def hash_event(event):
    return hashlib.sha256(canonical_json(event).encode()).hexdigest()

state = requests.get("http://127.0.0.1:5001/state", timeout=2).json()
prev_hash = state["last_hash"]

event = {
    "nonce": str(int(time.time() * 1000)),
    "payload": {"msg": "transfer_funds"},
    "prev_hash": prev_hash,
    "sender": "alice"
}

sender_sk = ed25519.Ed25519PrivateKey.generate()
sender_pk = sender_sk.public_key()

packet = {
    "event": event,
    "hash": hash_event(event),
    "signature": sender_sk.sign(canonical_json(event).encode()).hex(),
    "sender_sig_pub": sender_pk.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    ).hex()
}

with open("event.json", "w", encoding="utf-8") as f:
    json.dump(packet, f, ensure_ascii=False, indent=2)

print("event.json generated")
print("prev_hash =", prev_hash)
print("new_hash =", packet["hash"])
print("nonce =", packet["event"]["nonce"])
```

Run:

```bash
python send_event.py
cat event.json
```

#### Submit the event

```bash
curl -X POST http://127.0.0.1:5001/receive -H "Content-Type: application/json" -d @event.json
```

#### Authorize on the Totem

When the executor node terminal shows:

```bash
🔐 Totem gesture (ex: 120):
```

enter:

```bash
120
```

#### Validate node state and audit result

```bash
curl http://127.0.0.1:5001/state
curl http://127.0.0.1:5001/ledger
curl "http://127.0.0.1:5010/audit?target=http://127.0.0.1:5001"
```

Expected result:
- `ledger_size` increases by 1,
- `last_hash` changes,
- the new packet appears in `/ledger`,
- the auditor returns `audit_result: CONSISTENT`.

> Note: the correct ingestion endpoint is `/receive`. The POST request only completes after the correct Totem gesture is entered in the executor node terminal. Re-submitting the same `event.json` may return `{"status":"duplicate"}`.

### 7. Normalize old ledger entries

If older ledger entries do not yet contain `state_root`, use `migrate_state_roots.py` to normalize historical packets.

Run:

```bash
python migrate_state_roots.py ledger_node1.json
```

This recalculates progressive `state_root` values and updates legacy entries.

## Current status

This repository reflects a **recovered and stabilized execution kernel** evolved beyond the original simulator stage.

Validated properties in the recovered branch include:

- node startup and endpoint availability,
- persisted ledger loading,
- event submission and execution,
- deterministic replay,
- `state_root` consistency,
- historical ledger normalization,
- successful local audit with `CONSISTENT` result,
- dedicated Auditor Node startup,
- remote independent audit,
- validator-signature verification in the auditor,
- Merkle root recomputation and comparison,
- successful auditor result with `CONSISTENT`.

## Limitations

DSAN-core remains experimental and has important limitations:

- no Byzantine fault tolerant consensus,
- no asynchronous consensus engine,
- no persistent validator identity governance,
- no finalized membership model,
- Totem authorization is interactive and currently terminal-bound,
- policy semantics are still evolving,
- audit is local and developer-oriented, not yet a standalone production verifier.

## Development direction

The most logical next steps are:

- dedicated auditor-node mode,
- persistent validator identity model,
- stricter sync validation across normalized ledger history,
- formal EPL / JSON policy definitions,
- clearer execution/state separation,
- protocol-level documentation,
- integration path into broader DSAN Network services.

## Positioning

DSAN-core should be understood as a **verifiable execution kernel**, not merely a blockchain prototype.

Its central purpose is to make governed execution:
- replayable,
- state-derivable,
- externally auditable,
- structurally verifiable.

## Disclaimer

This project is under active architectural evolution. Interfaces, packet structure, and verification logic may change as the core stabilizes.

