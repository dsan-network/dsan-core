from fastapi import FastAPI
from pydantic import BaseModel

from dsan.agent.agent import DSANAgent
from dsan.core.engine import execute

app = FastAPI()
agent = DSANAgent("node_1")

class Message(BaseModel):
    sender: str
    payload: str
    encrypted: bool
    signature: str
    pub_keys: dict

@app.get("/")
def root():
    return {"status": "DSAN node online"}

@app.post("/receive")
def receive(msg: Message):
    valid, data = agent.receive(msg.dict())

    if not valid:
        return {"status": "rejected"}

    result = execute(data)

    return {
        "status": "accepted",
        "result": result
    }
