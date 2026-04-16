# agent/agent.py

from dsan.crypto.identity import Identity

class Totem:
    def __init__(self, id):
        self.id = id
        self.unlocked = False

    def authenticate(self, gesture_code):
        if gesture_code == "valid":
            self.unlocked = True

    def authorize(self):
        return self.unlocked

class DSANAgent:
    def __init__(self, name, mode=None):
        self.name = name
        self.mode = mode
        self.totem = None

    def execute(self, action: str):
        if not hasattr(self, "totem") or not self.totem.is_authorized():
            raise Exception("Execution denied: Totem not authorized")

        return f"[EXECUTED] {action}"
        
    def sign_message(self, message: str):
        return self.identity.sign(message.encode())

    def get_public_key(self):
        return self.identity.serialize_public()
