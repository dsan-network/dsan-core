import base64
from dsan.crypto.identity import DSANTotem
from dsan.crypto.handshake import derive_shared_key, encrypt, decrypt

class DSANAgent:
    def __init__(self, agent_id):
        self.id = agent_id
        self.totem = DSANTotem()

    def create_message(self, payload: dict, receiver_enc_pub=None):
        data = str(payload)
        encrypted = False

        if receiver_enc_pub:
            key = derive_shared_key(
                self.totem.enc_private,
                base64.b64decode(receiver_enc_pub)
            )
            data = encrypt(key, payload)
            encrypted = True

        message = data.encode()
        signature = self.totem.sign(message)

        return {
            "sender": self.id,
            "payload": data,
            "encrypted": encrypted,
            "signature": signature,
            "pub_keys": self.totem.get_public_keys()
        }

    def receive(self, msg):
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        try:
            pub = Ed25519PublicKey.from_public_bytes(
                base64.b64decode(msg["pub_keys"]["sig"])
            )

            pub.verify(
                base64.b64decode(msg["signature"]),
                msg["payload"].encode()
            )

            if msg["encrypted"]:
                key = derive_shared_key(
                    self.totem.enc_private,
                    base64.b64decode(msg["pub_keys"]["enc"])
                )
                data = decrypt(key, msg["payload"])
            else:
                data = msg["payload"]

            return True, data

        except Exception:
            return False, None
