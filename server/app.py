from flask import Flask, render_template
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")


@app.route("/")
def dashboard():
    logs = []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []

    return render_template("dashboard.html", logs=logs)


if __name__ == "__main__":
    print("Reading logs from:", LOG_FILE)
    app.run(debug=True)
