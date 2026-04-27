import os
import sys
import json
import hashlib
import requests
from flask import Flask, request, jsonify
from dsan.crypto.merkle import merkle_root
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from dsan.crypto.validator import Validator
from dsan.core.context import ExecutionContext
from dsan.epl.policy import DSANPolicy
from dsan.totem.totem import DSANTotem
from dsan.core.replay import replay_ledger
from dsan.core.state import DSANState

# ------------------------
# INIT (ordem correta)
# ------------------------

app = Flask(__name__)

NODE_ID = sys.argv[1]
PORT = int(sys.argv[2])
PEERS = sys.argv[3:] if len(sys.argv) > 3 else []

LEDGER_FILE = f"ledger_{NODE_ID}.json"

context = ExecutionContext(PEERS)
totem = DSANTotem()

validator = Validator()
ledger = []
seen_hashes = set()
seen_nonces = set()

# ------------------------
# UTILS
# ------------------------

def load_ledger():
    global ledger
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r") as f:
            ledger = json.load(f)

def save_ledger():
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)

def compute_root():
    hashes = [entry["hash"] for entry in ledger]
    return merkle_root(hashes)

def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

def hash_event(event):
    return hashlib.sha256(canonical_json(event).encode()).hexdigest()

def last_hash():
    if not ledger:
        return "0" * 64
    return ledger[-1]["hash"]

# ------------------------
# VALIDATORS CHECK
# ------------------------

def validate_validators(entry):
    h = entry["hash"].encode()

    for v in entry.get("validators", []):
        try:
            pub = bytes.fromhex(v["pub"])
            sig = bytes.fromhex(v["sig"])

            key = Ed25519PublicKey.from_public_bytes(pub)
            key.verify(sig, h)

        except Exception:
            return False

    return True

# ------------------------
# STATUS
# ------------------------

@app.route('/state_root')
def get_state_root():
    return jsonify({
        "state_root": replay_ledger(ledger)
    })

@app.route('/')
def home():
    return jsonify({"status": f"{NODE_ID} online"})

@app.route('/state')
def state():
    return jsonify({
        "ledger_size": len(ledger),
        "last_hash": last_hash()
    })

@app.route('/last_hash')
def get_last_hash():
    return jsonify({"last_hash": last_hash()})

@app.route('/root')
def root():
    return jsonify({
        "root": compute_root(),
        "size": len(ledger)
    })

# ------------------------
# VOTE
# ------------------------

@app.route('/vote', methods=['POST'])
def vote():
    data = request.get_json()

    try:
        event = data["event"]
        signature = bytes.fromhex(data["signature"])
        pub = bytes.fromhex(data["sender_sig_pub"])

        if event["nonce"] in seen_nonces:
            return jsonify({"vote": "NO", "reason": "replay"})

        pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub)
        pub_key.verify(signature, canonical_json(event).encode())

        if hash_event(event) != data["hash"]:
            return jsonify({"vote": "NO", "reason": "tamper"})

        if event["prev_hash"] != last_hash():
            return jsonify({
                "vote": "NO",
                "reason": "chain_mismatch",
                "expected": last_hash()
            })

        decision = DSANPolicy.evaluate(event)
        if not decision["allowed"]:
            return jsonify({"vote": "NO", "reason": "policy_block"})

        return jsonify({"vote": "YES"})

    except Exception as e:
        return jsonify({"vote": "NO", "reason": str(e)})

# ------------------------
# RECEIVE
# ------------------------

@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()

    try:
        event = data["event"]
        event_hash = data["hash"]

        if event_hash in seen_hashes:
            return jsonify({"status": "duplicate"}), 403

        # SELF VOTE
        self_vote = requests.post(
            f"http://127.0.0.1:{PORT}/vote",
            json=data
        ).json()

        if self_vote["vote"] != "YES":
            return jsonify({"status": "rejected_local"}), 403

        # PEER VOTES
        votes = 1
        total = len(PEERS) + 1

        for peer in PEERS:
            try:
                r = requests.post(f"{peer}/vote", json=data, timeout=2).json()
                if r.get("vote") == "YES":
                    votes += 1
            except:
                print("⚠️ Peer offline:", peer)

        print(f"🗳️ Votes: {votes}/{total}")

        if votes <= total // 2:
            return jsonify({"status": "consensus_failed"}), 403

        print("✔ CONSENSO ALCANÇADO")

        # TOTEM
        print("🔐 Totem requerido")
        if not totem.authorize():
            return jsonify({"status": "totem_denied"}), 403

        # EXECUÇÃO
        result = f"[EXECUTED] {event['payload']}"

        # ASSINATURAS
        validator_sig = validator.sign(event_hash.encode())

        validators = [{
            "node": NODE_ID,
            "pub": validator.pub_hex(),
            "sig": validator_sig
        }]

        for peer in PEERS:
            try:
                r = requests.post(f"{peer}/sign", json={"hash": event_hash}).json()
                validators.append(r)
            except:
                pass

        # SALVAR
        packet = {
            "event": event,
            "hash": event_hash,
            "validators": validators,
            "result": result
        }

        ledger.append(packet)
        save_ledger()

        seen_hashes.add(event_hash)
        seen_nonces.add(event["nonce"])

        print(f"✔ {NODE_ID} executou")
        print(f"🌳 MERKLE ROOT: {compute_root()}")

        broadcast_sync()

        return jsonify({
            "status": "executed",
            "hash": event_hash
        })

    except Exception as e:
        print("Erro:", e)
        return jsonify({"status": "error", "error": str(e)}), 400

state = DSANState()

for entry in ledger:
    state.apply(entry["event"])

state_root = state.root()

packet["state_root"] = state_root

# ------------------------
# SIGN
# ------------------------

@app.route('/sign', methods=['POST'])
def sign():
    data = request.get_json()
    h = data["hash"]

    sig = validator.sign(h.encode())

    return jsonify({
        "node": NODE_ID,
        "pub": validator.pub_hex(),
        "sig": sig
    })

# ------------------------
# SYNC
# ------------------------

@app.route('/sync', methods=['POST'])
def sync():
    global ledger

    try:
        data = request.get_json()

        incoming_ledger = data.get("ledger", [])
        incoming_root = data.get("root")

        if not incoming_ledger:
            return jsonify({"status": "empty"}), 400

        if incoming_root == compute_root():
            return jsonify({"status": "already_synced"})

        prev_hash = "0" * 64

        for entry in incoming_ledger:
            if not validate_validators(entry):
                return jsonify({"status": "invalid_validators"}), 400

            event = entry["event"]
            stored_hash = entry["hash"]

            if hash_event(event) != stored_hash:
                return jsonify({"status": "invalid_hash"}), 400

            if event["prev_hash"] != prev_hash:
                return jsonify({"status": "fork_detected"}), 400

            prev_hash = stored_hash

        if len(incoming_ledger) > len(ledger):
            ledger = incoming_ledger
            save_ledger()
            print("🔄 Ledger substituído")
        
        return jsonify({"status": "synced"})

        calculated_root = replay_ledger(incoming_ledger)

        if any("state_root" not in e for e in incoming_ledger):
        return jsonify({"status": "missing_state_root"}), 400

        last_state_root = incoming_ledger[-1]["state_root"]

if calculated_root != last_state_root:
    return jsonify({"status": "invalid_state"}), 400

    except Exception as e:
        print("❌ Sync erro:", e)
        return jsonify({"status": "error", "error": str(e)}), 400

# ------------------------
# BROADCAST
# ------------------------

def broadcast_sync():
    packet = {
        "ledger": ledger,
        "root": compute_root()
    }

    for peer in PEERS:
        try:
            requests.post(f"{peer}/sync", json=packet, timeout=1)
        except Exception as e:
            print("Erro sync:", e)

# ------------------------

if __name__ == "__main__":
    load_ledger()

    print(f"\n🛡️ NODE {NODE_ID} | PORT {PORT}")
    print(f"🔗 Peers: {PEERS}")
    print(f"🌐 Modo: {context.mode}\n")

    app.run(host="127.0.0.1", port=PORT)