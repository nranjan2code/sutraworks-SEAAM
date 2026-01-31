from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = get_logger("soma.perception.file_system_observer")

class FileSystemObserverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        self.publish_event('file.modified', event)

    def on_created(self, event):
        self.publish_event('file.created', event)

    def on_deleted(self, event):
        self.publish_event('file.deleted', event)

    def on_moved(self, event):
        self.publish_event('file.moved', event)

    def publish_event(self, event_type, event):
        metadata = {
            'path': event.src_path,
            'type': event.event_type,
            'timestamp': time.time()
        }
        if hasattr(event, 'dest_path'):
            metadata['destination'] = event.dest_path
        bus.publish(Event(event_type=event_type, data=metadata))

class FileSystemObserver:
    def __init__(self):
        self.observer = Observer()
        self.handler = FileSystemObserverHandler()
        self.path_to_watch = getattr(config, 'file_system_observer.path', '/')

    def start(self):
        logger.info(f"Starting file system observer for path: {self.path_to_watch}")
        self.observer.schedule(self.handler, self.path_to_watch, recursive=True)
        self.observer.start()

    def stop(self):
        logger.info("Stopping file system observer")
        self.observer.stop()
        self.observer.join()

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = FileSystemObserver()
    try:
        organ.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        organ.stop()