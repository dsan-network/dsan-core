# Core-vNext API Negotiation and Release Strategy

**Status:** experimental migration contract  
**Package:** `dsan-core-vnext`  
**Current package version:** `0.2.0a1`  
**Current API version:** `1.0`  
**Contract schema:** `dsan:core-vnext-contract:1`

---

## 1. Versions are intentionally separate

Core-vNext distinguishes four version domains:

```text
package version
    != API version
    != contract schema
    != protocol/schema version
```

The package version identifies a distributable build.

The API version identifies the callable interoperability surface consumed by external repositories such as `dsan-app`.

The contract schema versions the machine-readable compatibility manifest itself.

Protocol/schema versions identify wire or canonical semantic formats such as:

```text
dsan:execution-ledger:alpha04:1
```

A package update MUST NOT be interpreted as an API compatibility signal by itself.

---

## 2. Machine-readable contract

The installed package exposes:

```python
from dsan.core_vnext import core_vnext_contract
```

The manifest contains:

- `contract_schema`;
- `api_version`;
- `package_version`;
- supported protocol identifiers;
- explicit feature identifiers.

Current required features are:

```text
accountable-history.verify/1
event.ed25519.verify/1
execution-ledger.project/1
execution-ledger.verify/1
execution-ledger.state/1
```

Consumers MUST negotiate this manifest before invoking the Core-vNext backend.

---

## 3. Fail-closed compatibility rule

During Alpha 0.4 migration, compatibility is explicit rather than optimistic.

A consumer MUST reject Core-vNext before use when any of the following is true:

1. contract schema is unknown;
2. API version is unsupported;
3. required protocol is absent;
4. required feature is absent;
5. the installed package version is outside the consumer's explicitly supported set;
6. the package's advertised version and installed distribution metadata disagree.

There is no automatic fallback from an incompatible Core-vNext backend to a local implementation when Core-vNext was explicitly selected as primary.

---

## 4. Compatibility evolution

### Package version

Core-vNext uses PEP 440/SemVer-style package versions. Pre-release package changes may be frequent while the API remains stable.

### API version

`API_VERSION` is a separate `MAJOR.MINOR` contract.

- incompatible callable/semantic changes require a new API major;
- additive changes may use a new API minor;
- consumers still list supported API versions explicitly during the Alpha phase.

### Protocol versions

Protocol identifiers are exact opaque strings. A new protocol version is not assumed compatible with an older protocol unless the consumer explicitly declares support.

### Feature versions

Feature identifiers are capability-scoped and versioned independently using a `/N` suffix.

---

## 5. Development pin versus release pin

Until the first deliberate Core-vNext tag/release is created, `dsan-app` SHOULD pin an exact Git commit and validate the machine-readable contract at runtime/CI.

Development form:

```text
dsan-core-vnext @ git+https://github.com/dsan-network/dsan-core.git@<exact-commit>
```

After API/release stabilization, the preferred form is a signed/annotated repository tag associated with a package version, for example:

```text
core-vnext-v0.2.0a1
```

and a corresponding GitHub release/changelog entry.

The tag MUST resolve to a commit whose `pyproject.toml` package version and `core_vnext_contract().package_version` are identical.

---

## 6. Promotion requirements

A Core-vNext package version is eligible for promotion from development pin to release pin only when:

- Core-vNext package installation succeeds in CI;
- package metadata matches `PACKAGE_VERSION`;
- the contract manifest passes self-consistency tests;
- cross-repository fixtures remain byte-identical where required;
- governed-cycle parity remains green;
- real-runtime shadow parity remains green for persistence, federation and negative/conditional paths;
- explicit unsupported-version tests remain fail-closed.

---

## 7. Current release position

`0.2.0a1 / API 1.0` is the first build with an explicit machine-readable compatibility boundary.

It is still experimental. The current App integration SHOULD continue using an exact commit pin until an explicit repository tag/release is created.

No tag creation is implied merely by changing `pyproject.toml`.
