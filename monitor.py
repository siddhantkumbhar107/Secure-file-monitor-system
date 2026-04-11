from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):
    def __init__(self, process_event):
        self.process_event = process_event

    def on_any_event(self, event):
        if event.is_directory:
            return
        self.process_event(event.event_type.upper(), event.src_path)

def start_monitor(path, process_event):
    observer = Observer()
    observer.schedule(Handler(process_event), path, recursive=True)
    observer.start()
    print("👀 Monitoring File System...")
    return observer