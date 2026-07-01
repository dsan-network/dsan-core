## DSAN-core recovered milestone

This update consolidates the recovered DSAN-core branch into a verifiable execution baseline.

### Added
- Dedicated Auditor Node service for remote verification.
- Independent replay-based audit flow.
- Merkle root recomputation and comparison in the auditor.
- Validator-signature verification in the auditor.
- Per-entry `state_root` normalization for historical ledger consistency.
- New technical documentation:
  - `README.md`
  - `docs/ARCHITECTURE.md`
  - `docs/ROADMAP.md`
  - `docs/PROTOCOL.md`

### Improved
- Clearer positioning of DSAN-core as a verifiable execution kernel.
- Better separation between executor and verifier roles.
- More explicit protocol and architectural documentation.
- Local development flow for send, audit, and ledger normalization.

### Validated
- Executor node startup and ledger persistence.
- Event submission and execution.
- Deterministic replay.
- `state_root` consistency.
- Merkle root consistency.
- Independent remote audit with `CONSISTENT` result.

### Notes
This milestone is still experimental and not Byzantine fault tolerant.  
It represents a recovered and stabilized foundation for the next DSAN-core stages, especially Auditor Node hardening, validator identity, and stricter sync verification.
