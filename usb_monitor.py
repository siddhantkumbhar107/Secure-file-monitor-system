import psutil
import time

def get_usb_drives():
    drives = []
    for part in psutil.disk_partitions():
        if 'removable' in part.opts:
            drives.append(part.mountpoint)
    return drives

def monitor_usb(callback):
    print("🔌 USB Monitoring Started...")

    known = set(get_usb_drives())

    while True:
        time.sleep(2)
        current = set(get_usb_drives())

        new = current - known
        for d in new:
            print(f"🔌 USB Inserted: {d}")
            callback("USB_INSERTED", d)

        removed = known - current
        for d in removed:
            print(f"❌ USB Removed: {d}")
            callback("USB_REMOVED", d)

        known = current