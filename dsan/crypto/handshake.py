# crypto/handshake.py

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

class Handshake:
    def __init__(self):
        self.private_key = X25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def derive_shared_key(self, peer_public_key_bytes):
        peer_key = X25519PrivateKey.from_private_bytes(peer_public_key_bytes)
        shared = self.private_key.exchange(peer_key)

        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'dsan-handshake'
        )

        return hkdf.derive(shared)
