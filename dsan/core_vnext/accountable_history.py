"""Core-vNext accountable-history commitment verification.

This module verifies the deterministic commitment shape currently used by the
DSAN App Reference Runtime's UnifiedEvidenceJournal. It is an interoperability
bridge for Core-vNext migration, not a normative declaration that the App
journal serialization is the final DSAN Execution Ledger format.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .execution_ledger import sha256_json


class HistoryReject(ValueError):
    pass


def journal_genesis_event(subject: str) -> str:
    if not isinstance(subject, str) or not subject.startswith("dse:"):
        raise HistoryReject("journal subject must be a DSE reference")
    return f"event:{sha256_json({'journal_genesis': subject})[:26]}"


def journal_genesis_root(subject: str) -> str:
    head = journal_genesis_event(subject)
    return sha256_json({"subject": subject, "head": head, "sequence": 0})


@dataclass(frozen=True)
class AccountableHistoryVerificationResult:
    accepted: bool
    subject: str
    sequence: int
    event_id: str | None
    result_root: str | None
    entry_root: str | None
    reason: str


def verify_accountable_history_entry(
    subject: str,
    entry: Mapping[str, Any],
    *,
    expected_sequence: int | None = None,
    expected_previous_event: str | None = None,
    expected_previous_root: str | None = None,
) -> AccountableHistoryVerificationResult:
    """Verify one App-compatible accountable journal commitment.

    Event signatures remain a separate verification layer. This function only
    proves that event, result, ordering fields and roots are committed exactly
    by the expected journal formula.
    """
    try:
        if not isinstance(entry, Mapping):
            raise HistoryReject("history entry must be an object")
        sequence = entry.get("sequence")
        event_id = entry.get("event_id")
        previous_event = entry.get("previous_event")
        previous_root = entry.get("previous_root")
        kind = entry.get("kind")
        accepted = entry.get("accepted")
        event = entry.get("event")
        result = entry.get("result")
        result_root = entry.get("result_root")
        entry_root = entry.get("entry_root")

        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            raise HistoryReject("history sequence must be a positive integer")
        if expected_sequence is not None and sequence != expected_sequence:
            raise HistoryReject("history sequence mismatch")
        if not isinstance(event_id, str) or not event_id.startswith("event:"):
            raise HistoryReject("history event_id must be an event reference")
        if not isinstance(previous_event, str) or not previous_event.startswith("event:"):
            raise HistoryReject("history previous_event must be an event reference")
        if expected_previous_event is not None and previous_event != expected_previous_event:
            raise HistoryReject("history previous_event mismatch")
        if not isinstance(previous_root, str) or len(previous_root) != 64:
            raise HistoryReject("history previous_root must be a SHA-256 commitment")
        if expected_previous_root is not None and previous_root != expected_previous_root:
            raise HistoryReject("history previous_root mismatch")
        if not isinstance(kind, str) or not kind:
            raise HistoryReject("history kind is required")
        if not isinstance(accepted, bool):
            raise HistoryReject("history accepted must be boolean")
        if not isinstance(event, Mapping):
            raise HistoryReject("history event must be an object")
        if event.get("subject") != subject:
            raise HistoryReject("history event subject mismatch")
        if event.get("object_id") != event_id:
            raise HistoryReject("history event identity mismatch")
        if event.get("sequence") != sequence:
            raise HistoryReject("history event sequence mismatch")
        if event.get("previous_event") != previous_event:
            raise HistoryReject("history event previous_event mismatch")

        expected_result_root = sha256_json(result)
        if result_root != expected_result_root:
            raise HistoryReject("history result_root mismatch")

        material = {
            "subject": subject,
            "sequence": sequence,
            "previous_event": previous_event,
            "previous_root": previous_root,
            "event_id": event_id,
            "kind": kind,
            "accepted": accepted,
            "event": dict(event),
            "result": result,
            "result_root": result_root,
        }
        expected_entry_root = sha256_json(material)
        if entry_root != expected_entry_root:
            raise HistoryReject("history entry_root mismatch")

        return AccountableHistoryVerificationResult(
            True,
            subject,
            sequence,
            event_id,
            result_root,
            entry_root,
            "accountable history entry verified",
        )
    except (HistoryReject, TypeError, ValueError) as exc:
        return AccountableHistoryVerificationResult(
            False,
            subject,
            entry.get("sequence", 0) if isinstance(entry, Mapping) else 0,
            entry.get("event_id") if isinstance(entry, Mapping) else None,
            None,
            None,
            str(exc),
        )
