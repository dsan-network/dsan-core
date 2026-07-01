from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

class Validator:

    def __init__(self):
        self._private = ed25519.Ed25519PrivateKey.generate()
        self._public = self._private.public_key()

    def sign(self, data: bytes):
        return self._private.sign(data).hex()

    def pub_hex(self):
        return self._public.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()