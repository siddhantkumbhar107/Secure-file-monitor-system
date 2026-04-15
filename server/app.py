from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# In-memory logs for free Render
logs = []


@app.route("/api/logs", methods=["POST"])
def receive_logs():
    try:
        data = request.get_json(force=True)
        logs.append(data)
        print("RECEIVED LOG:", data)
        return jsonify({"status": "success", "count": len(logs)}), 200
    except Exception as e:
        print("ERROR RECEIVING LOG:", e)
        return jsonify({"status": "error", "message": str(e)}), 500


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
    total_logs = len(logs)
    files_created = sum(1 for log in logs if log.get("event") == "FILE_CREATED")
    files_deleted = sum(1 for log in logs if log.get("event") == "FILE_DELETED")
    files_modified = sum(1 for log in logs if log.get("event") == "FILE_MODIFIED")
    usb_inserted = sum(1 for log in logs if log.get("event") == "USB_INSERTED")
    unauthorized = sum(1 for log in logs if str(log.get("status")).upper() == "UNAUTHORIZED")

    rows = ""
    for log in reversed(logs):
        rows += f"""
        <tr>
            <td>{log.get('timestamp', '-')}</td>
            <td>{log.get('event', '-')}</td>
            <td>{log.get('file_name', '-')}</td>
            <td><span class="{badge_class(log.get('status', '-'))}">{log.get('status', '-')}</span></td>
            <td>{log.get('alert', '-')}</td>
        </tr>
        """

    if not rows:
        rows = "<tr><td colspan='5'>No logs found</td></tr>"

    return f"""
 <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="5">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secure Monitoring</title>
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #061326, #020817 60%, #0a1f3f);
                color: white;
                padding: 24px;
            }}
            h1 {{
                margin-bottom: 20px;
            }}
            .cards {{
                display: flex;
                gap: 15px;
                flex-wrap: wrap;
                margin-bottom: 20px;
            }}
            .card {{
                background: #102040;
                border: 1px solid #1e3a8a;
                border-radius: 12px;
                padding: 18px;
                min-width: 150px;
                text-align: center;
            }}
            .label {{
                font-size: 14px;
                color: #d3def7;
            }}
            .value {{
                font-size: 26px;
                font-weight: bold;
                margin-top: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: #102040;
            }}
            th {{
                background: #16305c;
                text-align: left;
                padding: 12px;
            }}
            td {{
                padding: 12px;
                border: 1px solid #1c335f;
            }}
            .badge {{
                padding: 5px 10px;
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }}
            .success {{ background: green; }}
            .danger {{ background: red; }}
            .info {{ background: blue; }}
            .warning {{ background: orange; }}
            .neutral {{ background: gray; }}
        </style>
    </head>
    <body>
        <h1>🔐 Secure File Monitoring Dashboard</h1>

        <div class="cards">
            <div class="card"><div class="label">Total Logs</div><div class="value">{total_logs}</div></div>
            <div class="card"><div class="label">Created</div><div class="value">{files_created}</div></div>
            <div class="card"><div class="label">Deleted</div><div class="value">{files_deleted}</div></div>
            <div class="card"><div class="label">Modified</div><div class="value">{files_modified}</div></div>
            <div class="card"><div class="label">USB</div><div class="value">{usb_inserted}</div></div>
            <div class="card"><div class="label">Unauthorized</div><div class="value">{unauthorized}</div></div>
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


if __name__ == "__main__":
    app.run(debug=True)
