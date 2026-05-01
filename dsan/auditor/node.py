from flask import Flask, jsonify, request

from dsan.auditor.audit import audit_remote_node

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({"status": "auditor online"})


@app.route("/audit", methods=["GET"])
def audit():
    target = request.args.get("target")
    if not target:
        return jsonify({"status": "error", "error": "missing_target"}), 400

    try:
        report = audit_remote_node(target)
        return jsonify(report)
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)