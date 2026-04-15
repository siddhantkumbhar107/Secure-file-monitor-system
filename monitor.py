import time
import json
import os
import hashlib
import socket
import getpass
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# YOUR RENDER API URL
API_URL = "https://secure-file-monitor-system.onrender.com/api/logs"

# FILE TO STORE LOCAL LOGS
LOG_FILE = "logs.json"

# WATCHED FOLDERS (AUTO DETECT)
WATCH_FOLDERS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Documents")
]


# GET DEVICE NAME
def get_device():
    return socket.gethostname()


# CREATE HASH (OPTIONAL)
def get_hash(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return "-"


# SAVE LOG + SEND TO SERVER
def add_log(event, file_path, status="AUTHORIZED", alert=""):
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "file_name": os.path.basename(file_path) if file_path else "-",
        "status": status,
        "alert": alert,
        "user": getpass.getuser(),
        "device": get_device(),
        "source": file_path,
        "destination": "-"
    }

    # SAVE LOCALLY
    try:
        logs = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(LOG_FILE, "w") as f:
            json.dump(logs, f, indent=4)
    except:
        pass

    # SEND TO RENDER
    try:
        requests.post(API_URL, json=log_entry, timeout=5)
    except:
        print("⚠ Could not send log to server")

    print("LOG:", log_entry)


# EVENT HANDLER
class MonitorHandler(FileSystemEventHandler):

    def on_created(self, event):
        if not event.is_directory:
            add_log("FILE_CREATED", event.src_path, "AUTHORIZED", "File created")

    def on_deleted(self, event):
        if not event.is_directory:
            add_log("FILE_DELETED", event.src_path, "AUTHORIZED", "File deleted")

    def on_modified(self, event):
        if not event.is_directory:
            add_log("FILE_MODIFIED", event.src_path, "AUTHORIZED", "File modified")


# MAIN FUNCTION
def start_monitor():
    observer = Observer()
    handler = MonitorHandler()

    print("🚀 Monitoring Started...")
    print("👀 Watching folders:")

    for folder in WATCH_FOLDERS:
        if os.path.exists(folder):
            observer.schedule(handler, folder, recursive=True)
            print(" -", folder)

    observer.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    start_monitor()
