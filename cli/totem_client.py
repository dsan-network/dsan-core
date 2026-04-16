import requests
import base64
import time
from identity import load_or_create
from cryptography.hazmat.primitives import serialization

key = load_or_create()
public_key = key.public_key()

def sign(message: bytes):
    signature = key.sign(message)
    return base64.b64encode(signature).decode()

def get_public_key():
    return base64.b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    ).decode()

def send(action):
    nonce = str(int(time.time() * 1000))

    message = f"{action}:{nonce}".encode()

    payload = {
        "action": action,
        "nonce": nonce,
        "signature": sign(message),
        "public_key": get_public_key()
    }

    print("PAYLOAD:", payload)  # útil pro teste

    res = requests.post(
        "http://127.0.0.1:8000/execute",
        json=payload
    )

    print(res.json())

if __name__ == "__main__":
    send("transfer_funds")