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
    except Exception:
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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secure File Monitoring Dashboard</title>
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #061326, #020817 60%, #0a1f3f);
                color: white;
                padding: 24px;
            }}

            .container {{
                max-width: 1500px;
                margin: auto;
            }}

            .header {{
                text-align: center;
                margin-bottom: 26px;
            }}

            .header h1 {{
                margin: 0;
                font-size: 56px;
                font-weight: 700;
            }}

            .header p {{
                margin-top: 14px;
                color: #c7d7f3;
                font-size: 18px;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 18px;
                margin-bottom: 26px;
            }}

            .card {{
                background: rgba(13, 31, 61, 0.95);
                border: 1px solid #1e3a8a;
                border-radius: 16px;
                padding: 22px;
                text-align: center;
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
            }}

            .card .label {{
                color: #d3def7;
                font-size: 15px;
                margin-bottom: 10px;
            }}

            .card .value {{
                font-size: 26px;
                font-weight: 700;
            }}

            .table-box {{
                background: rgba(13, 31, 61, 0.95);
                border: 1px solid #1e3a8a;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 10px 24px rgba(0, 0, 0, 0.22);
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
            }}

            th {{
                background: #1a3970;
                color: white;
                text-align: left;
                padding: 16px;
                font-size: 15px;
            }}

            td {{
                padding: 16px;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                font-size: 14px;
                color: #edf3ff;
            }}

            tr:hover {{
                background: rgba(255, 255, 255, 0.03);
            }}

            .badge {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 999px;
                font-size: 12px;
                font-weight: bold;
            }}

            .success {{
                background: rgba(34, 197, 94, 0.18);
                color: #7dffb1;
            }}

            .danger {{
                background: rgba(239, 68, 68, 0.18);
                color: #ff9f9f;
            }}

            .info {{
                background: rgba(59, 130, 246, 0.18);
                color: #8fc1ff;
            }}

            .warning {{
                background: rgba(245, 158, 11, 0.18);
                color: #ffd37d;
            }}

            .neutral {{
                background: rgba(148, 163, 184, 0.18);
                color: #d6deea;
            }}

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
                z-index: 1000;
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
                z-index: 1000;
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

                .header h1 {{
                    font-size: 42px;
                }}
            }}

            @media (max-width: 700px) {{
                .cards {{
                    grid-template-columns: repeat(2, 1fr);
                }}

                .header h1 {{
                    font-size: 32px;
                }}

                .header p {{
                    font-size: 16px;
                }}

                .help-box {{
                    width: calc(100% - 40px);
                    right: 20px;
                }}
            }}

            @media (max-width: 500px) {{
                .cards {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>

    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Secure File Monitoring Dashboard</h1>
                <p>Real-time monitoring of file creation, deletion, USB activity, and possible unauthorized access.</p>
            </div>

            <div class="cards">
                <div class="card">
                    <div class="label">Total Logs</div>
                    <div class="value">{total_logs}</div>
                </div>
                <div class="card">
                    <div class="label">Created</div>
                    <div class="value">{files_created}</div>
                </div>
                <div class="card">
                    <div class="label">Deleted</div>
                    <div class="value">{files_deleted}</div>
                </div>
                <div class="card">
                    <div class="label">Modified</div>
                    <div class="value">{files_modified}</div>
                </div>
                <div class="card">
                    <div class="label">USB Inserted</div>
                    <div class="value">{usb_inserted}</div>
                </div>
                <div class="card">
                    <div class="label">Unauthorized</div>
                    <div class="value">{unauthorized}</div>
                </div>
            </div>

            <div class="table-box">
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

        <button class="How to use-button" onclick="toggleHow to use()">❓ How to use</button>

        <div id="how to useBox" class="how to use-box">
            <h3>📘 How to Use</h3>
            <ul>
                <li>Run <b>monitor.py</b> in one terminal</li>
                <li>Run <b>app.py</b> in another terminal</li>
                <li>Open <b>http://127.0.0.1:5000/</b></li>
                <li>Create, modify, or delete any file</li>
                <li>Insert a USB device to track activity</li>
                <li>Dashboard updates automatically every 5 seconds</li>
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
