# DSAN-core v1.0.0 Release Notes

## Highlights

DSAN-core v1.0.0 establishes the first stabilized release of the DSAN execution and verification kernel.

This release delivers a functioning executor node, a dedicated auditor node, deterministic replay, `state_root` verification, Merkle-root recomputation, ledger normalization, and a documented manual Totem-gated execution flow.

## Included in this release

- Executor node with governed event reception and execution
- Dedicated Auditor Node for independent verification
- Canonical event hashing
- Ledger persistence and replay support
- Deterministic `state_root` derivation
- Merkle root recomputation and comparison
- Historical ledger normalization with `migrate_state_roots.py`
- Manual Totem-gated authorization flow
- English and Portuguese README documentation
- Release checklist and known issues tracking

## Validation status

The current release has been manually validated with:

- successful executor node startup
- successful auditor node startup
- successful event submission through `/receive`
- correct Totem authorization via terminal gesture input
- duplicate-event detection
- successful ledger growth after valid event execution
- successful replay consistency
- successful auditor result with `CONSISTENT`
- successful structural validation, Merkle-root match, and `state_root` match

## Known limitations

- Totem authorization is interactive and terminal-bound
- consensus is not Byzantine fault tolerant
- validator identity governance is not yet persistent
- membership is not finalized
- policy semantics are still evolving
- audit remains local and developer-oriented

## Version scope

This version should be understood as the first stable release of the DSAN-core kernel, not as a finished production network.

It provides a verifiable local execution core with replay, auditability, and state consistency guarantees suitable for continued protocol evolution.

## Tag

`v1.0.0`
