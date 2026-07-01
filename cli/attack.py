import requests
import copy
from dsan.agent.agent import DSANAgent

alice = DSANAgent("alice")

packet = alice.create_event({"msg": "attack_test"})

url = "http://127.0.0.1:5001/receive"

print("\n--- ENVIO LEGÍTIMO ---")
print(requests.post(url, json=packet).json())

print("\n--- REPLAY ATTACK ---")
print(requests.post(url, json=packet).json())

print("\n--- TAMPER ATTACK ---")
tampered = copy.deepcopy(packet)
tampered["event"]["payload"]["msg"] = "HACKED"

print(requests.post(url, json=tampered).json())