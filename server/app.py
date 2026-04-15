from flask import Flask, request, jsonify

app = Flask(__name__)

# GLOBAL LOG STORAGE (IN MEMORY)
logs = []


@app.route("/api/logs", methods=["POST"])
def receive_logs():
    try:
        data = request.json
        logs.append(data)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)})


def badge_class(status):
    status = str(status).upper()
    if status == "AUTHORIZED":
        return "badge success"
    if status == "UNAUTHORIZED":
        return "badge danger"
    if status == "CONNECTED":
        return "badge info"
    return "badge neutral"


@app.route("/")
def dashboard():
    total_logs = len(logs)
    files_created = sum(1 for log in logs if log.get("event") == "FILE_CREATED")
    files_deleted = sum(1 for log in logs if log.get("event") == "FILE_DELETED")
    files_modified = sum(1 for log in logs if log.get("event") == "FILE_MODIFIED")
    usb_inserted = sum(1 for log in logs if log.get("event") == "USB_INSERTED")
    unauthorized = sum(1 for log in logs if log.get("status") == "UNAUTHORIZED")

    rows = ""
    for log in reversed(logs):
        rows += f"""
        <tr>
            <td>{log.get('timestamp','-')}</td>
            <td>{log.get('event','-')}</td>
            <td>{log.get('file_name','-')}</td>
            <td><span class="{badge_class(log.get('status','-'))}">{log.get('status','-')}</span></td>
            <td>{log.get('alert','-')}</td>
        </tr>
        """

    if not rows:
        rows = "<tr><td colspan='5'>No logs found</td></tr>"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="5">
        <title>Secure Monitoring</title>
        <style>
            body {{ background:#081221; color:white; font-family:Arial; padding:20px; }}
            table {{ width:100%; border-collapse: collapse; }}
            th, td {{ padding:10px; border:1px solid #1c335f; }}
            th {{ background:#16305c; }}
            .badge {{ padding:5px 10px; border-radius:5px; }}
            .success {{ background:green; }}
            .danger {{ background:red; }}
            .info {{ background:blue; }}
        </style>
    </head>
    <body>

    <h1>🔐 Secure File Monitoring Dashboard</h1>

    <p>Total Logs: {total_logs}</p>

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
