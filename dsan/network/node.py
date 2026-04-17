import sys
from flask import Flask, request, jsonify
from dsan.agent.agent import DSANAgent

app = Flask(__name__)

agent_name = sys.argv[1] if len(sys.argv) > 1 else "node"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 5001

agent = DSANAgent(agent_name)


@app.route("/")
def home():
    return f"DSAN node {agent.id} online"


@app.route("/receive", methods=["POST"])
def receive():
    data = request.get_json()

    if not data:
        return jsonify({"error": "invalid"}), 400

    ok = agent.receive(
        data["envelope"],
        data["signature"],
        data["sender_sig_pub"]
    )

    if ok:
        print(f"\n✔ Mensagem validada por {agent.id}")
        return jsonify({"status": "accepted"})
    else:
        print(f"\n❌ Falha criptográfica")
        return jsonify({"status": "rejected"}), 403


if __name__ == "__main__":
    print(f"\n🛡️ DSAN NODE {agent_name} na porta {port}")
    app.run(host="127.0.0.1", port=port)