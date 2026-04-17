import base64
from cryptography.hazmat.primitives.asymmetric import ed25519, x25519

class DSANTotem:
    def __init__(self):
        self.sig_private = ed25519.Ed25519PrivateKey.generate()
        self.enc_private = x25519.X25519PrivateKey.generate()
        self.unlock_gesture = [1, 2, 0]

    def verify_gesture(self, gesture):
        return gesture == self.unlock_gesture

    def sign(self, message: bytes):
        return base64.b64encode(self.sig_private.sign(message)).decode()

    def get_public_keys(self):
        return {
            "sig": base64.b64encode(
                self.sig_private.public_key().public_bytes_raw()
            ).decode(),
            "enc": base64.b64encode(
                self.enc_private.public_key().public_bytes_raw()
            ).decode()
        }
