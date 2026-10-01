import copy
import json
import unittest
from pathlib import Path

from dsan.core_vnext.execution_ledger import (
    LEDGER_PROTOCOL,
    build_execution_ledger_record,
    execution_ledger_state,
    ledger_genesis_root,
    ledger_record_id,
    verify_execution_ledger_records,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "core_vnext" / "execution_ledger_v1.json"


class CoreVNextExecutionLedgerContracts(unittest.TestCase):
    def load(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_shared_fixture_verifies_without_dsan_app_dependency(self):
        fixture = self.load()
        self.assertEqual(LEDGER_PROTOCOL, fixture["protocol"])
        result = verify_execution_ledger_records(fixture["subject"], fixture["records"])
        self.assertTrue(result.accepted, result.reason)
        expected = fixture["expected_state"]
        self.assertEqual(expected["sequence"], result.sequence)
        self.assertEqual(expected["root"], result.root)
        self.assertEqual(expected["head_record_id"], result.head_record_id)

    def test_canonical_ids_and_genesis_match_fixture_contract(self):
        fixture = self.load()
        subject = fixture["subject"]
        self.assertEqual(
            "a1d8dbf5bfbb880e394b6598579e1024a8807912851e4043edd1ddcc3271a57d",
            ledger_genesis_root(subject),
        )
        for sequence, record in enumerate(fixture["records"], start=1):
            self.assertEqual(ledger_record_id(subject, sequence), record["record_id"])
            self.assertNotEqual(record["record_id"], record["event_id"])

    def test_builder_regenerates_fixture_records_exactly(self):
        fixture = self.load()
        subject = fixture["subject"]
        previous_id = None
        previous_root = ledger_genesis_root(subject)
        generated = []
        for expected in fixture["records"]:
            built = build_execution_ledger_record(
                subject=subject,
                sequence=expected["sequence"],
                previous_record_id=previous_id,
                previous_record_root=previous_root,
                event_id=expected["event_id"],
                event_type=expected["event_type"],
                event_class=expected["event_class"],
                information_class=expected["information_class"],
                event_time=expected["event_time"],
                actor=expected["actor"],
                journal_kind=expected["journal_kind"],
                accepted=expected["accepted"],
                references=expected["references"],
                causal_event_ids=expected["causal_event_ids"],
                provenance=expected["provenance"],
                event_integrity=expected["event_integrity"],
                journal_entry_root=expected["journal_entry_root"],
                result_root=expected["result_root"],
            )
            self.assertEqual(expected, built.to_dict())
            generated.append(built)
            previous_id = built.record_id
            previous_root = built.record_root

        state = execution_ledger_state(subject, generated)
        expected_state = fixture["expected_state"]
        self.assertEqual(expected_state["protocol"], state.protocol)
        self.assertEqual(expected_state["subject"], state.subject)
        self.assertEqual(expected_state["sequence"], state.sequence)
        self.assertEqual(expected_state["head_record_id"], state.head_record_id)
        self.assertEqual(expected_state["root"], state.root)
        self.assertEqual(expected_state["status"], state.status)

    def test_semantic_drift_breaks_record_integrity(self):
        fixture = self.load()
        records = copy.deepcopy(fixture["records"])
        records[0]["references"]["policy_version"] = 2
        result = verify_execution_ledger_records(fixture["subject"], records)
        self.assertFalse(result.accepted)
        self.assertIn("integrity", result.reason)

    def test_reordering_is_rejected(self):
        fixture = self.load()
        records = list(reversed(copy.deepcopy(fixture["records"])))
        result = verify_execution_ledger_records(fixture["subject"], records)
        self.assertFalse(result.accepted)
        self.assertTrue("sequence" in result.reason or "record_id" in result.reason)

    def test_broken_previous_record_root_is_rejected(self):
        fixture = self.load()
        records = copy.deepcopy(fixture["records"])
        records[1]["previous_record_root"] = "0" * 64
        result = verify_execution_ledger_records(fixture["subject"], records)
        self.assertFalse(result.accepted)
        self.assertIn("previous_record_root", result.reason)

    def test_event_identity_cannot_collapse_into_record_identity(self):
        fixture = self.load()
        records = copy.deepcopy(fixture["records"])
        records[0]["event_id"] = records[0]["record_id"]
        result = verify_execution_ledger_records(fixture["subject"], records)
        self.assertFalse(result.accepted)
        self.assertIn("event", result.reason)


if __name__ == "__main__":
    unittest.main()
