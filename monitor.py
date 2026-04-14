import os
import time
import json
import psutil
import hashlib
import getpass
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs.json")

IGNORED_FILES = {
    os.path.abspath(LOG_FILE).lower(),
    os.path.abspath(os.path.join(BASE_DIR, "app.py")).lower(),
    os.path.abspath(os.path.join(BASE_DIR, "monitor.py")).lower(),
    os.path.abspath(os.path.join(BASE_DIR, "requirements.txt")).lower(),
    os.path.abspath(os.path.join(BASE_DIR, "run.bat")).lower(),
}

USB_WATCHERS = {}
SYSTEM_WATCHERS = []
CONNECTED_USB_DRIVES = set()
RECENT_EVENTS = {}


def should_ignore(path):
    if not path:
        return False
    try:
        return os.path.abspath(path).lower() in IGNORED_FILES
    except Exception:
        return False


def get_current_user():
    try:
        return getpass.getuser()
    except Exception:
        return "Unknown"


def ensure_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)


def load_logs():
    ensure_log_file()
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception:
        return []


def save_logs(logs):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)


def calculate_file_hash(file_path):
    if not file_path or file_path == "-":
        return "-"

    if should_ignore(file_path):
        return "IGNORED"

    if not os.path.exists(file_path):
        return "FILE_NOT_FOUND"

    if os.path.isdir(file_path):
        return "FOLDER_NO_HASH"

    try:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        return f"HASH_ERROR: {str(e)}"


def get_file_size(file_path):
    try:
        if file_path and os.path.isfile(file_path) and not should_ignore(file_path):
            return os.path.getsize(file_path)
    except Exception:
        pass
    return 0


def get_file_name(path):
    try:
        if not path or path == "-":
            return "-"
        return os.path.basename(path) or path
    except Exception:
        return "-"


def is_duplicate(event_type, source, destination, seconds=2):
    key = f"{event_type}|{source}|{destination}"
    now = time.time()
    old_time = RECENT_EVENTS.get(key)

    if old_time and (now - old_time) < seconds:
        return True

    RECENT_EVENTS[key] = now
    return False


def add_log(event_type, source, destination, status, alert):
    if should_ignore(source) or should_ignore(destination):
        return

    if is_duplicate(event_type, source, destination):
        return

    logs = load_logs()
    target = destination if destination and destination != "-" else source

    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": event_type,
        "source": source if source else "-",
        "destination": destination if destination else "-",
        "file_name": get_file_name(target),
        "user": get_current_user(),
        "status": status,
        "file_size": get_file_size(target),
        "hash": calculate_file_hash(target),
        "alert": alert
    }

    logs.insert(0, log_entry)
    save_logs(logs)

    print("=" * 70)
    print(f"LOG SAVED -> {event_type}")
    print(f"TIME: {log_entry['timestamp']}")
    print(f"SOURCE: {log_entry['source']}")
    print(f"DESTINATION: {log_entry['destination']}")
    print(f"FILE: {log_entry['file_name']}")
    print(f"USER: {log_entry['user']}")
    print(f"STATUS: {log_entry['status']}")
    print(f"ALERT: {log_entry['alert']}")


def get_home_folders():
    home = os.path.expanduser("~")
    folders = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Downloads"),
        os.path.join(home, "Documents")
    ]
    return [folder for folder in folders if os.path.exists(folder)]


def get_removable_drives():
    usb_drives = set()
    try:
        for part in psutil.disk_partitions(all=False):
            opts = (part.opts or "").lower()
            if "removable" in opts:
                usb_drives.add(part.mountpoint)
    except Exception as e:
        print("USB detection error:", e)
    return usb_drives


class USBEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or should_ignore(event.src_path):
            return
        add_log("FILE_COPIED_TO_USB", "-", event.src_path, "UNAUTHORIZED", "New file detected on USB drive")

    def on_modified(self, event):
        if event.is_directory or should_ignore(event.src_path):
            return
        add_log("FILE_MODIFIED_ON_USB", event.src_path, event.src_path, "UNAUTHORIZED", "File modified on USB drive")

    def on_deleted(self, event):
        if event.is_directory or should_ignore(event.src_path):
            return
        add_log("FILE_DELETED_ON_USB", event.src_path, "-", "UNAUTHORIZED", "File deleted from USB drive")

    def on_moved(self, event):
        if event.is_directory or should_ignore(event.src_path) or should_ignore(event.dest_path):
            return
        add_log("FILE_MOVED_ON_USB", event.src_path, event.dest_path, "UNAUTHORIZED", "File moved or renamed on USB drive")


class LaptopEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or should_ignore(event.src_path):
            return

        if CONNECTED_USB_DRIVES:
            add_log("FILE_RECEIVED_FROM_USB", "-", event.src_path, "UNAUTHORIZED", "Possible file received from USB to laptop")
        else:
            add_log("FILE_CREATED", "-", event.src_path, "AUTHORIZED", "File created on laptop")

    def on_modified(self, event):
        if event.is_directory or should_ignore(event.src_path):
            return
        add_log("FILE_MODIFIED", event.src_path, event.src_path, "AUTHORIZED", "File modified on laptop")

    def on_deleted(self, event):
        if event.is_directory or should_ignore(event.src_path):
            return
        add_log("FILE_DELETED", event.src_path, "-", "AUTHORIZED", "File deleted on laptop")

    def on_moved(self, event):
        if event.is_directory or should_ignore(event.src_path) or should_ignore(event.dest_path):
            return
        add_log("FILE_MOVED", event.src_path, event.dest_path, "AUTHORIZED", "File moved or renamed on laptop")


def start_usb_watcher(drive):
    if drive in USB_WATCHERS:
        return

    try:
        observer = Observer()
        observer.schedule(USBEventHandler(), drive, recursive=True)
        observer.start()
        USB_WATCHERS[drive] = observer

        add_log("USB_INSERTED", "-", drive, "CONNECTED", "USB drive inserted")
        print("Started watching USB:", drive)
    except Exception as e:
        print("Could not watch USB:", drive, e)


def stop_usb_watcher(drive):
    observer = USB_WATCHERS.get(drive)
    if observer:
        observer.stop()
        observer.join(timeout=3)
        del USB_WATCHERS[drive]

    add_log("USB_REMOVED", drive, "-", "DISCONNECTED", "USB drive removed")
    print("Stopped watching USB:", drive)


def monitor_usb_changes():
    global CONNECTED_USB_DRIVES
    previous_drives = set()

    while True:
        current_drives = get_removable_drives()
        inserted = current_drives - previous_drives
        removed = previous_drives - current_drives

        for drive in inserted:
            CONNECTED_USB_DRIVES.add(drive)
            start_usb_watcher(drive)

        for drive in removed:
            CONNECTED_USB_DRIVES.discard(drive)
            stop_usb_watcher(drive)

        previous_drives = current_drives
        time.sleep(2)


def start_laptop_watchers():
    folders = get_home_folders()
    for folder in folders:
        try:
            observer = Observer()
            observer.schedule(LaptopEventHandler(), folder, recursive=True)
            observer.start()
            SYSTEM_WATCHERS.append(observer)
            print("Watching laptop folder:", folder)
        except Exception as e:
            print("Could not watch folder:", folder, e)


def main():
    ensure_log_file()

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, indent=4)

    print("Starting Secure File Monitoring System")
    print("Log file path:", LOG_FILE)
    print("Current user:", get_current_user())

    start_laptop_watchers()

    usb_thread = threading.Thread(target=monitor_usb_changes, daemon=True)
    usb_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitors...")
        for observer in SYSTEM_WATCHERS:
            observer.stop()
        for observer in SYSTEM_WATCHERS:
            observer.join()

        for drive, observer in list(USB_WATCHERS.items()):
            observer.stop()
            observer.join()

        print("Stopped.")


if __name__ == "__main__":
    main()
