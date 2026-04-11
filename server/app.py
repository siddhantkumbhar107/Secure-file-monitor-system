from flask import Flask, jsonify, render_template
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")


def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)


def load_logs():
    ensure_log_file()
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print("Error reading logs:", e)
        return []


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/api/logs")
def get_logs():
    logs = load_logs()
    return jsonify(logs)


@app.route("/api/stats")
def get_stats():
    logs = load_logs()

    stats = {
        "total_logs": len(logs),
        "usb_inserted": sum(1 for log in logs if log.get("event") == "USB_INSERTED"),
        "usb_removed": sum(1 for log in logs if log.get("event") == "USB_REMOVED"),
        "files_copied_to_usb": sum(1 for log in logs if log.get("event") == "FILE_COPIED_TO_USB"),
        "files_received_from_usb": sum(1 for log in logs if log.get("event") == "FILE_RECEIVED_FROM_USB"),
        "unauthorized_events": sum(1 for log in logs if log.get("status") == "UNAUTHORIZED")
    }

    return jsonify(stats)


if __name__ == "__main__":
    print("Reading logs from:", LOG_FILE)
    app.run(debug=True)
