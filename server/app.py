from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

logs = []

@app.route("/")
def home():
    total_logs = len(logs)
    unauthorized_count = sum(1 for log in logs if log.get("status") == "UNAUTHORIZED")
    sensitive_count = sum(1 for log in logs if log.get("sensitive") is True)

    return render_template(
        "dashboard.html",
        logs=list(reversed(logs)),
        total_logs=total_logs,
        unauthorized_count=unauthorized_count,
        sensitive_count=sensitive_count
    )

@app.route("/log", methods=["POST"])
def receive_log():
    data = request.get_json(force=True)

    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs.append(data)

    print("📥 Received Log:", data)
    return jsonify({"status": "success", "count": len(logs)}), 200

@app.route("/logs")
def get_logs():
    return jsonify(logs)

if __name__ == "__main__":
    app.run()
