import copy
import json
import unittest
from pathlib import Path

from dsan.core_vnext import (
    execution_ledger_state,
    journal_genesis_event,
    journal_genesis_root,
    project_accountable_history,
    sha256_json,
    verify_execution_ledger_records,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "core_vnext" / "governed_cycle_v1.json"


def build_history(fixture):
    subject = fixture["subject"]
    previous_event = journal_genesis_event(subject)
    previous_root = journal_genesis_root(subject)
    history = []
    for sequence, spec in enumerate(fixture["events"], start=1):
        event = {
            "schema": "dsan:event:1",
            "object_id": spec["event_id"],
            "object_type": "event",
            "version": 1,
            "event_type": spec["event_type"],
            "subject": subject,
            "actor": spec["actor"],
            "timestamp": spec["timestamp"],
            "created_at": spec["timestamp"],
            "sequence": sequence,
            "previous_event": previous_event,
            "causation": list(spec["causation"]),
            "payload": copy.deepcopy(spec["payload"]),
            "provenance": {"fixture": "governed-cycle-v1"},
            "integrity": copy.deepcopy(spec["integrity"]),
            "authorized": False,
        }
        result = copy.deepcopy(spec["result"])
        result_root = sha256_json(result)
        material = {
            "subject": subject,
            "sequence": sequence,
            "previous_event": previous_event,
            "previous_root": previous_root,
            "event_id": spec["event_id"],
            "kind": spec["kind"],
            "accepted": bool(result.get("accepted", False)),
            "event": event,
            "result": result,
            "result_root": result_root,
        }
        entry_root = sha256_json(material)
        history.append({**material, "entry_root": entry_root})
        previous_event = spec["event_id"]
        previous_root = entry_root
    return history


class CoreVNextGovernedCycleContracts(unittest.TestCase):
    def load(self):
        return json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_full_governed_cycle_projects_to_expected_records(self):
        fixture = self.load()
        history = build_history(fixture)
        records = project_accountable_history(fixture["subject"], history)
        expected = fixture["expected"]
        self.assertEqual(expected["record_ids"], [x.record_id for x in records])
        self.assertEqual(expected["record_roots"], [x.record_root for x in records])
        self.assertEqual(expected["event_classes"], [x.event_class for x in records])
        self.assertEqual(expected["information_classes"], [x.information_class for x in records])
        self.assertEqual(expected["reconciliation_references"][0], records[5].references)
        self.assertEqual(expected["reconciliation_references"][1], records[6].references)
        self.assertEqual(expected["evidence_references"], records[7].references)
        state = execution_ledger_state(fixture["subject"], records)
        self.assertEqual(expected["sequence"], state.sequence)
        self.assertEqual(expected["head_record_id"], state.head_record_id)
        self.assertEqual(expected["ledger_root"], state.root)

    def test_projected_cycle_is_independently_verifiable(self):
        fixture = self.load()
        records = project_accountable_history(fixture["subject"], build_history(fixture))
        verified = verify_execution_ledger_records(fixture["subject"], records)
        self.assertTrue(verified.accepted, verified.reason)
        self.assertEqual(fixture["expected"]["ledger_root"], verified.root)

    def test_reconciliation_remains_observation_not_authority(self):
        fixture = self.load()
        records = project_accountable_history(fixture["subject"], build_history(fixture))
        for record in records[5:7]:
            self.assertEqual("EXECUTION_RECONCILIATION_RECORDED", record.event_class)
            self.assertEqual("STATE_OBSERVATION", record.information_class)
            self.assertEqual("executor:fixture", record.actor)
        self.assertEqual("EVIDENCE_CREATED", records[7].event_class)
        self.assertEqual("event:cycle-reconcile-2", records[7].references["outcome_event_id"])

    def test_history_tampering_is_rejected_before_ledger_projection(self):
        fixture = self.load()
        history = build_history(fixture)
        history[2]["result"]["decision_state"] = "DENIED"
        with self.assertRaisesRegex(ValueError, "result_root"):
            project_accountable_history(fixture["subject"], history)


if __name__ == "__main__":
    unittest.main()
