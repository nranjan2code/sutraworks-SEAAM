from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import json
import os
from datetime import datetime

logger = get_logger("soma.memory.journal")

class JournalOrgan:
    def __init__(self):
        self.log_file_path = os.path.join(config.paths.soma, "journal.json")
        bus.subscribe('file_system.change', self.on_file_change)
        self.load_journal()

    def load_journal(self):
        if not os.path.exists(self.log_file_path):
            self.journal = []
        else:
            with open(self.log_file_path, 'r') as file:
                try:
                    self.journal = json.load(file)
                except json.JSONDecodeError:
                    logger.error("Failed to decode journal file. Starting with an empty journal.")
                    self.journal = []

    def save_journal(self):
        with open(self.log_file_path, 'w') as file:
            json.dump(self.journal, file, indent=4)

    def on_file_change(self, event):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event.event_type,
            "data": event.data
        }
        self.journal.append(entry)
        self.save_journal()
        logger.info(f"Logged event: {entry}")

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = JournalOrgan()