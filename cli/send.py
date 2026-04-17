import requests
from dsan.agent.agent import DSANAgent

# agentes locais
alice = DSANAgent("node2")   # quem envia
bob = DSANAgent("node1")     # quem recebe

payload = {
    "type": "TRANSFER",
    "value": 100
}

signature, envelope = alice.sign_message(
    payload,
    recipient_pub_keys=bob.totem.get_public_keys()
)

packet = {
    "envelope": envelope,
    "signature": signature,
    "sender_sig_pub": alice.totem.get_public_keys()["sig"]
}

res = requests.post("http://127.0.0.1:5001/receive", json=packet)

print(res.json())