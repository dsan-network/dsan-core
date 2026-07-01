import hashlib
import json
import requests
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from dsan.core.replay import replay_ledger


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def hash_event(event):
    return hashlib.sha256(canonical_json(event).encode()).hexdigest()


def verify_ed25519_signature(pub_hex, sig_hex, message_bytes):
    try:
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
        pub.verify(bytes.fromhex(sig_hex), message_bytes)
        return True
    except Exception:
        return False


def validate_validator_signatures(entry, index):
    validators = entry.get("validators", [])
    if not isinstance(validators, list) or not validators:
        return False, f"missing_validators_at_{index}"

    message = entry["hash"].encode()

    for v in validators:
        if not all(k in v for k in ("node", "pub", "sig")):
            return False, f"malformed_validator_at_{index}"

        ok = verify_ed25519_signature(v["pub"], v["sig"], message)
        if not ok:
            return False, f"invalid_validator_signature_at_{index}"

    return True, "ok"


def validate_ledger_structure(ledger):
    if not isinstance(ledger, list):
        return False, "ledger_not_list"

    prev_expected = "0" * 64

    for i, entry in enumerate(ledger):
        if "event" not in entry or "hash" not in entry:
            return False, f"missing_fields_at_{i}"

        event = entry["event"]
        event_hash = hash_event(event)

        if entry["hash"] != event_hash:
            return False, f"invalid_hash_at_{i}"

        if event.get("prev_hash") != prev_expected:
            return False, f"chain_mismatch_at_{i}"

        if "state_root" not in entry:
            return False, f"missing_state_root_at_{i}"

        validators_ok, validators_reason = validate_validator_signatures(entry, i)
        if not validators_ok:
            return False, validators_reason

        prev_expected = entry["hash"]

    return True, "ok"


def calculate_merkle_root(ledger):
    hashes = [entry["hash"] for entry in ledger]

    if not hashes:
        return hashlib.sha256(b"").hexdigest()

    level = hashes[:]

    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])

        next_level = []
        for i in range(0, len(level), 2):
            combined = (level[i] + level[i + 1]).encode()
            next_level.append(hashlib.sha256(combined).hexdigest())

        level = next_level

    return level[0]


def audit_remote_node(base_url):
    ledger = requests.get(f"{base_url}/ledger", timeout=10).json()
    state = requests.get(f"{base_url}/state", timeout=10).json()
    root = requests.get(f"{base_url}/root", timeout=10).json()
    state_root = requests.get(f"{base_url}/state_root", timeout=10).json()

    valid, reason = validate_ledger_structure(ledger)

    replayed_state_root = replay_ledger(ledger) if valid else None
    recalculated_merkle_root = calculate_merkle_root(ledger) if valid else None

    remote_state_root = state_root.get("state_root")
    remote_merkle_root = root.get("root")
    packet_state_root = ledger[-1].get("state_root") if ledger else None

    state_root_match = (
        valid
        and replayed_state_root == remote_state_root
        and packet_state_root == replayed_state_root
    )

    merkle_root_match = valid and recalculated_merkle_root == remote_merkle_root

    consistent = valid and state_root_match and merkle_root_match

    return {
        "target": base_url,
        "ledger_size": state.get("ledger_size"),
        "last_hash": state.get("last_hash"),
        "remote_merkle_root": remote_merkle_root,
        "recalculated_merkle_root": recalculated_merkle_root,
        "merkle_root_match": merkle_root_match,
        "remote_state_root": remote_state_root,
        "replayed_state_root": replayed_state_root,
        "packet_state_root": packet_state_root,
        "state_root_match": state_root_match,
        "structure_valid": valid,
        "structure_reason": reason,
        "audit_result": "CONSISTENT" if consistent else "MISMATCH",
    }