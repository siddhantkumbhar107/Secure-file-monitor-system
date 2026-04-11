from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

logs = []

@app.route("/")
def home():
    return "🚀 Secure File Monitoring Server Running"

@app.route("/log", methods=["POST"])
def receive_log():
    data = request.json
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    logs.append(data)
    print("📥 Received Log:", data)

    return jsonify({"status": "success"})

@app.route("/logs")
def get_logs():
    return jsonify(logs)

if __name__ == "__main__":
    app.run()
