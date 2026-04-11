from sender import send_log
from monitor import start_monitor
from classifier import is_sensitive
from hashing import get_hash
from auth import check_user
from logger import log_event
from usb_monitor import monitor_usb
import threading
import time


# 🔥 PROCESS FILE EVENTS
def process_event(event_type, file_pathsend):

    print("\n==============================")
    print(f"📂 Event: {event_type} -> {file_path}")

    # STEP 2 (Hidden classification logic)
    sensitive = is_sensitive(file_path)

    # 🔐 Hashing
    print("\n🔐 Hashing")
    file_hash = get_hash(file_path)
    print("Hash:", file_hash)

    # 👤 Authorization
    print("\n👤 User Check")
    user, authorized = check_user()
    status = "AUTHORIZED" if authorized else "UNAUTHORIZED"
    print("User:", user, "| Status:", status)

    # 🚨 Alerts & Decision
    print("\n🚨 Alerts")

    # Sensitive file copied
    if sensitive and event_type == "CREATED":
        print("🚨 ALERT: Sensitive data copied outside the organization!")

    # Malware-like modification
    if event_type == "MODIFIED":
        print("⚠ WARNING: Possible malware activity detected!")

    # USB transfer detection
    if file_path.startswith(("E:\\", "F:\\", "G:\\")):
        print("🔌 ALERT: Unauthorized USB transfer detected!")
        if sensitive:
            print("🔥 CRITICAL: Sensitive file copied to USB!")

    # Unauthorized user
    if not authorized:
        print("🚨 ALERT: Unauthorized data movement detected!")

    # Integrity issue
    if file_hash == "FILE_NOT_FOUND":
        print("❌ Integrity violation detected!")

    # 📝 Log event
    data = {
        "event": event_type,
        "file": file_path,
        "user": user,
        "status": status,
        "hash": file_hash
    }

    log_event(data)
    send_log(data) 

# 🔌 USB EVENT HANDLER
def usb_event(event_type, drive):
    print("\n==============================")
    print(f"🔌 USB EVENT: {event_type} -> {drive}")


# 🚀 MAIN FUNCTION
def main():
    print("🚀 START SYSTEM")

    # 👉 Change this path if needed
    path = r"C:\Users\Ganesh\Desktop"

    # Start file monitoring
    observer = start_monitor(path, process_event)

    # Start USB monitoring (parallel thread)
    usb_thread = threading.Thread(target=monitor_usb, args=(usb_event,))
    usb_thread.daemon = True
    usb_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 END SYSTEM")
        observer.stop()

    observer.join()


# ▶ START PROGRAM
if __name__ == "__main__":
    main()
