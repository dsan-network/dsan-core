"""Core-vNext accountable-history -> Execution Ledger projection.

This is the cross-repository migration bridge that mirrors the current
`dsan-app` Alpha 0.4 Execution Ledger semantics over already-accountable
history entries. It does not authorize, execute, mutate sovereign state, or
reinterpret source-event truth.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from .accountable_history import journal_genesis_event, journal_genesis_root, verify_accountable_history_entry
from .execution_ledger import ExecutionLedgerRecord, LedgerReject, build_execution_ledger_record, ledger_genesis_root

EVENT_CLASS = {
    "intent.submit": "INTENT_CREATED",
    "execution.request.create": "REQUEST_CREATED",
    "execution.decision.issue": "DECISION_CREATED",
    "guardian.authorization.request": "GUARDIAN_AUTHORIZATION_REQUESTED",
    "execution.release.issue": "EXECUTION_RELEASED",
    "execution.start": "EXECUTION_STARTED",
    "execution.complete": "EXECUTION_COMPLETED",
    "execution.fail": "EXECUTION_FAILED",
    "execution.cancel": "EXECUTION_CANCELLED",
    "execution.expire": "EXECUTION_EXPIRED",
    "execution.evidence.record": "EVIDENCE_CREATED",
    "execution.reconciliation.record": "EXECUTION_RECONCILIATION_RECORDED",
    # DSAN-SPEC-0010 Draft provides STATE_CHANGED and permits additional
    # domain events. Core-vNext preserves the source event_type while using the
    # existing stable class instead of inventing a normative Policy class.
    "policy.publish": "STATE_CHANGED",
    "policy.retire": "STATE_CHANGED",
}

REFERENCE_FIELDS = (
    "intent_id", "request_id", "policy_id", "policy_version", "version",
    "decision_id", "authorization_id", "release_id", "execution_id",
    "evidence_id", "reconciliation_id", "capability_id", "request_event_id",
    "decision_event_id", "release_event_id", "start_event_id", "outcome_event_id",
)


def _merge_reference_source(target: dict[str, Any], source: Any) -> None:
    if not isinstance(source, Mapping):
        return
    for field in REFERENCE_FIELDS:
        value = source.get(field)
        if value is not None and field not in target:
            if field == "version" and "policy_id" in source:
                target.setdefault("policy_version", value)
            else:
                target[field] = value
    authorization_ids = source.get("authorization_ids")
    if isinstance(authorization_ids, (list, tuple)) and all(isinstance(x, str) for x in authorization_ids):
        target.setdefault("authorization_ids", list(authorization_ids))


def _references(entry: Mapping[str, Any]) -> dict[str, Any]:
    refs: dict[str, Any] = {}
    event = entry["event"]
    _merge_reference_source(refs, event.get("payload"))
    _merge_reference_source(refs, entry.get("result"))
    return refs


def _provenance(entry: Mapping[str, Any]) -> dict[str, Any]:
    event = entry["event"]
    raw = event.get("provenance")
    provenance = dict(raw) if isinstance(raw, Mapping) else {}
    payload = event.get("payload")
    payload_provenance = payload.get("provenance") if isinstance(payload, Mapping) else None
    if isinstance(payload_provenance, Mapping):
        provenance["payload_provenance"] = dict(payload_provenance)
    provenance.update({
        "dse": event.get("subject"),
        "originating_actor": event.get("actor"),
        "journal_kind": entry.get("kind"),
        "journal_sequence": entry.get("sequence"),
    })
    return provenance


def _information_class(event_type: str) -> str:
    if event_type == "execution.reconciliation.record":
        return "STATE_OBSERVATION"
    return "ASSERTED_EVENT"


def project_accountable_history(subject: str, entries: Iterable[Mapping[str, Any]]) -> list[ExecutionLedgerRecord]:
    """Project a verified accountable history into canonical Ledger Records."""
    records: list[ExecutionLedgerRecord] = []
    previous_event = journal_genesis_event(subject)
    previous_history_root = journal_genesis_root(subject)
    previous_record_id: str | None = None
    previous_record_root = ledger_genesis_root(subject)

    for expected_sequence, raw in enumerate(entries, start=1):
        if not isinstance(raw, Mapping):
            raise LedgerReject("accountable history entry must be an object")
        entry = dict(raw)
        verified = verify_accountable_history_entry(
            subject, entry, expected_sequence=expected_sequence,
            expected_previous_event=previous_event,
            expected_previous_root=previous_history_root,
        )
        if not verified.accepted:
            raise LedgerReject(verified.reason)

        event = entry.get("event")
        if not isinstance(event, Mapping):
            raise LedgerReject("accountable history event must be an object")
        event_type = event.get("event_type")
        if not isinstance(event_type, str) or not event_type:
            raise LedgerReject("accountable history event_type is required")
        causation = event.get("causation", [])
        if not isinstance(causation, list) or not all(isinstance(x, str) for x in causation):
            raise LedgerReject("accountable history causation must be a string list")

        record = build_execution_ledger_record(
            subject=subject, sequence=expected_sequence,
            previous_record_id=previous_record_id,
            previous_record_root=previous_record_root,
            event_id=entry["event_id"], event_type=event_type,
            event_class=EVENT_CLASS.get(event_type, "DSAN_EVENT"),
            information_class=_information_class(event_type),
            event_time=event.get("timestamp") or event.get("created_at"),
            actor=event.get("actor", "unknown"), journal_kind=entry["kind"],
            accepted=entry["accepted"], references=_references(entry),
            causal_event_ids=causation, provenance=_provenance(entry),
            event_integrity=dict(event.get("integrity") or {}),
            journal_entry_root=entry["entry_root"], result_root=entry["result_root"],
        )
        records.append(record)
        previous_event = entry["event_id"]
        previous_history_root = entry["entry_root"]
        previous_record_id = record.record_id
        previous_record_root = record.record_root

    return records
