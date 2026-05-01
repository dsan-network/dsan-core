import requests
from dsan.core.replay import replay_ledger

NODE_URL = "http://127.0.0.1:5001"

ledger = requests.get(f"{NODE_URL}/ledger").json()
root_info = requests.get(f"{NODE_URL}/root").json()
state_info = requests.get(f"{NODE_URL}/state_root").json()
state_meta = requests.get(f"{NODE_URL}/state").json()

replayed_state_root = replay_ledger(ledger)
node_state_root = state_info["state_root"]

print("=== DSAN AUDIT REPORT ===")
print("ledger_size:", state_meta["ledger_size"])
print("last_hash:", state_meta["last_hash"])
print("merkle_root:", root_info["root"])
print("node_state_root:", node_state_root)
print("replayed_state_root:", replayed_state_root)

if ledger:
    last_entry = ledger[-1]
    packet_state_root = last_entry.get("state_root")
    print("packet_state_root:", packet_state_root)

    if packet_state_root is None:
        print("packet_state_root_check: MISSING")
    elif packet_state_root == replayed_state_root:
        print("packet_state_root_check: OK")
    else:
        print("packet_state_root_check: MISMATCH")
else:
    print("packet_state_root: EMPTY_LEDGER")

if node_state_root == replayed_state_root:
    print("audit_result: CONSISTENT")
else:
    print("audit_result: MISMATCH")