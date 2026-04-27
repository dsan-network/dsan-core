import hashlib
import json

class DSANState:

    def __init__(self):
        self.data = {}

    def apply(self, event):
        action = event["payload"].get("msg")

        # exemplo determinístico
        if action == "transfer_funds":
            self.data["last_action"] = "transfer"

        else:
            self.data["last_action"] = action

    def root(self):
        serialized = json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()