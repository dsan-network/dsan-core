import requests
from dsan.agent.agent import DSANAgent

agent = DSANAgent("alice")

# 🔗 pega último hash do node
res = requests.get("http://127.0.0.1:5001/last_hash").json()
prev_hash = res["last_hash"]

packet = agent.create_event(
    {"msg": "transfer_funds"},
    prev_hash
)

res = requests.post(
    "http://127.0.0.1:5001/receive",
    json=packet
)

print(res.json())