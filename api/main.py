from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

app = FastAPI()
used_nonces = set()


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

    if req.nonce in used_nonces:
        raise HTTPException(status_code=403, detail="Replay attack detected")

    try:
        pub = Ed25519PublicKey.from_public_bytes(
            base64.b64decode(req.public_key)
        )

        message = f"{req.action}:{req.nonce}".encode()

        pub.verify(base64.b64decode(req.signature), message)

    except Exception:
        raise HTTPException(status_code=403, detail="Invalid signature")

    used_nonces.add(req.nonce)

    return {
        "status": "authorized",
        "result": f"[EXECUTED] {req.action}",
    }