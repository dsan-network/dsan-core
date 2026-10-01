"""DSAN Core-vNext experimental namespace.

This package is intentionally isolated from the current dsan-core v1 execution
kernel. Nothing in here changes legacy node, replay, Totem, Ledger Packet, or
API behavior until explicit interoperability gates are passed.
"""

from .accountable_history import (
    AccountableHistoryVerificationResult,
    HistoryReject,
    journal_genesis_event,
    journal_genesis_root,
    verify_accountable_history_entry,
)
from .event_crypto import (
    EventKeyBinding,
    EventVerificationResult,
    signing_bytes,
    signing_view,
    verify_signed_event,
)
from .execution_ledger import (
    LEDGER_PROTOCOL,
    ExecutionLedgerRecord,
    ExecutionLedgerState,
    LedgerReject,
    LedgerVerificationResult,
    build_execution_ledger_record,
    canonical_json,
    execution_ledger_state,
    ledger_genesis_root,
    ledger_record_id,
    sha256_json,
    verify_execution_ledger_records,
)
from .ledger_projection import (
    EVENT_CLASS,
    REFERENCE_FIELDS,
    project_accountable_history,
)

__all__ = [
    "AccountableHistoryVerificationResult",
    "EVENT_CLASS",
    "EventKeyBinding",
    "EventVerificationResult",
    "ExecutionLedgerRecord",
    "ExecutionLedgerState",
    "HistoryReject",
    "LEDGER_PROTOCOL",
    "LedgerReject",
    "LedgerVerificationResult",
    "REFERENCE_FIELDS",
    "build_execution_ledger_record",
    "canonical_json",
    "execution_ledger_state",
    "journal_genesis_event",
    "journal_genesis_root",
    "ledger_genesis_root",
    "ledger_record_id",
    "project_accountable_history",
    "sha256_json",
    "signing_bytes",
    "signing_view",
    "verify_accountable_history_entry",
    "verify_execution_ledger_records",
    "verify_signed_event",
]
