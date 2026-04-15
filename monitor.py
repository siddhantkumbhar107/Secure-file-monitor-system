import time
import os
import json
import socket
import getpass
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

API_URL = "https://secure-file-monitor-system.onrender.com/api/logs"

WATCH_FOLDERS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Documents")
]


def get_device():
    return socket.gethostname()


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

    print("SENDING LOG:", log_entry)

    try:
        response = requests.post(API_URL, json=log_entry, timeout=10)
        print("SERVER RESPONSE:", response.status_code, response.text)
    except Exception as e:
        print("ERROR SENDING LOG:", e)


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


def start_monitor():
    observer = Observer()
    handler = MonitorHandler()

    print("🚀 Monitoring Started...")
    print("Watching folders:")

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
