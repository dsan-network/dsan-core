"""Core-vNext API/version contract.

This manifest is the machine-readable compatibility boundary used by external
consumers such as dsan-app. Package version and API version are intentionally
separate: package releases may change without breaking the API contract, while
an incompatible API change MUST change ``API_VERSION``.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

CONTRACT_SCHEMA = "dsan:core-vnext-contract:1"
API_VERSION = "1.0"
PACKAGE_VERSION = "0.2.0a2"

SUPPORTED_PROTOCOLS = (
    "dsan:execution-ledger:alpha04:1",
)

FEATURES = (
    "accountable-history.verify/1",
    "event.ed25519.verify/1",
    "execution-ledger.project/1",
    "execution-ledger.verify/1",
    "execution-ledger.state/1",
    "execution-ledger.policy-lifecycle/1",
)


@dataclass(frozen=True)
class CoreVNextContract:
    contract_schema: str
    api_version: str
    package_version: str
    protocols: tuple[str, ...]
    features: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        raw = asdict(self)
        raw["protocols"] = list(self.protocols)
        raw["features"] = list(self.features)
        return raw


def core_vnext_contract() -> CoreVNextContract:
    """Return the immutable compatibility manifest for this installed build."""
    return CoreVNextContract(
        contract_schema=CONTRACT_SCHEMA,
        api_version=API_VERSION,
        package_version=PACKAGE_VERSION,
        protocols=SUPPORTED_PROTOCOLS,
        features=FEATURES,
    )
