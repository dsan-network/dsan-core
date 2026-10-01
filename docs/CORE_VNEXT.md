# DSAN Core-vNext — Interoperability Boundary

**Status:** experimental Reference Profile migration layer  
**Current scope:** accountable event integrity + accountable-history commitments + Execution Ledger canonical records  
**Legacy kernel impact:** none

`dsan/core_vnext/` is an intentionally isolated namespace used to converge the current `dsan-app` governed-execution Reference Runtime with a future DSAN Core implementation.

It does not reinterpret or replace the current v1 execution kernel, Totem gate, replay engine, vote/coordinator logic, API endpoints, or legacy Ledger Packet.

---

## 1. Why Core-vNext exists

The current DSAN execution specifications require stronger semantic separation than the historical v1 packet model.

In particular:

```text
Event ID != Ledger Record ID
```

and the governed runtime now distinguishes:

```text
DSE
Agent
EAF
Executor
Intent
Request
Policy
Decision
Guardian Authorization
Release
Execution
Evidence
Reconciliation
Event
Ledger Record
```

Correlation between these objects does not merge their identities.

Core-vNext provides a clean migration target without silently changing v1 semantics.

---

## 2. Implemented primitives

### Canonical JSON / hashing

Core-vNext exposes deterministic UTF-8 JSON serialization with sorted keys, compact separators and no NaN values, plus SHA-256 commitments.

### Ed25519 event verification

`event_crypto.py` verifies an explicitly bound Ed25519 public key against the canonical DSAN event signing view.

This proves cryptographic attribution/integrity under the supplied binding. It does not create Authority, Capability, Policy permission, Execution Decision, Release or execution permission.

### Accountable-history verification

`accountable_history.py` verifies the deterministic commitment shape used by the current App `UnifiedEvidenceJournal`:

```text
previous_event
previous_root
event
result
result_root
entry_root
```

This is an interoperability bridge. It is not a declaration that the App journal serialization is the final normative DSAN Execution Ledger format.

### Execution Ledger Record construction/verification

`execution_ledger.py` provides:

- deterministic `ledger:*` Record IDs;
- Record ID distinct from Event ID;
- independent Ledger Genesis Root;
- canonical `record_root` construction;
- `previous_record_id` / `previous_record_root` chaining;
- deterministic Ledger State derivation;
- tamper detection;
- pure read-only verification.

---

## 3. Cross-repository fixtures

Two fixtures are currently shared exactly between `dsan-app` and `dsan-core`.

### Structural fixture

```text
fixtures/core_vnext/execution_ledger_v1.json
```

Purpose:

- canonical Record ID;
- ordering;
- chaining;
- semantic references;
- deterministic Ledger Root;
- serialization drift detection.

Expected final Ledger Root:

```text
6afa3c1432aa1c837e1cd6e8fa099d42c52ccacbe5a2518991cdf95087016d10
```

### Signed fixture

```text
fixtures/core_vnext/signed_event_ledger_v1.json
```

Purpose:

```text
Ed25519 Event signature
        ↓
accountable-history result/entry commitment
        ↓
Execution Ledger Record commitment
```

Expected Ledger Root:

```text
efa39fe86718134170cbf913928a1f8e69a7ff71025e040004392971d57eec50
```

The signing key in this fixture is deterministic test material and confers no real-world authority.

---

## 4. Migration stages

Current progress:

```text
Stage A — fixture contract in dsan-app                 DONE
Stage B — independent parser/verifier in dsan-core    DONE
Stage C — byte-identical cross-repo fixture parity    DONE
Stage D — Core-vNext ledger/event primitives          IN PROGRESS / SUBSTANTIAL
Stage E — dsan-app consumes Core-vNext API             NOT STARTED
Stage F — duplicate App implementations removed        NOT STARTED
```

Stage E must not start by deleting working App logic.

The safe order is:

1. prove semantic parity;
2. provide a stable Core-vNext API/package boundary;
3. make the App consume that boundary behind tests;
4. compare roots/results across both implementations;
5. remove duplicate implementations only after parity is demonstrated.

---

## 5. What Core-vNext does not yet claim

Core-vNext does not yet provide a complete DSAN-SPEC-0010 conformant Execution Ledger.

Open areas include:

- full event-class catalog;
- richer indirect correlation;
- receipt/synchronization-time semantics;
- generic conflict records and resolution;
- first-class distributed Ledger Record exchange;
- ledger retention lifecycle;
- Ledger Record selective disclosure;
- durable schema/version migration;
- HRE-backed rollback/integrity anchoring;
- full GuardianOS/device trust integration;
- production App-to-Core dependency/API integration.

---

## 6. Security boundary

Core-vNext verification MUST remain fail-closed.

A valid signature or valid Ledger Record MUST NOT be interpreted as proof of sovereign authorization by itself.

Conceptually:

```text
Signature
   != Authority
   != Capability
   != Policy permission
   != Execution Decision
   != Execution Release
   != physical execution
```

Similarly:

```text
Ledger Record
   != Authority
   != Authorization
   != Execution
```

The ledger records accountable history; it does not manufacture governance.

---

## 7. Promotion criterion

Core-vNext should be promoted from migration namespace toward the primary Core only after:

- cross-repo fixtures remain green;
- App and Core produce identical canonical records/roots from the same source history;
- cryptographic verification semantics match;
- version/schema behavior is explicit;
- no v1 security property is silently weakened;
- the App can consume Core-vNext without carrying a parallel implementation of the same canonical logic.

Until then, `dsan/core_vnext` is the interoperability laboratory and compatibility boundary, not a replacement for the current v1 kernel.
