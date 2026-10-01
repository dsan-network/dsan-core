"""Core-vNext Execution Ledger interoperability verifier.

This module implements only the pure, read-only canonical record/chain contract
shared with the dsan-app Alpha 0.4 interoperability fixture. It intentionally
has no dependency on the legacy dsan-core v1 node, Totem, vote, execution,
ledger-packet, or state-replay code.

It is a migration target, not a declaration that the current v1 Ledger Packet
already conforms to DSAN-SPEC-0010.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping

LEDGER_PROTOCOL = "dsan:execution-ledger:alpha04:1"


class LedgerReject(ValueError):
    """Raised internally when a Core-vNext ledger contract is invalid."""


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def ledger_genesis_root(subject: str) -> str:
    if not isinstance(subject, str) or not subject.startswith("dse:"):
        raise LedgerReject("ledger subject must be a DSE reference")
    return sha256_json({
        "protocol": LEDGER_PROTOCOL,
        "subject": subject,
        "sequence": 0,
    })


def ledger_record_id(subject: str, sequence: int) -> str:
    if not isinstance(subject, str) or not subject.startswith("dse:"):
        raise LedgerReject("ledger subject must be a DSE reference")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise LedgerReject("ledger record sequence must be a positive integer")
    return f"ledger:{sha256_json({'subject': subject, 'sequence': sequence})}"


def _record_material(raw: Mapping[str, Any]) -> dict[str, Any]:
    material = dict(raw)
    material.pop("record_root", None)
    causal = material.get("causal_event_ids")
    if isinstance(causal, tuple):
        material["causal_event_ids"] = list(causal)
    return material


_REQUIRED_FIELDS = {
    "record_id",
    "sequence",
    "previous_record_id",
    "previous_record_root",
    "event_id",
    "event_type",
    "event_class",
    "information_class",
    "event_time",
    "subject",
    "actor",
    "journal_kind",
    "accepted",
    "references",
    "causal_event_ids",
    "provenance",
    "event_integrity",
    "journal_entry_root",
    "result_root",
    "record_root",
}


@dataclass(frozen=True)
class LedgerVerificationResult:
    accepted: bool
    subject: str
    sequence: int
    root: str | None
    head_record_id: str | None
    reason: str


def _validate_record_shape(row: Mapping[str, Any]) -> None:
    missing = _REQUIRED_FIELDS - set(row)
    if missing:
        raise LedgerReject(f"ledger record missing fields: {sorted(missing)}")
    if not isinstance(row.get("event_id"), str) or not row["event_id"].startswith("event:"):
        raise LedgerReject("ledger event_id must be an event reference")
    if not isinstance(row.get("event_type"), str) or not row["event_type"]:
        raise LedgerReject("ledger event_type is required")
    if not isinstance(row.get("event_class"), str) or not row["event_class"]:
        raise LedgerReject("ledger event_class is required")
    if not isinstance(row.get("information_class"), str) or not row["information_class"]:
        raise LedgerReject("ledger information_class is required")
    if not isinstance(row.get("actor"), str) or ":" not in row["actor"]:
        raise LedgerReject("ledger actor must be a DSAN reference")
    if not isinstance(row.get("journal_kind"), str) or not row["journal_kind"]:
        raise LedgerReject("ledger journal_kind is required")
    if not isinstance(row.get("accepted"), bool):
        raise LedgerReject("ledger accepted must be boolean")
    if not isinstance(row.get("references"), dict):
        raise LedgerReject("ledger references must be an object")
    if not isinstance(row.get("causal_event_ids"), list) or not all(isinstance(x, str) for x in row["causal_event_ids"]):
        raise LedgerReject("ledger causal_event_ids must be a string list")
    if not isinstance(row.get("provenance"), dict):
        raise LedgerReject("ledger provenance must be an object")
    if not isinstance(row.get("event_integrity"), dict):
        raise LedgerReject("ledger event_integrity must be an object")
    for field in ("previous_record_root", "journal_entry_root", "result_root", "record_root"):
        value = row.get(field)
        if not isinstance(value, str) or len(value) != 64:
            raise LedgerReject(f"ledger {field} must be a SHA-256 commitment")


def verify_execution_ledger_records(
    subject: str,
    records: Iterable[Mapping[str, Any]],
) -> LedgerVerificationResult:
    """Verify canonical Core-vNext record identity, ordering and hash chaining.

    This function deliberately verifies the ledger-record contract only. Real
    event signatures and source-journal semantics remain separate verification
    layers and are not faked by this fixture verifier.
    """
    previous_id: str | None = None
    previous_root: str
    try:
        previous_root = ledger_genesis_root(subject)
        count = 0
        for expected_sequence, raw in enumerate(records, start=1):
            if not isinstance(raw, Mapping):
                raise LedgerReject("ledger record must be an object")
            row = dict(raw)
            _validate_record_shape(row)
            count = expected_sequence

            if row.get("sequence") != expected_sequence:
                raise LedgerReject("ledger sequence mismatch")
            expected_id = ledger_record_id(subject, expected_sequence)
            if row.get("record_id") != expected_id:
                raise LedgerReject("ledger record_id mismatch")
            if row.get("subject") != subject:
                raise LedgerReject("ledger record subject mismatch")
            if row.get("previous_record_id") != previous_id:
                raise LedgerReject("ledger previous_record_id mismatch")
            if row.get("previous_record_root") != previous_root:
                raise LedgerReject("ledger previous_record_root mismatch")
            if row.get("event_id") == row.get("record_id"):
                raise LedgerReject("ledger event identity is collapsed into record identity")

            expected_root = sha256_json(_record_material(row))
            if row.get("record_root") != expected_root:
                raise LedgerReject("ledger record integrity mismatch")

            previous_id = expected_id
            previous_root = expected_root

        return LedgerVerificationResult(
            True,
            subject,
            count,
            previous_root,
            previous_id,
            "execution ledger fixture verified",
        )
    except (LedgerReject, TypeError, ValueError) as exc:
        return LedgerVerificationResult(
            False,
            subject,
            locals().get("count", 0),
            None,
            previous_id,
            str(exc),
        )
