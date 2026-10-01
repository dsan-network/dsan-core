import copy
import json
import unittest
from pathlib import Path

from dsan.core_vnext.accountable_history import (
    journal_genesis_event,
    journal_genesis_root,
    verify_accountable_history_entry,
)
from dsan.core_vnext.event_crypto import EventKeyBinding, verify_signed_event
from dsan.core_vnext.execution_ledger import (
    build_execution_ledger_record,
    execution_ledger_state,
    verify_execution_ledger_records,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "core_vnext" / "signed_event_ledger_v1.json"


class CoreVNextSignedLedgerFixtureContracts(unittest.TestCase):
    def load(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_signed_event_history_and_ledger_all_verify(self):
        fixture = self.load()
        subject = fixture["subject"]
        entry = fixture["source_history_entry"]
        binding = EventKeyBinding(**fixture["key_binding"])

        signature = verify_signed_event(entry["event"], binding)
        self.assertTrue(signature.accepted, signature.reason)

        history = verify_accountable_history_entry(
            subject,
            entry,
            expected_sequence=1,
            expected_previous_event=journal_genesis_event(subject),
            expected_previous_root=journal_genesis_root(subject),
        )
        self.assertTrue(history.accepted, history.reason)

        ledger = verify_execution_ledger_records(subject, [fixture["ledger_record"]])
        self.assertTrue(ledger.accepted, ledger.reason)
        self.assertEqual(fixture["expected_ledger_state"]["root"], ledger.root)

    def test_core_builder_recreates_signed_fixture_ledger_record_exactly(self):
        fixture = self.load()
        expected = fixture["ledger_record"]
        built = build_execution_ledger_record(
            subject=expected["subject"],
            sequence=expected["sequence"],
            previous_record_id=expected["previous_record_id"],
            previous_record_root=expected["previous_record_root"],
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
        state = execution_ledger_state(fixture["subject"], [built])
        self.assertEqual(fixture["expected_ledger_state"], {
            "protocol": state.protocol,
            "subject": state.subject,
            "sequence": state.sequence,
            "head_record_id": state.head_record_id,
            "root": state.root,
            "status": state.status,
        })

    def test_event_payload_tampering_breaks_signature(self):
        fixture = self.load()
        event = copy.deepcopy(fixture["source_history_entry"]["event"])
        event["payload"]["target"] = "record:forged"
        result = verify_signed_event(event, EventKeyBinding(**fixture["key_binding"]))
        self.assertFalse(result.accepted)
        self.assertIn("signature", result.reason)

    def test_result_tampering_breaks_accountable_history_commitment(self):
        fixture = self.load()
        entry = copy.deepcopy(fixture["source_history_entry"])
        entry["result"]["reason"] = "forged"
        result = verify_accountable_history_entry(
            fixture["subject"],
            entry,
            expected_sequence=1,
            expected_previous_event=journal_genesis_event(fixture["subject"]),
            expected_previous_root=journal_genesis_root(fixture["subject"]),
        )
        self.assertFalse(result.accepted)
        self.assertIn("result_root", result.reason)

    def test_ledger_reference_tampering_breaks_record_commitment(self):
        fixture = self.load()
        record = copy.deepcopy(fixture["ledger_record"])
        record["references"]["request_id"] = "request:forged"
        result = verify_execution_ledger_records(fixture["subject"], [record])
        self.assertFalse(result.accepted)
        self.assertIn("integrity", result.reason)


if __name__ == "__main__":
    unittest.main()
