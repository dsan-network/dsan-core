import requests
import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import ed25519

NODE = "http://127.0.0.1:5001"

def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'))

def verify_signature(pub_hex, sig_hex, message_bytes):
    pub = bytes.fromhex(pub_hex)
    sig = bytes.fromhex(sig_hex)

    pub_key = ed25519.Ed25519PublicKey.from_public_bytes(pub)
    pub_key.verify(sig, message_bytes)

def hash_event(event):
    return hashlib.sha256(canonical_json(event).encode()).hexdigest()

def audit():

    print("\n🔎 DSAN AUDIT START\n")

    # ------------------------
    # 1. BAIXA LEDGER
    # ------------------------
    try:
        ledger = requests.get(f"{NODE}/ledger").json()
    except Exception as e:
        print("❌ Não conseguiu obter ledger:", e)
        return

    if not ledger:
        print("⚠️ Ledger vazio")
        return

    prev_hash_expected = "0" * 64

    # ------------------------
    # 2. VERIFICA CADEIA
    # ------------------------
    for index, entry in enumerate(ledger):

        print(f"\n🔹 EVENT {index}")

        event = entry["event"]
        stored_hash = entry["hash"]
        validators = entry.get("validators", [])

        # ------------------------
        # HASH
        # ------------------------
        computed_hash = hash_event(event)

        if computed_hash != stored_hash:
            print("❌ HASH INVÁLIDO")
            return
        else:
            print("✔ Hash válido")

        # ------------------------
        # CHAIN
        # ------------------------
        if event["prev_hash"] != prev_hash_expected:
            print("❌ QUEBRA DE CADEIA")
            print("Esperado:", prev_hash_expected)
            print("Recebido:", event["prev_hash"])
            return
        else:
            print("✔ Cadeia consistente")

        prev_hash_expected = stored_hash

        # ------------------------
        # VALIDATORS
        # ------------------------
        if not validators:
            print("❌ Sem validadores")
            return

        print(f"✔ {len(validators)} assinaturas encontradas")

        for v in validators:
            try:
                verify_signature(
                    v["pub"],
                    v["sig"],
                    stored_hash.encode()
                )
            except Exception as e:
                print("❌ Assinatura inválida:", v)
                return

        print("✔ Assinaturas válidas")

    print("\n✅ AUDIT OK — LEDGER ÍNTEGRO\n")

if __name__ == "__main__":
    audit()