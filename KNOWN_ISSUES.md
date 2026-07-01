# Known Issues

These are the known issues and current limitations of DSAN-core.

## Current limitations
- Totem authorization is interactive and currently depends on terminal input.
- Consensus is not Byzantine fault tolerant.
- Validator identity governance is not yet persistent.
- Membership model is not finalized.
- Policy semantics are still evolving.
- Audit is local and developer-oriented, not yet a standalone production verifier.

## Operational notes
- The correct ingestion endpoint is `/receive`.
- Re-submitting the same packet may return `{"status":"duplicate"}`.
- Manual end-to-end tests require entering the Totem gesture in the executor node terminal.
- Older ledger entries may need normalization through `migrate_state_roots.py`.

## Not in v1.0
- BFT consensus
- production-grade distributed deployment
- finalized validator governance
- full externalized Totem integration