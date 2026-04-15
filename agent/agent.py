# agent/agent.py

from crypto.identity import Identity

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
    def __init__(self, name, totem):
        self.name = name
        self.totem = totem

    def execute(self, action):
        if not self.totem.authorize():
            raise Exception("Execution denied: Totem not authorized")

        return f"Executing {action}"
        
    def sign_message(self, message: str):
        return self.identity.sign(message.encode())

    def get_public_key(self):
        return self.identity.serialize_public()
