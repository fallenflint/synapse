#! env python

import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent



class ChangeHandler(FileSystemEventHandler):
    """Restart Synapse upon file change."""
    def on_modified(self, event):
        if not isinstance(event, FileModifiedEvent):
            return
        print(f"Restarting Synapse due to changes in: {event.src_path}")
        self.stop()
        self.start()

    def start(self):
        self.popen = subprocess.Popen(["poetry", "run", "python", "-m", "synapse.app.homeserver", "-c", "homeserver.yaml"])

    def stop(self):
        self.popen.kill()


if __name__ == "__main__":
    path = __file__
    event_handler = ChangeHandler()
    event_handler.start()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
