import requests
from dsan.agent.agent import DSANAgent

NODE_URL = "http://127.0.0.1:5001"

agent = DSANAgent("alice")

state = requests.get(f"{NODE_URL}/state").json()
prev_hash = state["last_hash"]

packet = agent.create_event(
    {
        "type": "transfer",
        "from": "alice",
        "to": "bob",
        "amount": 10
    },
    prev_hash
)

response = requests.post(f"{NODE_URL}/receive", json=packet)

print("status:", response.status_code)
print("body:", response.json())