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
    usb_inserted = sum(1 for log in logs if log.get("event") == "USB_INSERTED")
    usb_removed = sum(1 for log in logs if log.get("event") == "USB_REMOVED")
    files_created = sum(1 for log in logs if log.get("event") == "FILE_CREATED")
    files_deleted = sum(1 for log in logs if log.get("event") == "FILE_DELETED")
    files_modified = sum(1 for log in logs if log.get("event") == "FILE_MODIFIED")
    files_copied_to_usb = sum(1 for log in logs if log.get("event") == "FILE_COPIED_TO_USB")
    unauthorized = sum(1 for log in logs if str(log.get("status")) == "UNAUTHORIZED")

    rows = ""
    if logs:
        for log in logs:
            rows += f"""
            <tr>
                <td>{log.get('timestamp', '-')}</td>
                <td>{log.get('event', '-')}</td>
                <td class="path-cell">{log.get('source', '-')}</td>
                <td class="path-cell">{log.get('destination', '-')}</td>
                <td>{log.get('file_name', '-')}</td>
                <td>{log.get('user', '-')}</td>
                <td><span class="{badge_class(log.get('status', '-'))}">{log.get('status', '-')}</span></td>
                <td>{log.get('file_size', 0)}</td>
                <td class="hash-cell">{log.get('hash', '-')}</td>
                <td>{log.get('alert', '-')}</td>
            </tr>
            """
    else:
        rows = """
        <tr>
            <td colspan="10" class="empty-row">No logs found</td>
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
                display: flex;
                justify-content: space-between;
                gap: 24px;
                background: rgba(9, 20, 40, 0.95);
                border: 1px solid rgba(82, 129, 255, 0.18);
                border-radius: 28px;
                padding: 32px;
                margin-bottom: 28px;
                box-shadow: 0 14px 45px rgba(0, 0, 0, 0.25);
            }}

            .hero-left {{
                flex: 1;
            }}

            .tag {{
                display: inline-block;
                padding: 10px 18px;
                border-radius: 999px;
                background: rgba(59, 130, 246, 0.14);
                border: 1px solid rgba(96, 165, 250, 0.35);
                color: #c8dcff;
                font-weight: 700;
                margin-bottom: 18px;
                font-size: 15px;
            }}

            .title {{
                font-size: 58px;
                line-height: 1.05;
                margin: 0 0 16px 0;
            }}

            .subtitle {{
                color: #a8bbdc;
                font-size: 19px;
                line-height: 1.6;
                max-width: 980px;
                margin: 0;
            }}

            .hero-right {{
                width: 240px;
                display: flex;
                flex-direction: column;
                gap: 16px;
            }}

            .mini-card {{
                background: rgba(8, 17, 36, 0.95);
                border: 1px solid rgba(82, 129, 255, 0.18);
                border-radius: 22px;
                padding: 22px;
            }}

            .mini-card .label {{
                color: #94a8c9;
                font-size: 16px;
                margin-bottom: 8px;
            }}

            .mini-card .value {{
                font-size: 24px;
                font-weight: 700;
            }}

            .online {{
                color: #45f28c;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(7, 1fr);
                gap: 18px;
                margin-bottom: 28px;
            }}

            .card {{
                background: rgba(8, 17, 36, 0.96);
                border: 1px solid rgba(82, 129, 255, 0.18);
                border-radius: 22px;
                padding: 22px;
                min-height: 126px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
            }}

            .card .label {{
                color: #a3b5d3;
                font-size: 15px;
                margin-bottom: 12px;
            }}

            .card .value {{
                font-size: 42px;
                font-weight: 700;
            }}

            .card.blue {{ border-color: rgba(59, 130, 246, 0.35); }}
            .card.red {{ border-color: rgba(239, 68, 68, 0.35); }}
            .card.green {{ border-color: rgba(34, 197, 94, 0.35); }}
            .card.yellow {{ border-color: rgba(245, 158, 11, 0.35); }}
            .card.cyan {{ border-color: rgba(6, 182, 212, 0.35); }}
            .card.purple {{ border-color: rgba(168, 85, 247, 0.35); }}

            .table-box {{
                background: rgba(8, 17, 36, 0.96);
                border: 1px solid rgba(82, 129, 255, 0.18);
                border-radius: 26px;
                padding: 24px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
            }}

            .table-title {{
                font-size: 34px;
                margin: 0 0 18px 0;
            }}

            .table-wrap {{
                overflow-x: auto;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                min-width: 1400px;
            }}

            thead {{
                background: rgba(255, 255, 255, 0.04);
            }}

            th, td {{
                padding: 14px 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                text-align: left;
                vertical-align: top;
                font-size: 14px;
            }}

            th {{
                color: #d7e4ff;
                font-size: 15px;
            }}

            td {{
                color: #edf4ff;
            }}

            tr:hover {{
                background: rgba(255, 255, 255, 0.03);
            }}

            .path-cell {{
                max-width: 280px;
                word-break: break-word;
                color: #c9d8f0;
            }}

            .hash-cell {{
                max-width: 280px;
                word-break: break-all;
                color: #bcd2ff;
                font-size: 13px;
            }}

            .badge {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 999px;
                font-size: 12px;
                font-weight: 700;
            }}

            .success {{
                background: rgba(34, 197, 94, 0.16);
                color: #69f0a0;
            }}

            .danger {{
                background: rgba(239, 68, 68, 0.16);
                color: #ff8b8b;
            }}

            .info {{
                background: rgba(6, 182, 212, 0.16);
                color: #73e7ff;
            }}

            .warning {{
                background: rgba(245, 158, 11, 0.16);
                color: #ffd278;
            }}

            .neutral {{
                background: rgba(148, 163, 184, 0.16);
                color: #d6dce6;
            }}

            .empty-row {{
                text-align: center;
                color: #a8bbdc;
                padding: 26px;
            }}

            @media (max-width: 1400px) {{
                .cards {{
                    grid-template-columns: repeat(4, 1fr);
                }}
            }}

            @media (max-width: 1000px) {{
                .hero {{
                    flex-direction: column;
                }}

                .hero-right {{
                    width: 100%;
                    flex-direction: row;
                }}

                .mini-card {{
                    flex: 1;
                }}

                .cards {{
                    grid-template-columns: repeat(2, 1fr);
                }}

                .title {{
                    font-size: 40px;
                }}
            }}

            @media (max-width: 650px) {{
                .cards {{
                    grid-template-columns: 1fr;
                }}

                .hero-right {{
                    flex-direction: column;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="hero">
                <div class="hero-left">
                    <div class="tag">Cybersecurity Monitoring</div>
                    <h1 class="title">🔐 Secure File Monitoring Dashboard</h1>
                    <p class="subtitle">
                        Real-time monitoring of file creation, deletion, modification,
                        USB activity, and possible unauthorized access.
                    </p>
                </div>

                <div class="hero-right">
                    <div class="mini-card">
                        <div class="label">System Status</div>
                        <div class="value online">Online</div>
                    </div>
                    <div class="mini-card">
                        <div class="label">Refresh</div>
                        <div class="value">Every 5s</div>
                    </div>
                </div>
            </div>

            <div class="cards">
                <div class="card blue">
                    <div class="label">Total Logs</div>
                    <div class="value">{total_logs}</div>
                </div>
                <div class="card cyan">
                    <div class="label">USB Inserted</div>
                    <div class="value">{usb_inserted}</div>
                </div>
                <div class="card yellow">
                    <div class="label">USB Removed</div>
                    <div class="value">{usb_removed}</div>
                </div>
                <div class="card green">
                    <div class="label">Files Created</div>
                    <div class="value">{files_created}</div>
                </div>
                <div class="card red">
                    <div class="label">Files Deleted</div>
                    <div class="value">{files_deleted}</div>
                </div>
                <div class="card purple">
                    <div class="label">Files Modified</div>
                    <div class="value">{files_modified}</div>
                </div>
                <div class="card red">
                    <div class="label">Unauthorized Events</div>
                    <div class="value">{unauthorized}</div>
                </div>
            </div>

            <div class="table-box">
                <h2 class="table-title">Recent Activity Logs</h2>
                <div class="table-wrap">
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
                </div>
            </div>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    print("Reading logs from:", LOG_FILE)
    app.run(debug=True)
