import hashlib
import json


class DSANState:
    def __init__(self):
        self.data = {}

    def apply(self, event):
        payload = event.get("payload", {})
        action = payload.get("type")

        if action == "transfer":
            sender = payload["from"]
            receiver = payload["to"]
            amount = payload["amount"]

            self.data[sender] = self.data.get(sender, 0) - amount
            self.data[receiver] = self.data.get(receiver, 0) + amount
        else:
            self.data["last_action"] = payload

    def root(self):
        serialized = json.dumps(self.data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode()).hexdigest()