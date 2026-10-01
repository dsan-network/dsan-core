"""Core-vNext canonical event-signature verification primitives.

This verifier is intentionally narrow: it verifies attribution/integrity for
one Ed25519-signed DSAN event against an explicit public-key binding. It does
not create authority, validate policy, authorize execution, or manage the full
key lifecycle.
"""
from __future__ import annotations

from dataclasses import dataclass
import base64
import copy
from typing import Any, Mapping

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .execution_ledger import canonical_json

ALGORITHM = "Ed25519"


def _unb64(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def signing_view(event: Mapping[str, Any]) -> dict[str, Any]:
    view = copy.deepcopy(dict(event))
    integrity = dict(view.get("integrity") or {})
    integrity.pop("signature", None)
    view["integrity"] = integrity
    return view


def signing_bytes(event: Mapping[str, Any]) -> bytes:
    return canonical_json(signing_view(event))


@dataclass(frozen=True)
class EventKeyBinding:
    identity: str
    key_id: str
    algorithm: str
    public_key: str


@dataclass(frozen=True)
class EventVerificationResult:
    accepted: bool
    event_id: str
    signer: str
    key_id: str | None
    reason: str

    @property
    def valid(self) -> bool:
        return self.accepted


def verify_signed_event(event: Mapping[str, Any], binding: EventKeyBinding) -> EventVerificationResult:
    eid = event.get("object_id", "event:invalid")
    actor = event.get("actor", "unknown")
    integrity = event.get("integrity")
    if not isinstance(integrity, Mapping):
        return EventVerificationResult(False, eid, actor, None, "missing integrity object")

    signer = integrity.get("signer")
    key_id = integrity.get("key_id")
    algorithm = integrity.get("algorithm")
    signature = integrity.get("signature")

    if signer != actor or binding.identity != actor:
        return EventVerificationResult(False, eid, actor, key_id if isinstance(key_id, str) else None, "event signer/binding identity mismatch")
    if algorithm != ALGORITHM or binding.algorithm != ALGORITHM:
        return EventVerificationResult(False, eid, actor, key_id if isinstance(key_id, str) else None, "unsupported event signing algorithm")
    if key_id != binding.key_id:
        return EventVerificationResult(False, eid, actor, key_id if isinstance(key_id, str) else None, "event key_id does not match binding")
    if not isinstance(signature, str):
        return EventVerificationResult(False, eid, actor, key_id if isinstance(key_id, str) else None, "missing event signature")

    try:
        public = Ed25519PublicKey.from_public_bytes(_unb64(binding.public_key))
        public.verify(_unb64(signature), signing_bytes(event))
    except (InvalidSignature, ValueError, TypeError):
        return EventVerificationResult(False, eid, actor, key_id, "invalid event signature")

    return EventVerificationResult(True, eid, actor, key_id, "event signature verified")
