# main.py

from agent.agent import DSANAgent
from network.transport import send_message

alice = DSANAgent("alice")

message = "Hello DSAN"
signature = alice.sign_message(message)

payload = {
    "sender": "alice",
    "message": message,
    "signature": signature.hex()
}

send_message("localhost", 5000, payload)
