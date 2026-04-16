import time
import base64

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature


class Totem:
    def __init__(self, public_key):
        self.public_key = public_key
        self.last_auth = None

    def verify_token(self, token):
        message = f"{token['totem_id']}:{token['timestamp']}:{token['nonce']}"

        try:
            signature = base64.b64decode(token['signature'])

            self.public_key.verify(
                signature,
                message.encode(),
                ec.ECDSA(hashes.SHA256())
            )

        except InvalidSignature:
            return False

        # validade de 10 segundos
        if abs(time.time() - token['timestamp']) > 10:
            return False

        self.last_auth = time.time()
        return True

    def is_authorized(self):
        if not self.last_auth:
            return False

        return (time.time() - self.last_auth) < 10