from flask import Flask
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")


def load_logs():
    demo_logs = [
        {
            "timestamp": "2026-04-14 16:00:00",
            "event": "SYSTEM_STARTED",
            "file_name": "-",
            "status": "AUTHORIZED",
            "alert": "Monitoring system started"
        },
        {
            "timestamp": "2026-04-14 16:01:00",
            "event": "FILE_CREATED",
            "file_name": "example.txt",
            "status": "AUTHORIZED",
            "alert": "File created successfully"
        },
        {
            "timestamp": "2026-04-14 16:02:00",
            "event": "USB_INSERTED",
            "file_name": "USB Drive",
            "status": "CONNECTED",
            "alert": "USB device inserted"
        },
        {
            "timestamp": "2026-04-14 16:03:00",
            "event": "FILE_COPIED_TO_USB",
            "file_name": "example.txt",
            "status": "UNAUTHORIZED",
            "alert": "File copied to USB"
        }
    ]

    try:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    return data
    except Exception:
        pass

    return demo_logs
# STATUS BADGE
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
    for log in logs:
        rows += f"""
        <tr>
            <td>{log.get('timestamp','-')}</td>
            <td>{log.get('event','-')}</td>
            <td>{log.get('file_name','-')}</td>
            <td><span class="{badge_class(log.get('status','-'))}">{log.get('status','-')}</span></td>
            <td>{log.get('alert','-')}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="5">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secure File Monitoring Dashboard</title>

        <style>
            body {{
                margin: 0;
                font-family: Arial;
                background: linear-gradient(135deg,#061326,#020817,#0a1f3f);
                color: white;
                padding: 20px;
            }}

            h1 {{
                text-align: center;
            }}

            .cards {{
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin: 20px 0;
            }}

            .card {{
                background: #102040;
                padding: 15px;
                border-radius: 10px;
                min-width: 150px;
                text-align: center;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: #102040;
            }}

            th, td {{
                padding: 10px;
                border: 1px solid #1c335f;
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

            /* HELP BUTTON */
            .help-button {{
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: #2563eb;
                color: white;
                border: none;
                padding: 12px 18px;
                border-radius: 50px;
                cursor: pointer;
                font-weight: bold;
            }}

            .help-box {{
                display: none;
                position: fixed;
                bottom: 80px;
                right: 20px;
                width: 300px;
                background: #0f1f3d;
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #1e3a8a;
            }}
        </style>
    </head>

    <body>

    <h1>🔐 Secure File Monitoring Dashboard</h1>

    <div class="cards">
        <div class="card">Total Logs<br><b>{total_logs}</b></div>
        <div class="card">Created<br><b>{files_created}</b></div>
        <div class="card">Deleted<br><b>{files_deleted}</b></div>
        <div class="card">Modified<br><b>{files_modified}</b></div>
        <div class="card">USB<br><b>{usb_inserted}</b></div>
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

    <!-- HELP BUTTON -->
    <button class="help-button" onclick="toggleHelp()">❓ Help</button>

    <!-- HELP POPUP -->
    <div id="helpBox" class="help-box">
        <h3>📘 How to Use</h3>
        <ul>
            <li>Run <b>monitor.py</b></li>
            <li>Run <b>app.py</b></li>
            <li>Local: <b>http://127.0.0.1:5000/</b></li>
            <li>Online: <b>https://secure-file-monitor-system.onrender.com/</b></li>
            <li>Create / delete files</li>
            <li>Insert USB device</li>
        </ul>
    </div>

    <script>
    function toggleHelp() {{
        var box = document.getElementById("helpBox");
        box.style.display = (box.style.display === "block") ? "none" : "block";
    }}
    </script>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
