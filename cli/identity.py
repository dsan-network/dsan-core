import os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

KEY_PATH = "totem.key"

def load_or_create():
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    
    key = Ed25519PrivateKey.generate()
    
    with open(KEY_PATH, "wb") as f:
        f.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )
    
    return key