# DSAN-core Release Checklist

## Scope freeze
- [x] v1.0 scope is frozen
- [x] No new features outside release scope
- [x] Limitations are explicitly documented

## Core functionality
- [x] Executor node starts successfully
- [x] Auditor node starts successfully
- [x] `/state` responds correctly
- [x] `/root` responds correctly
- [x] `/state_root` responds correctly
- [x] `/ledger` responds correctly
- [x] `/receive` accepts a valid new event
- [x] Totem authorization works with gesture input
- [x] Duplicate event submission returns expected result
- [x] Ledger persistence works after restart

## Verification
- [x] Merkle root is recomputed correctly
- [x] `state_root` matches replayed state
- [x] Auditor returns `CONSISTENT`
- [x] Ledger structure validation passes
- [x] Validator signature verification passes

## Documentation
- [x] `README.md` is up to date
- [x] `README.pt-BR.md` is up to date
- [x] Manual Totem test flow is documented
- [x] Repository structure is documented
- [x] Limitations are documented
- [x] Known issues are documented

## Release prep
- [x] Final file tree is reviewed
- [x] Legacy ledger entries are normalized if needed
- [x] Version/tag name is defined (`v1.0.0`)
- [x] Release notes summary is ready
- [x] Final smoke test has been executed