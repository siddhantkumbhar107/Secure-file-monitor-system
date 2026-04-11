from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

logs = []

@app.route("/")
def home():
    html = """
    <html>
    <head>
        <title>Secure File Monitoring Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 30px;
                background: #f4f6f8;
            }
            h1 {
                color: #222;
            }
            .card {
                background: white;
                padding: 15px;
                margin-bottom: 12px;
                border-radius: 10px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            }
            .empty {
                color: #666;
                font-size: 18px;
            }
            .meta {
                color: #444;
                margin-top: 8px;
            }
        </style>
    </head>
    <body>
        <h1>🚀 Secure File Monitoring Dashboard</h1>
    """

    if not logs:
        html += '<p class="empty">No logs received yet.</p>'
    else:
        for log in reversed(logs):
            html += f"""
            <div class="card">
                <b>Event:</b> {log.get('event', '')}<br>
                <b>File:</b> {log.get('file', '')}<br>
                <b>User:</b> {log.get('user', '')}<br>
                <b>Status:</b> {log.get('status', '')}<br>
                <b>Hash:</b> {log.get('hash', '')}<br>
                <div class="meta"><b>Timestamp:</b> {log.get('timestamp', '')}</div>
            </div>
            """

    html += """
    </body>
    </html>
    """
    return html


@app.route("/log", methods=["POST"])
def receive_log():
    data = request.json or {}
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logs.append(data)
    print("📥 Received Log:", data)
    return jsonify({"status": "success"}), 200


@app.route("/logs")
def get_logs():
    return jsonify(logs)


if __name__ == "__main__":
    app.run()
