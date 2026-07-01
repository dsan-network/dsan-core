import requests

NODE = "http://127.0.0.1:5001"

r = requests.get(f"{NODE}/root").json()

print("\n🌳 ROOT HASH")
print("Root:", r["root"])
print("Ledger size:", r["size"])