# agent/agent.py

from crypto.identity import Identity

class DSANAgent:
    def __init__(self, name, mode="hybrid"):
        self.name = name
        self.mode = mode  # off-cloud | on-cloud | hybrid

    def sign_message(self, message: str):
        return self.identity.sign(message.encode())

    def get_public_key(self):
        return self.identity.serialize_public()
