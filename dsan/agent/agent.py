import time
import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


class DSANAgent:
    def __init__(self, agent_id="agent"):
        self.agent_id = agent_id
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def create_event(self, payload, prev_hash):
        event = {
            "sender": self.agent_id,
            "payload": payload,
            "nonce": str(int(time.time() * 1000)),
            "prev_hash": prev_hash,
        }

        event_bytes = canonical_json(event).encode()
        signature = self.private_key.sign(event_bytes)
        event_hash = hashlib.sha256(event_bytes).hexdigest()

        return {
            "event": event,
            "hash": event_hash,
            "signature": signature.hex(),
            "sender_sig_pub": self.public_key.public_bytes_raw().hex(),
        }