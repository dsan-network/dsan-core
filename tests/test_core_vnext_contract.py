import importlib.metadata
import unittest

from dsan.core_vnext import (
    API_VERSION,
    CONTRACT_SCHEMA,
    FEATURES,
    LEDGER_PROTOCOL,
    PACKAGE_VERSION,
    SUPPORTED_PROTOCOLS,
    core_vnext_contract,
)


class CoreVNextContractTests(unittest.TestCase):
    def test_manifest_is_explicit_and_self_consistent(self):
        contract = core_vnext_contract()
        self.assertEqual("dsan:core-vnext-contract:1", CONTRACT_SCHEMA)
        self.assertEqual("1.0", API_VERSION)
        self.assertEqual("0.2.0a2", PACKAGE_VERSION)
        self.assertEqual(CONTRACT_SCHEMA, contract.contract_schema)
        self.assertEqual(API_VERSION, contract.api_version)
        self.assertEqual(PACKAGE_VERSION, contract.package_version)
        self.assertIn(LEDGER_PROTOCOL, contract.protocols)
        self.assertEqual(tuple(SUPPORTED_PROTOCOLS), contract.protocols)
        self.assertEqual(tuple(FEATURES), contract.features)
        self.assertIn("execution-ledger.policy-lifecycle/1", contract.features)

    def test_installed_distribution_version_matches_manifest(self):
        self.assertEqual(PACKAGE_VERSION, importlib.metadata.version("dsan-core-vnext"))

    def test_manifest_wire_shape_uses_json_lists(self):
        raw = core_vnext_contract().to_dict()
        self.assertEqual(CONTRACT_SCHEMA, raw["contract_schema"])
        self.assertEqual(API_VERSION, raw["api_version"])
        self.assertEqual(PACKAGE_VERSION, raw["package_version"])
        self.assertIsInstance(raw["protocols"], list)
        self.assertIsInstance(raw["features"], list)
        self.assertIn("execution-ledger.project/1", raw["features"])
        self.assertIn("execution-ledger.policy-lifecycle/1", raw["features"])


if __name__ == "__main__":
    unittest.main()
