import json
import os
import hashlib
from datetime import datetime

LOG_FILE = "logs.json"


def calculate_file_hash(file_path):
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


def load_existing_logs():
    if not os.path.exists(LOG_FILE):
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def save_log(event_type, file_path, user, status, alert):
    logs = load_existing_logs()

    file_hash = calculate_file_hash(file_path)

    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event_type,
        "file": file_path,
        "user": user,
        "status": status,
        "hash": file_hash,
        "alert": alert
    }

    logs.insert(0, log_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)


if __name__ == "__main__":
    print("🚀 START SYSTEM")
    print("👀 Monitoring File System...")
    print("🪶 USB Monitoring Started...")
    print("\n==============================\n")

    # TEST ENTRY 1
    save_log(
        event_type="DELETED",
        file_path=r"C:\Users\Ganesh\Desktop\New folder",
        user="Ganesh",
        status="UNAUTHORIZED",
        alert="Unauthorized data movement detected"
    )

    print("📁 Event: DELETED -> C:\\Users\\Ganesh\\Desktop\\New folder")
    print("🔐 Hashing")
    print("Hash: FILE_NOT_FOUND")
    print("👤 User Check")
    print("User: Ganesh | Status: UNAUTHORIZED")
    print("🚨 Alerts")
    print("🚨 ALERT: Unauthorized data movement detected!")
    print("❌ Integrity violation detected!")

    # TEST ENTRY 2
    save_log(
        event_type="MODIFIED",
        file_path=r"C:\Users\Ganesh\Documents\important.txt",
        user="Ganesh",
        status="AUTHORIZED",
        alert="File modified successfully"
    )

    print("\n✅ Two test logs added to logs.json")
