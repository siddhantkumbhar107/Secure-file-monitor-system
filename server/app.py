from flask import Flask
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")


def load_logs():
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        return [{
            "timestamp": "-",
            "event": "READ_ERROR",
            "source": "-",
            "destination": "-",
            "file_name": "-",
            "user": "-",
            "status": "ERROR",
            "file_size": 0,
            "hash": "-",
            "alert": str(e)
        }]


@app.route("/")
def dashboard():
    logs = load_logs()

    total_logs = len(logs)
    usb_inserted = sum(1 for log in logs if log.get("event") == "USB_INSERTED")
    files_created = sum(1 for log in logs if log.get("event") == "FILE_CREATED")
    files_deleted = sum(1 for log in logs if log.get("event") == "FILE_DELETED")
    unauthorized = sum(1 for log in logs if log.get("status") == "UNAUTHORIZED")

    rows = ""
    if logs:
        for log in logs:
            rows += f"""
            <tr>
                <td>{log.get('timestamp', '-')}</td>
                <td>{log.get('event', '-')}</td>
                <td>{log.get('source', '-')}</td>
                <td>{log.get('destination', '-')}</td>
                <td>{log.get('file_name', '-')}</td>
                <td>{log.get('user', '-')}</td>
                <td>{log.get('status', '-')}</td>
                <td>{log.get('file_size', 0)}</td>
                <td>{log.get('hash', '-')}</td>
                <td>{log.get('alert', '-')}</td>
            </tr>
            """
    else:
        rows = """
        <tr>
            <td colspan="10">No logs found</td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="5">
        <title>Secure File Monitoring Dashboard</title>
        <style>
            * {{
                box-sizing: border-box;
                font-family: Arial, sans-serif;
            }}
            body {{
                margin: 0;
                padding: 20px;
                background: #081221;
                color: white;
            }}
            h1 {{
                margin-bottom: 20px;
            }}
            .cards {{
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin-bottom: 20px;
            }}
            .card {{
                background: #102040;
                border-radius: 10px;
                padding: 20px;
                min-width: 180px;
            }}
            .card .label {{
                font-size: 14px;
                color: #cbd5e1;
            }}
            .card .value {{
                margin-top: 10px;
                font-size: 32px;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: #102040;
            }}
            th, td {{
                border: 1px solid #1c335f;
                padding: 10px;
                text-align: left;
                font-size: 14px;
            }}
            th {{
                background: #16305c;
            }}
        </style>
    </head>
    <body>
        <h1>Secure File Monitoring Dashboard</h1>

        <div class="cards">
            <div class="card">
                <div class="label">Total Logs</div>
                <div class="value">{total_logs}</div>
            </div>
            <div class="card">
                <div class="label">USB Inserted</div>
                <div class="value">{usb_inserted}</div>
            </div>
            <div class="card">
                <div class="label">Files Created</div>
                <div class="value">{files_created}</div>
            </div>
            <div class="card">
                <div class="label">Files Deleted</div>
                <div class="value">{files_deleted}</div>
            </div>
            <div class="card">
                <div class="label">Unauthorized Events</div>
                <div class="value">{unauthorized}</div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Event</th>
                    <th>Source</th>
                    <th>Destination</th>
                    <th>File Name</th>
                    <th>User</th>
                    <th>Status</th>
                    <th>Size</th>
                    <th>Hash</th>
                    <th>Alert</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
    </body>
    </html>
    """
    return html


if __name__ == "__main__":
    print("Reading logs from:", LOG_FILE)
    app.run(debug=True)
