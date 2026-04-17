import base64
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

def derive_shared_key(priv, peer_pub_bytes):
    peer = x25519.X25519PublicKey.from_public_bytes(peer_pub_bytes)
    shared = priv.exchange(peer)

    key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"dsan-v2"
    ).derive(shared)

    return base64.urlsafe_b64encode(key)

def encrypt(key, data: dict):
    return Fernet(key).encrypt(str(data).encode()).decode()

def decrypt(key, token: str):
    return Fernet(key).decrypt(token.encode()).decode()
