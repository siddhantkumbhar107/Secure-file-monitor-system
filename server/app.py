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
    except:
        return []


def badge_class(status):
    status = str(status).upper()
    if status == "AUTHORIZED":
        return "badge success"
    if status == "UNAUTHORIZED":
        return "badge danger"
    if status == "CONNECTED":
        return "badge info"
    if status == "DISCONNECTED":
        return "badge warning"
    return "badge neutral"


@app.route("/")
def dashboard():
    logs = load_logs()

    total_logs = len(logs)
    files_created = sum(1 for log in logs if log.get("event") == "FILE_CREATED")
    files_deleted = sum(1 for log in logs if log.get("event") == "FILE_DELETED")
    files_modified = sum(1 for log in logs if log.get("event") == "FILE_MODIFIED")
    usb_inserted = sum(1 for log in logs if log.get("event") == "USB_INSERTED")
    unauthorized = sum(1 for log in logs if log.get("status") == "UNAUTHORIZED")

    rows = ""
    if logs:
        for log in logs:
            rows += f"""
            <tr>
                <td>{log.get('timestamp', '-')}</td>
                <td>{log.get('event', '-')}</td>
                <td>{log.get('file_name', '-')}</td>
                <td><span class="{badge_class(log.get('status', '-'))}">{log.get('status', '-')}</span></td>
                <td>{log.get('alert', '-')}</td>
            </tr>
            """
    else:
        rows = "<tr><td colspan='5'>No logs found</td></tr>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="5">
        <title>Secure File Monitoring Dashboard</title>
        <style>
            body {{
                font-family: Arial;
                background: #081221;
                color: white;
                padding: 20px;
            }}

            h1 {{
                text-align: center;
            }}

            .cards {{
                display: flex;
                gap: 15px;
                margin: 20px 0;
                flex-wrap: wrap;
            }}

            .card {{
                background: #102040;
                padding: 20px;
                border-radius: 10px;
                width: 180px;
                text-align: center;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}

            th, td {{
                border: 1px solid #1c335f;
                padding: 10px;
            }}

            th {{
                background: #16305c;
            }}

            .badge {{
                padding: 5px 10px;
                border-radius: 5px;
            }}

            .success {{ background: green; }}
            .danger {{ background: red; }}
            .info {{ background: blue; }}
            .warning {{ background: orange; }}
        </style>
    </head>

    <body>

    <h1>🔐 Secure File Monitoring Dashboard</h1>

    <!-- HOW TO USE SECTION -->
    <div style="margin-top:20px; background:#0f1f3d; padding:20px; border-radius:12px; border:1px solid #1e3a8a;">
        <h2 style="margin-bottom:10px;">📘 How to Use This System</h2>
        <ul style="line-height:1.8; color:#cbd5f5;">
            <li>Run <b>monitor.py</b> in one terminal</li>
            <li>Run <b>app.py</b> in another terminal</li>
            <li>Open <b>http://127.0.0.1:5000/</b></li>
            <li>Create, modify, or delete any file</li>
            <li>Insert a USB device to track activity</li>
            <li>Dashboard updates automatically every 5 seconds</li>
        </ul>
    </div>

    <div class="cards">
        <div class="card">Total Logs<br><b>{total_logs}</b></div>
        <div class="card">Created<br><b>{files_created}</b></div>
        <div class="card">Deleted<br><b>{files_deleted}</b></div>
        <div class="card">Modified<br><b>{files_modified}</b></div>
        <div class="card">USB Inserted<br><b>{usb_inserted}</b></div>
        <div class="card">Unauthorized<br><b>{unauthorized}</b></div>
    </div>

    <table>
        <tr>
            <th>Time</th>
            <th>Event</th>
            <th>File</th>
            <th>Status</th>
            <th>Alert</th>
        </tr>
        {rows}
    </table>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
