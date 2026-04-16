from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

app = FastAPI()

used_nonces = {}

AUTHORIZED_TOTEMS = {
    "5sGlTyDMJo2Zuhn9kP/5OHw7WNbdVJbdvzGB2hSFpbw="
}

MAX_NONCES = 1000


class RequestModel(BaseModel):
    action: str
    nonce: str
    signature: str
    public_key: str


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/execute")
def execute(req: RequestModel):

    # 🔐 valida se totem é autorizado
    if req.public_key not in AUTHORIZED_TOTEMS:
        raise HTTPException(status_code=403, detail="Unauthorized totem")

    # 🔐 controle de nonce por identidade
    user_nonces = used_nonces.setdefault(req.public_key, set())

    if req.nonce in user_nonces:
        raise HTTPException(status_code=403, detail="Replay attack detected")

    try:
        public_key_bytes = base64.b64decode(req.public_key)
        signature_bytes = base64.b64decode(req.signature)

        pub = Ed25519PublicKey.from_public_bytes(public_key_bytes)

        message = f"{req.action}:{req.nonce}".encode()

        pub.verify(signature_bytes, message)

    except Exception:
        raise HTTPException(status_code=403, detail="Invalid signature")

    # registra nonce
    user_nonces.add(req.nonce)

    # controle de memória
    if len(user_nonces) > MAX_NONCES:
        user_nonces.pop()

    return {
        "status": "authorized",
        "result": f"[EXECUTED] {req.action}"
    }