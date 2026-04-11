import os
import time
import json
import psutil
import hashlib
import getpass
import threading
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_FILE = "logs.json"
USB_WATCHERS = {}
SYSTEM_WATCHERS = []
CONNECTED_USB_DRIVES = set()


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
        if file_path and os.path.isfile(file_path):
            return os.path.getsize(file_path)
    except Exception:
        pass
    return 0


def path_exists(path):
    try:
        return os.path.exists(path)
    except Exception:
        return False


def is_subpath(child_path, parent_path):
    try:
        child_abs = os.path.abspath(child_path).lower()
        parent_abs = os.path.abspath(parent_path).lower()
        return child_abs.startswith(parent_abs)
    except Exception:
        return False


def get_file_name(path):
    try:
        return os.path.basename(path) if path and path != "-" else "-"
    except Exception:
        return "-"


def add_log(event_type, source, destination, status, alert):
    logs = load_logs()

    target_for_metadata = destination if destination and destination != "-" else source
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event_type,
        "source": source if source else "-",
        "destination": destination if destination else "-",
        "file_name": get_file_name(target_for_metadata),
        "user": get_current_user(),
        "status": status,
        "file_size": get_file_size(target_for_metadata),
        "hash": calculate_file_hash(target_for_metadata),
        "alert": alert
    }

    logs.insert(0, log_entry)
    save_logs(logs)

    print("=" * 60)
    print(f"TIME: {log_entry['timestamp']}")
    print(f"EVENT: {log_entry['event']}")
    print(f"SOURCE: {log_entry['source']}")
    print(f"DESTINATION: {log_entry['destination']}")
    print(f"FILE: {log_entry['file_name']}")
    print(f"USER: {log_entry['user']}")
    print(f"STATUS: {log_entry['status']}")
    print(f"SIZE: {log_entry['file_size']}")
    print(f"HASH: {log_entry['hash']}")
    print(f"ALERT: {log_entry['alert']}")


def get_home_folders():
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "Desktop"),
        os.path.join(home, "Downloads"),
        os.path.join(home, "Documents"),
    ]
    return [folder for folder in candidates if os.path.exists(folder)]


def get_removable_drives():
    usb_drives = set()

    try:
        partitions = psutil.disk_partitions(all=False)
        for part in partitions:
            opts = part.opts.lower()
            device = (part.device or "").lower()
            mountpoint = part.mountpoint

            if "removable" in opts:
                usb_drives.add(mountpoint)
            elif "cdrom" in opts:
                continue
            elif device.startswith("\\\\?\\usb") or "usb" in device:
                usb_drives.add(mountpoint)
    except Exception:
        pass

    return usb_drives


class USBEventHandler(FileSystemEventHandler):
    def __init__(self, usb_root):
        super().__init__()
        self.usb_root = os.path.abspath(usb_root)

    def on_created(self, event):
        if event.is_directory:
            return

        add_log(
            event_type="FILE_COPIED_TO_USB",
            source="-",
            destination=event.src_path,
            status="UNAUTHORIZED",
            alert="New file detected on USB drive"
        )

    def on_modified(self, event):
        if event.is_directory:
            return

        add_log(
            event_type="FILE_MODIFIED_ON_USB",
            source=event.src_path,
            destination=event.src_path,
            status="UNAUTHORIZED",
            alert="File modified on USB drive"
        )

    def on_deleted(self, event):
        if event.is_directory:
            return

        add_log(
            event_type="FILE_DELETED_ON_USB",
            source=event.src_path,
            destination="-",
            status="UNAUTHORIZED",
            alert="File deleted from USB drive"
        )

    def on_moved(self, event):
        if event.is_directory:
            return

        add_log(
            event_type="FILE_MOVED_ON_USB",
            source=event.src_path,
            destination=event.dest_path,
            status="UNAUTHORIZED",
            alert="File moved or renamed on USB drive"
        )


class LaptopEventHandler(FileSystemEventHandler):
    def __init__(self, watched_folder):
        super().__init__()
        self.watched_folder = os.path.abspath(watched_folder)

    def on_created(self, event):
        if event.is_directory:
            return

        event_type = "FILE_CREATED"
        alert = "File created on laptop"
        status = "AUTHORIZED"

        for usb_drive in CONNECTED_USB_DRIVES:
            # If USB is connected, newly created file on laptop may be received from USB
            event_type = "FILE_RECEIVED_FROM_USB"
            alert = "Possible file received from USB to laptop"
            status = "UNAUTHORIZED"
            break

        add_log(
            event_type=event_type,
            source="-",
            destination=event.src_path,
            status=status,
            alert=alert
        )

    def on_modified(self, event):
        if event.is_directory:
            return

        add_log(
            event_type="FILE_MODIFIED",
            source=event.src_path,
            destination=event.src_path,
            status="AUTHORIZED",
            alert="File modified on laptop"
        )

    def on_deleted(self, event):
        if event.is_directory:
            return

        add_log(
            event_type="FILE_DELETED",
            source=event.src_path,
            destination="-",
            status="AUTHORIZED",
            alert="File deleted from laptop"
        )

    def on_moved(self, event):
        if event.is_directory:
            return

        add_log(
            event_type="FILE_MOVED",
            source=event.src_path,
            destination=event.dest_path,
            status="AUTHORIZED",
            alert="File moved or renamed on laptop"
        )


def start_usb_watcher(usb_drive):
    if usb_drive in USB_WATCHERS:
        return

    try:
        handler = USBEventHandler(usb_drive)
        observer = Observer()
        observer.schedule(handler, usb_drive, recursive=True)
        observer.start()
        USB_WATCHERS[usb_drive] = observer

        add_log(
            event_type="USB_INSERTED",
            source="-",
            destination=usb_drive,
            status="CONNECTED",
            alert="USB drive inserted"
        )

        print(f"[USB WATCHING STARTED] {usb_drive}")
    except Exception as e:
        print(f"[USB WATCH ERROR] {usb_drive}: {e}")


def stop_usb_watcher(usb_drive):
    observer = USB_WATCHERS.get(usb_drive)
    if observer:
        try:
            observer.stop()
            observer.join(timeout=3)
        except Exception:
            pass
        del USB_WATCHERS[usb_drive]

    add_log(
        event_type="USB_REMOVED",
        source=usb_drive,
        destination="-",
        status="DISCONNECTED",
        alert="USB drive removed"
    )

    print(f"[USB WATCHING STOPPED] {usb_drive}")


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
            if drive in CONNECTED_USB_DRIVES:
                CONNECTED_USB_DRIVES.remove(drive)
            stop_usb_watcher(drive)

        previous_drives = current_drives
        time.sleep(3)


def start_laptop_watchers():
    folders = get_home_folders()

    for folder in folders:
        try:
            handler = LaptopEventHandler(folder)
            observer = Observer()
            observer.schedule(handler, folder, recursive=True)
            observer.start()
            SYSTEM_WATCHERS.append(observer)
            print(f"[LAPTOP WATCHING] {folder}")
        except Exception as e:
            print(f"[WATCH ERROR] {folder}: {e}")


def main():
    ensure_log_file()

    print("Starting Secure File Monitoring System...")
    print(f"Detected user: {get_current_user()}")

    watched_folders = get_home_folders()
    if watched_folders:
        print("Watching laptop folders:")
        for folder in watched_folders:
            print(f" - {folder}")
    else:
        print("No standard folders found to watch.")

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

        print("Monitoring stopped.")


if __name__ == "__main__":
    main()
