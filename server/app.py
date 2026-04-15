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
return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure File Monitoring Dashboard</title>
    <style>
        * {{
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }}

        body {{
            margin: 0;
            padding: 24px;
            background: linear-gradient(135deg, #061326, #020817 60%, #0a1f3f);
            color: white;
        }}

        .container {{
            max-width: 1600px;
            margin: auto;
        }}

        .hero {{
            background: rgba(10, 20, 40, 0.95);
            border: 1px solid rgba(82, 129, 255, 0.18);
            border-radius: 24px;
            padding: 30px;
            margin-bottom: 24px;
            box-shadow: 0 14px 35px rgba(0,0,0,0.25);
        }}

        .hero h1 {{
            margin: 0 0 10px 0;
            font-size: 54px;
            font-weight: 700;
        }}

        .hero p {{
            margin: 0;
            color: #b7c8e6;
            font-size: 18px;
            line-height: 1.6;
        }}

        .cards {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 18px;
            margin-bottom: 24px;
        }}

        .card {{
            background: rgba(13, 31, 61, 0.95);
            border: 1px solid #1e3a8a;
            border-radius: 18px;
            padding: 22px;
            text-align: center;
            box-shadow: 0 10px 22px rgba(0,0,0,0.18);
        }}

        .card .label {{
            color: #d2def5;
            font-size: 15px;
            margin-bottom: 8px;
        }}

        .card .value {{
            font-size: 34px;
            font-weight: 700;
        }}

        .table-box {{
            background: rgba(13, 31, 61, 0.95);
            border: 1px solid #1e3a8a;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 10px 22px rgba(0,0,0,0.18);
        }}

        .table-title {{
            padding: 22px 22px 0 22px;
            font-size: 28px;
            font-weight: 700;
        }}

        .table-wrap {{
            overflow-x: auto;
            padding: 18px 22px 22px 22px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            min-width: 1000px;
        }}

        th {{
            background: #1a3970;
            color: white;
            text-align: left;
            padding: 14px;
            font-size: 15px;
        }}

        td {{
            padding: 14px;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            font-size: 14px;
            color: #edf3ff;
        }}

        tr:hover {{
            background: rgba(255,255,255,0.03);
        }}

        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}

        .success {{ background: #16a34a; }}
        .danger {{ background: #dc2626; }}
        .info {{ background: #2563eb; }}
        .warning {{ background: #d97706; }}
        .neutral {{ background: #64748b; }}

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
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }}

        .help-box {{
            display: none;
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 320px;
            background: #0f1f3d;
            color: white;
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #1e3a8a;
            box-shadow: 0 5px 20px rgba(0,0,0,0.4);
        }}

        .help-box h3 {{
            margin-top: 0;
            margin-bottom: 10px;
        }}

        .help-box ul {{
            margin: 0;
            padding-left: 18px;
            line-height: 1.7;
            color: #cbd5f5;
            font-size: 14px;
        }}

        @media (max-width: 1200px) {{
            .cards {{
                grid-template-columns: repeat(3, 1fr);
            }}

            .hero h1 {{
                font-size: 40px;
            }}
        }}

        @media (max-width: 700px) {{
            .cards {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}

        @media (max-width: 500px) {{
            .cards {{
                grid-template-columns: 1fr;
            }}

            .hero h1 {{
                font-size: 30px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>🔐 Secure File Monitoring Dashboard</h1>
            <p>Centralized real-time dashboard for file activity, USB events, and suspicious actions received from connected devices.</p>
        </div>

        <div class="cards">
            <div class="card"><div class="label">Total Logs</div><div class="value">{total_logs}</div></div>
            <div class="card"><div class="label">Created</div><div class="value">{files_created}</div></div>
            <div class="card"><div class="label">Deleted</div><div class="value">{files_deleted}</div></div>
            <div class="card"><div class="label">Modified</div><div class="value">{files_modified}</div></div>
            <div class="card"><div class="label">USB</div><div class="value">{usb_inserted}</div></div>
            <div class="card"><div class="label">Unauthorized</div><div class="value">{unauthorized}</div></div>
        </div>

        <div class="table-box">
            <div class="table-title">Recent Activity Logs</div>
            <div class="table-wrap">
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
            </div>
        </div>
    </div>

    <button class="help-button" onclick="toggleHelp()">❓ Help</button>

    <div id="helpBox" class="help-box">
        <h3>📘 How to Use</h3>
        <ul>
            <li>Run <b>monitor.py</b> on any laptop</li>
            <li>Logs are sent to the Render dashboard</li>
            <li>Open <b>https://secure-file-monitor-system.onrender.com/</b></li>
            <li>Create, modify, or delete files</li>
            <li>Refresh happens automatically every 5 seconds</li>
        </ul>
    </div>

    <script>
        function toggleHelp() {{
            var box = document.getElementById("helpBox");
            if (box.style.display === "none" || box.style.display === "") {{
                box.style.display = "block";
            }} else {{
                box.style.display = "none";
            }}
        }}
    </script>
</body>
</html>
"""
if __name__ == "__main__":
    app.run(debug=True)
