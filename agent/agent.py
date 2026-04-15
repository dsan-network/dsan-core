# agent/agent.py

from crypto.identity import Identity

class DSANAgent:
    def __init__(self, name):
        self.name = name
        self.identity = Identity()

    def sign_message(self, message: str):
        return self.identity.sign(message.encode())

    def get_public_key(self):
        return self.identity.serialize_public()
