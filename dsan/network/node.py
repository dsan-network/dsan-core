import os
import sys
import json
import hashlib
import requests

from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from dsan.crypto.merkle import merkle_root
from dsan.crypto.validator import Validator
from dsan.core.context import ExecutionContext
from dsan.core.replay import replay_ledger
from dsan.epl.policy import DSANPolicy
from dsan.totem.totem import DSANTotem

app = Flask(__name__)

# ------------------------
# INIT
# ------------------------

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
    global ledger, seen_hashes, seen_nonces

    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "r", encoding="utf-8") as f:
            ledger = json.load(f)

        seen_hashes = {entry["hash"] for entry in ledger if "hash" in entry}
        seen_nonces = {
            entry["event"]["nonce"]
            for entry in ledger
            if "event" in entry and isinstance(entry["event"], dict) and "nonce" in entry["event"]
        }


def save_ledger():
    with open(LEDGER_FILE, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def hash_event(event):
    return hashlib.sha256(canonical_json(event).encode()).hexdigest()


def compute_root():
    hashes = [entry["hash"] for entry in ledger if "hash" in entry]
    return merkle_root(hashes)


def last_hash():
    if not ledger:
        return "0" * 64
    return ledger[-1]["hash"]


# ------------------------
# VALIDATORS
# ------------------------

def validate_validators(entry):
    validators = entry.get("validators", [])

    if not isinstance(validators, list) or not validators:
        return False

    h = entry["hash"].encode()

    for v in validators:
        try:
            if not isinstance(v, dict):
                return False

            if not all(k in v for k in ("node", "pub", "sig")):
                return False

            pub = bytes.fromhex(v["pub"])
            sig = bytes.fromhex(v["sig"])

            key = Ed25519PublicKey.from_public_bytes(pub)
            key.verify(sig, h)
        except Exception:
            return False

    return True


def validate_incoming_ledger(incoming_ledger):
    if not isinstance(incoming_ledger, list):
        return False, "ledger_not_list"

    prev_hash = "0" * 64

    for i, entry in enumerate(incoming_ledger):
        if not isinstance(entry, dict):
            return False, f"invalid_entry_type_at_{i}"

        if "event" not in entry or "hash" not in entry:
            return False, f"missing_fields_at_{i}"

        event = entry["event"]
        if not isinstance(event, dict):
            return False, f"invalid_event_type_at_{i}"

        if "prev_hash" not in event:
            return False, f"missing_prev_hash_at_{i}"

        if "state_root" not in entry:
            return False, f"missing_state_root_at_{i}"

        stored_hash = entry["hash"]

        if hash_event(event) != stored_hash:
            return False, f"invalid_hash_at_{i}"

        if event["prev_hash"] != prev_hash:
            return False, f"fork_detected_at_{i}"

        if not validate_validators(entry):
            return False, f"invalid_validators_at_{i}"

        prev_hash = stored_hash

    return True, "ok"


# ------------------------
# STATUS
# ------------------------

@app.route("/")
def home():
    return jsonify({"status": f"{NODE_ID} online"})


@app.route("/state")
def state():
    return jsonify({
        "ledger_size": len(ledger),
        "last_hash": last_hash()
    })


@app.route("/root")
def root():
    return jsonify({
        "root": compute_root(),
        "size": len(ledger)
    })


@app.route("/state_root")
def get_state_root():
    return jsonify({
        "state_root": replay_ledger(ledger)
    })


@app.route("/ledger")
def get_ledger():
    return jsonify(ledger)


# ------------------------
# VOTE
# ------------------------

@app.route("/vote", methods=["POST"])
def vote():
    data = request.get_json()
    if not data:
        return jsonify({"vote": "NO", "reason": "invalid_json"}), 400

    try:
        required = ["event", "hash", "signature", "sender_sig_pub"]
        if not all(k in data for k in required):
            return jsonify({"vote": "NO", "reason": "missing_fields"}), 400

        event = data["event"]
        signature = bytes.fromhex(data["signature"])
        pub = bytes.fromhex(data["sender_sig_pub"])

        if not isinstance(event, dict):
            return jsonify({"vote": "NO", "reason": "invalid_event"}), 400

        if "nonce" not in event:
            return jsonify({"vote": "NO", "reason": "missing_nonce"}), 400

        if "prev_hash" not in event:
            return jsonify({"vote": "NO", "reason": "missing_prev_hash"}), 400

        if event["nonce"] in seen_nonces:
            return jsonify({"vote": "NO", "reason": "replay"})

        pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub)
        pub_key.verify(signature, canonical_json(event).encode())

        if hash_event(event) != data["hash"]:
            return jsonify({"vote": "NO", "reason": "tamper"})

        if event["prev_hash"] != last_hash():
            return jsonify({"vote": "NO", "reason": "chain_mismatch"})

        decision = DSANPolicy.evaluate(event)
        if not decision["allowed"]:
            return jsonify({"vote": "NO", "reason": "policy_block"})

        return jsonify({"vote": "YES"})

    except Exception as e:
        return jsonify({"vote": "NO", "reason": str(e)}), 400


# ------------------------
# RECEIVE
# ------------------------

@app.route("/receive", methods=["POST"])
def receive():
    global ledger

    data = request.get_json()
    if not data:
        return jsonify({"status": "invalid_json"}), 400

    try:
        required = ["event", "hash", "signature", "sender_sig_pub"]
        if not all(k in data for k in required):
            return jsonify({"status": "missing_fields"}), 400

        event = data["event"]
        event_hash = data["hash"]

        if not isinstance(event, dict):
            return jsonify({"status": "invalid_event"}), 400

        if hash_event(event) != event_hash:
            return jsonify({"status": "tampered_event"}), 400

        if event_hash in seen_hashes:
            return jsonify({"status": "duplicate"}), 403

        # SELF VOTE
        self_vote = requests.post(
            f"http://127.0.0.1:{PORT}/vote",
            json=data,
            timeout=2
        ).json()

        if self_vote.get("vote") != "YES":
            return jsonify({
                "status": "rejected_local",
                "reason": self_vote.get("reason")
            }), 403

        # PEERS
        votes = 1
        total = len(PEERS) + 1

        for peer in PEERS:
            try:
                r = requests.post(f"{peer}/vote", json=data, timeout=2).json()
                if r.get("vote") == "YES":
                    votes += 1
            except Exception:
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

        # STATE ROOT
        temp_ledger = ledger + [{
            "event": event,
            "hash": event_hash,
            "validators": [{
                "node": NODE_ID,
                "pub": validator.pub_hex(),
                "sig": validator.sign(event_hash.encode())
            }],
            "result": result,
            "state_root": ""
        }]
        state_root = replay_ledger(temp_ledger)

        # VALIDATORS
        validators = [{
            "node": NODE_ID,
            "pub": validator.pub_hex(),
            "sig": validator.sign(event_hash.encode())
        }]

        for peer in PEERS:
            try:
                r = requests.post(
                    f"{peer}/sign",
                    json={"hash": event_hash},
                    timeout=2
                ).json()

                if all(k in r for k in ("node", "pub", "sig")):
                    validators.append(r)
            except Exception:
                pass

        # PACKET FINAL
        packet = {
            "event": event,
            "hash": event_hash,
            "validators": validators,
            "result": result,
            "state_root": state_root
        }

        ledger.append(packet)
        save_ledger()

        seen_hashes.add(event_hash)
        if "nonce" in event:
            seen_nonces.add(event["nonce"])

        print(f"✔ {NODE_ID} executou")
        print(f"🌳 MERKLE ROOT: {compute_root()}")
        print(f"🧠 STATE ROOT: {state_root}")

        broadcast_sync()

        return jsonify({
            "status": "executed",
            "hash": event_hash,
            "state_root": state_root
        })

    except Exception as e:
        print("Erro:", e)
        return jsonify({"status": "error", "error": str(e)}), 400


# ------------------------
# SIGN
# ------------------------

@app.route("/sign", methods=["POST"])
def sign():
    data = request.get_json()
    if not data:
        return jsonify({"status": "invalid_json"}), 400

    h = data.get("hash")
    if not h:
        return jsonify({"status": "missing_hash"}), 400

    sig = validator.sign(h.encode())

    return jsonify({
        "node": NODE_ID,
        "pub": validator.pub_hex(),
        "sig": sig
    })


# ------------------------
# SYNC
# ------------------------

@app.route("/sync", methods=["POST"])
def sync():
    global ledger, seen_hashes, seen_nonces

    data = request.get_json()
    if not data:
        return jsonify({"status": "invalid_json"}), 400

    incoming_ledger = data.get("ledger", [])
    incoming_root_advertised = data.get("root")

    if not incoming_ledger:
        return jsonify({"status": "empty"}), 400

    ok, reason = validate_incoming_ledger(incoming_ledger)
    if not ok:
        return jsonify({"status": reason}), 400

    calculated_state_root = replay_ledger(incoming_ledger)
    advertised_state_root = incoming_ledger[-1].get("state_root")

    if calculated_state_root != advertised_state_root:
        return jsonify({"status": "invalid_state"}), 400

    incoming_root = merkle_root([entry["hash"] for entry in incoming_ledger])
    local_root = merkle_root([entry["hash"] for entry in ledger])

    if incoming_root_advertised and incoming_root != incoming_root_advertised:
        return jsonify({"status": "invalid_root"}), 400

    if incoming_root == local_root:
        return jsonify({"status": "already_synced"}), 200

    if len(incoming_ledger) > len(ledger):
        ledger = incoming_ledger
        save_ledger()

        seen_hashes = {entry["hash"] for entry in ledger if "hash" in entry}
        seen_nonces = {
            entry["event"]["nonce"]
            for entry in ledger
            if "event" in entry and isinstance(entry["event"], dict) and "nonce" in entry["event"]
        }

        print("🔄 Ledger substituído")
        return jsonify({
            "status": "synced",
            "state_root": calculated_state_root,
            "root": incoming_root
        }), 200

    return jsonify({"status": "ignored_shorter_chain"}), 200


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