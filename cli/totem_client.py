import time
import base64
import json
import requests

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

API_URL = "http://localhost:8000/execute"


class DSANClient:
    def __init__(self):
        self.private_key = Ed25519PrivateKey.generate()
        self.public_key = base64.b64encode(
            self.private_key.public_key().public_bytes_raw()
        ).decode()

    def sign(self, message: bytes) -> str:
        signature = self.private_key.sign(message)
        return base64.b64encode(signature).decode()

    def build_payload(self, action, nonce=None):
        if not nonce:
            nonce = str(int(time.time() * 1000))

        message = f"{action}:{nonce}".encode()
        signature = self.sign(message)

        payload = {
            "action": action,
            "nonce": nonce,
            "signature": signature,
            "public_key": self.public_key
        }

        return payload

    def send(self, payload):
        try:
            res = requests.post(API_URL, json=payload)
            print("➡️ PAYLOAD:", payload)
            print("⬅️ RESPONSE:", res.status_code, res.text)
            print("-" * 60)
        except Exception as e:
            print("❌ ERRO:", e)


# =========================
# TESTES DE ATAQUE
# =========================

def test_normal(client):
    print("\n✅ TESTE NORMAL")
    payload = client.build_payload("transfer_funds")
    client.send(payload)


def test_replay(client):
    print("\n🔁 TESTE REPLAY ATTACK")

    payload = client.build_payload("transfer_funds")
    client.send(payload)

    print("♻️ Reenviando mesmo payload...")
    client.send(payload)  # mesmo nonce → deve falhar


def test_tamper(client):
    print("\n🧨 TESTE TAMPERING")

    payload = client.build_payload("transfer_funds")

    # altera ação sem recalcular assinatura
    payload["action"] = "hack_attempt"

    client.send(payload)


def test_invalid_signature(client):
    print("\n❌ TESTE ASSINATURA INVÁLIDA")

    payload = client.build_payload("transfer_funds")

    # corrompe assinatura
    payload["signature"] = payload["signature"][:-2] + "AA"

    client.send(payload)


def test_fake_key(client):
    print("\n🕵️ TESTE CHAVE FALSA")

    payload = client.build_payload("transfer_funds")

    # troca chave pública sem mudar assinatura
    payload["public_key"] = base64.b64encode(b"fake_key_12345678901234567890").decode()

    client.send(payload)


# =========================
# EXECUÇÃO
# =========================

if __name__ == "__main__":
    client = DSANClient()

    test_normal(client)
    test_replay(client)
    test_tamper(client)
    test_invalid_signature(client)
    test_fake_key(client)