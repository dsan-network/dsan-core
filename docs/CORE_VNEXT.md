# DSAN Core-vNext — Interoperability Boundary

**Status:** experimental Reference Profile migration layer; App shadow consumption active  
**Current scope:** accountable event integrity + accountable-history commitments + Execution Ledger canonical records/projection  
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

and the governed runtime distinguishes:

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

### Accountable-history projection

`ledger_projection.py` consumes already-accountable history and deterministically projects it into Core-vNext `ExecutionLedgerRecord` objects.

The projector preserves:

- Event ID / Record ID separation;
- event class;
- information class;
- causal event references;
- Request / Decision / Release / Execution / Evidence / Reconciliation references;
- provenance;
- source journal commitments;
- canonical Ledger chaining.

It performs no Authority evaluation and no execution.

### Execution Ledger Record construction/verification

`execution_ledger.py` provides:

- deterministic `ledger:*` Record IDs;
- independent Ledger Genesis Root;
- canonical `record_root` construction;
- `previous_record_id` / `previous_record_root` chaining;
- deterministic Ledger State derivation;
- tamper detection;
- pure read-only verification.

---

## 3. Installable package boundary

The repository now contains a minimal `pyproject.toml` exposing only:

```text
dsan
dsan.core_vnext
```

as package:

```text
dsan-core-vnext
```

This package boundary exists for migration/interoperability testing. It does not package or replace the legacy v1 execution kernel.

The Core-vNext CI installs the repository with:

```text
pip install .
```

and verifies that the installed namespace exposes the expected projection API before running interoperability tests.

---

## 4. Cross-repository fixtures

### Structural fixture

```text
fixtures/core_vnext/execution_ledger_v1.json
Git Blob SHA: 756f9b84fd6022bb917dd26fe8f26c411f62c3d3
```

Expected Ledger Root:

```text
6afa3c1432aa1c837e1cd6e8fa099d42c52ccacbe5a2518991cdf95087016d10
```

### Signed fixture

```text
fixtures/core_vnext/signed_event_ledger_v1.json
Git Blob SHA: 2fd3de7d8b8e35bd5553545c5d31472b561e94d4
```

It proves:

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

### Governed-cycle fixture

```text
fixtures/core_vnext/governed_cycle_v1.json
Git Blob SHA: a1038828f02dbfebde1e1b1c5c5dfd0cf5283af4
```

The scenario covers:

```text
Intent
  ↓
Execution Request
  ↓
EAF Decision — AUTHORIZED
  ↓
Execution Release
  ↓
EXECUTION_STARTED
  ↓
Reconciliation — INCONCLUSIVE
  ↓
Reconciliation — EXECUTED / COMPLETED
  ↓
Execution Evidence
```

Both repositories independently produce the same eight Ledger Records and final root:

```text
cf1564b7f53ce58a0e43c7e5eae42dd278b7f115d51b801192e2e66e91826709
```

Reconciliation remains represented as `STATE_OBSERVATION`, not authorization.

---

## 5. Migration stages

Current progress:

```text
Stage A — fixture contract in dsan-app                 DONE
Stage B — independent parser/verifier in dsan-core    DONE
Stage C — byte-identical cross-repo fixture parity    DONE
Stage D — Core-vNext ledger/event/projection API       ESTABLISHED FOR CURRENT SLICE
Stage E — dsan-app consumes Core-vNext API             IN PROGRESS / SHADOW MODE
Stage F — duplicate App implementations removed        NOT STARTED
```

Stage E was started without deleting working App logic.

The App now has an optional fail-closed bridge that installs a pinned Core-vNext commit in a dedicated interoperability workflow and compares the external projection with its local projection.

This means Core-vNext is now actually consumed cross-repository under CI, while production App semantics remain unchanged.

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

Reconciliation records are observations/assertions about execution state. Their presence in the ledger does not create permission to execute or re-execute.

---

## 7. What Core-vNext does not yet claim

Core-vNext does not yet provide a complete DSAN-SPEC-0010 conformant production Execution Ledger.

Open areas include:

- complete event-class catalog;
- version/schema negotiation;
- denied and conditional/Guardian-authorized execution fixtures;
- rejected, failed and cancelled path parity;
- generic synchronization/conflict Ledger Records;
- first-class distributed Ledger Record exchange;
- ledger retention lifecycle;
- Ledger Record selective disclosure;
- durable schema/version migration;
- HRE-backed rollback/integrity anchoring;
- full GuardianOS/device trust integration;
- production release/version strategy for App-to-Core dependency.

---

## 8. Promotion criterion

Core-vNext should be promoted from migration namespace toward the primary Core only after:

- structural, cryptographic and governed-cycle fixtures remain green;
- App and Core produce identical canonical records/roots from the same source histories;
- shadow parity is exercised against live/recovered/federated runtime histories;
- cryptographic verification semantics match;
- version/schema behavior is explicit;
- no v1 security property is silently weakened;
- an observed migration period shows no App/Core divergence;
- the App can switch read-only ledger/proof paths to Core-vNext before deleting duplicate code.

Until then, `dsan/core_vnext` is the interoperability laboratory and compatibility boundary, not a replacement for the current v1 kernel.
