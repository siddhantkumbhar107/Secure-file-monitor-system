import time
import os
import socket
import getpass
import requests
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

API_URL = "https://secure-file-monitor-system.onrender.com/api/logs"

WATCH_FOLDERS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads"),
    os.path.expanduser("~/Documents")
]

known_usb_drives = set()
recent_events = {}


def get_device():
    return socket.gethostname()


def is_duplicate(event_key, seconds=2):
    now = time.time()
    old = recent_events.get(event_key)
    if old and (now - old) < seconds:
        return True
    recent_events[event_key] = now
    return False


def send_log(event, file_path="-", status="AUTHORIZED", alert=""):
    file_name = os.path.basename(file_path) if file_path and file_path != "-" else "-"

    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": event,
        "file_name": file_name,
        "status": status,
        "alert": alert,
        "user": getpass.getuser(),
        "device": get_device(),
        "source": file_path,
        "destination": "-"
    }

    try:
        response = requests.post(API_URL, json=log_entry, timeout=10)
        print("SENT:", log_entry)
        print("SERVER:", response.status_code, response.text)
    except Exception as e:
        print("ERROR SENDING LOG:", e)


class MonitorHandler(FileSystemEventHandler):
    def on_created(self, event):
        path = event.src_path
        key = f"CREATE:{path}"
        if is_duplicate(key):
            return

        if event.is_directory:
            send_log("FOLDER_CREATED", path, "AUTHORIZED", "Folder created")
        else:
            send_log("FILE_CREATED", path, "AUTHORIZED", "File created")

    def on_deleted(self, event):
        path = event.src_path
        key = f"DELETE:{path}"
        if is_duplicate(key):
            return

        if event.is_directory:
            send_log("FOLDER_DELETED", path, "AUTHORIZED", "Folder deleted")
        else:
            send_log("FILE_DELETED", path, "AUTHORIZED", "File deleted")

    def on_modified(self, event):
        path = event.src_path
        key = f"MODIFY:{path}"
        if is_duplicate(key):
            return

        if not event.is_directory:
            filename = os.path.basename(path).lower()
            if filename in {"desktop.ini", "thumbs.db"}:
                return
            send_log("FILE_MODIFIED", path, "AUTHORIZED", "File modified")


def get_usb_drives():
    drives = set()
    try:
        for part in psutil.disk_partitions(all=False):
            opts = (part.opts or "").lower()
            if "removable" in opts:
                drives.add(part.device)
    except Exception as e:
        print("USB DETECTION ERROR:", e)
    return drives


def monitor_usb():
    global known_usb_drives

    while True:
        current_drives = get_usb_drives()

        inserted = current_drives - known_usb_drives
        removed = known_usb_drives - current_drives

        for drive in inserted:
            send_log("USB_INSERTED", drive, "CONNECTED", "USB device inserted")

        for drive in removed:
            send_log("USB_REMOVED", drive, "DISCONNECTED", "USB device removed")

        known_usb_drives = current_drives
        time.sleep(3)


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
        monitor_usb()
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


if __name__ == "__main__":
    start_monitor()
