from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
from seaa.dna.repository import DNARepository
from seaa.dna.schema import DNA
import json
import threading
import time
from typing import Optional, Dict

logger = get_logger("soma.kernel.memory_keeper")

class MemoryKeeper:
    """Persistent state management for Robinson's identity and DNA.

    Ensures Robinson survives any failure by:
    - Maintaining DNA integrity (SHA-256 verification)
    - Auto-backing up state on changes
    - Detecting and preventing tampering
    - Surviving process crashes and resets
    - Keeping instance identity persistent
    """

    def __init__(self):
        self.dna_repo = DNARepository()
        self.lock = threading.Lock()
        self.last_save_time = time.time()
        self.unsaved_changes = False

        # Subscribe to important events that need persistent storage
        bus.subscribe('organ.*.started', self._on_organ_event)
        bus.subscribe('organ.*.failed', self._on_organ_event)
        bus.subscribe('goal.satisfied', self._on_goal_event)
        bus.subscribe('goal.added', self._on_goal_event)

        # Start periodic save loop to ensure durability
        threading.Thread(target=self._periodic_save_loop, daemon=True).start()

        logger.info("MemoryKeeper initialized - Robinson is now persistent")

    def _on_organ_event(self, event: Event) -> None:
        """Track organ-related events for state updates"""
        self.unsaved_changes = True

    def _on_goal_event(self, event: Event) -> None:
        """Track goal-related events for state updates"""
        self.unsaved_changes = True

    def load_dna(self) -> DNA:
        """Load DNA with integrity verification"""
        with self.lock:
            try:
                dna = self.dna_repo.load()
                logger.info("DNA loaded and verified")
                return dna
            except Exception as e:
                logger.error(
                    "Failed to load DNA",
                    error=str(e)
                )
                raise

    def save_dna(self, dna: DNA) -> bool:
        """Save DNA with integrity protection"""
        with self.lock:
            try:
                self.dna_repo.save(dna)
                self.last_save_time = time.time()
                self.unsaved_changes = False

                logger.info("DNA saved and protected")

                # Publish save event
                bus.publish(Event(
                    event_type='memory.saved',
                    data={
                        'timestamp': time.time(),
                        'organs_count': len(dna.blueprint),
                        'goals_count': len(dna.goals),
                        'integrity_verified': True
                    }
                ))

                return True
            except Exception as e:
                logger.error(
                    "Failed to save DNA",
                    error=str(e)
                )
                return False

    def get_dna_integrity_status(self) -> Dict:
        """Check DNA integrity and tampering"""
        with self.lock:
            try:
                dna = self.dna_repo.load()

                return {
                    'integrity_verified': True,
                    'hash_algorithm': 'SHA-256',
                    'organs_count': len(dna.blueprint),
                    'goals_count': len(dna.goals),
                    'active_organs': len(dna.active_modules),
                    'last_modified': dna.metadata.get('last_modified', 'unknown'),
                    'total_evolutions': dna.metadata.get('total_evolutions', 0),
                    'total_failures': dna.metadata.get('total_failures', 0)
                }
            except Exception as e:
                return {
                    'integrity_verified': False,
                    'error': str(e),
                    'last_modified': None
                }

    def backup_dna(self) -> bool:
        """Create a backup of current DNA state"""
        with self.lock:
            try:
                dna = self.dna_repo.load()

                # Create backup filename with timestamp
                backup_path = f"dna.backup.{int(time.time())}.json"

                # Save backup
                with open(backup_path, 'w') as f:
                    json.dump(dna.to_dict(), f, indent=2)

                logger.info(
                    "DNA backup created",
                    backup_path=backup_path
                )

                # Publish backup event
                bus.publish(Event(
                    event_type='memory.backup_created',
                    data={
                        'backup_path': backup_path,
                        'timestamp': time.time()
                    }
                ))

                return True
            except Exception as e:
                logger.error(
                    "Failed to backup DNA",
                    error=str(e)
                )
                return False

    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore DNA from a backup file"""
        with self.lock:
            try:
                with open(backup_path, 'r') as f:
                    backup_data = json.load(f)

                # Convert to DNA object
                dna = DNA.from_dict(backup_data)

                # Save as current DNA (this updates hash)
                self.dna_repo.save(dna)

                logger.info(
                    "DNA restored from backup",
                    backup_path=backup_path
                )

                # Publish restore event
                bus.publish(Event(
                    event_type='memory.restored_from_backup',
                    data={
                        'backup_path': backup_path,
                        'timestamp': time.time()
                    }
                ))

                return True
            except Exception as e:
                logger.error(
                    "Failed to restore from backup",
                    backup_path=backup_path,
                    error=str(e)
                )
                return False

    def _periodic_save_loop(self) -> None:
        """Periodically save DNA if there are unsaved changes"""
        save_interval = getattr(config, 'memory_save_interval_seconds', 10)
        backup_interval = getattr(config, 'memory_backup_interval_seconds', 3600)  # 1 hour

        backup_counter = 0

        while True:
            try:
                time.sleep(save_interval)

                # Save if there are unsaved changes
                if self.unsaved_changes:
                    dna = self.load_dna()
                    self.save_dna(dna)

                # Create backup periodically
                backup_counter += save_interval
                if backup_counter >= backup_interval:
                    self.backup_dna()
                    backup_counter = 0

            except Exception as e:
                logger.error("Error in periodic save loop", error=str(e))

# REQUIRED ENTRY POINT (zero required args)
def start():
    keeper = MemoryKeeper()
