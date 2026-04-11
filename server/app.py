from flask import Flask, jsonify, render_template
import json
import os

app = Flask(__name__)
LOG_FILE = "logs.json"


def load_logs():
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/logs")
def get_logs():
    return jsonify(load_logs())


@app.route("/api/stats")
def get_stats():
    logs = load_logs()

    stats = {
        "total_logs": len(logs),
        "usb_inserted": sum(1 for log in logs if log.get("event") == "USB_INSERTED"),
        "usb_removed": sum(1 for log in logs if log.get("event") == "USB_REMOVED"),
        "files_copied_to_usb": sum(1 for log in logs if log.get("event") == "FILE_COPIED_TO_USB"),
        "files_received_from_usb": sum(1 for log in logs if log.get("event") == "FILE_RECEIVED_FROM_USB"),
        "files_created": sum(1 for log in logs if log.get("event") == "FILE_CREATED"),
        "files_deleted": sum(1 for log in logs if log.get("event") == "FILE_DELETED"),
        "unauthorized_events": sum(1 for log in logs if log.get("status") == "UNAUTHORIZED")
    }

    return jsonify(stats)


if __name__ == "__main__":
    app.run(debug=True)
