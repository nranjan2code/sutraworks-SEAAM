"""
SEAA DNA Repository

Persistent storage for DNA with:
- Atomic writes (prevent corruption)
- Automatic backups
- Validation on load/save
- Thread-safe operations
"""

import json
import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, Union, List

from seaa.core.logging import get_logger
from seaa.core.exceptions import (
    DNANotFoundError,
    DNACorruptedError,
    DNAValidationError,
)
from seaa.dna.schema import DNA

logger = get_logger("dna.repository")


class DNARepository:
    """
    Thread-safe persistence layer for DNA.
    
    Features:
    - Atomic writes (write to temp, then rename)
    - Automatic backups before modification
    - Validation on load/save
    - Change notification callbacks
    """
    
    def __init__(
        self,
        dna_path: Union[Path, str],
        backup_dir: Optional[Union[Path, str]] = None,
        max_backups: int = 10,
    ):
        self.dna_path = Path(dna_path)
        self.backup_dir = Path(backup_dir) if backup_dir else self.dna_path.parent / ".dna_backups"
        self.max_backups = max_backups
        self._lock = threading.RLock()
        self._change_callbacks: list[Callable[[DNA], None]] = []
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> DNA:
        """
        Load DNA from disk.
        
        Raises:
            DNANotFoundError: If file doesn't exist
            DNACorruptedError: If file contains invalid JSON
            DNAValidationError: If JSON doesn't match schema
        """
        with self._lock:
            if not self.dna_path.exists():
                logger.warning(f"DNA file not found: {self.dna_path}")
                raise DNANotFoundError(
                    f"DNA file not found: {self.dna_path}",
                    context={"path": str(self.dna_path)}
                )
            
            try:
                with open(self.dna_path, "r") as f:
                    raw_data = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"DNA file corrupted: {e}")
                raise DNACorruptedError(
                    f"DNA file contains invalid JSON: {e}",
                    context={"path": str(self.dna_path), "error": str(e)}
                )
            
            try:
                dna = DNA.from_dict(raw_data)
                logger.debug(f"Loaded DNA: {dna.system_name} v{dna.system_version}")
                return dna
            except Exception as e:
                logger.error(f"DNA validation failed: {e}")
                raise DNAValidationError(
                    f"DNA schema validation failed: {e}",
                    context={"path": str(self.dna_path), "error": str(e)}
                )
    
    def save(self, dna: DNA) -> None:
        """
        Save DNA to disk atomically.
        
        1. Create backup of existing file
        2. Write to temporary file
        3. Atomic rename to target
        """
        with self._lock:
            # Backup existing file
            if self.dna_path.exists():
                self._create_backup()
            
            # Update metadata
            dna.metadata.last_modified = datetime.utcnow().isoformat() + "Z"
            
            # Write to temp file
            temp_path = self.dna_path.with_suffix(".tmp")
            try:
                with open(temp_path, "w") as f:
                    json.dump(dna.to_dict(), f, indent=2)
                
                # Atomic rename
                temp_path.rename(self.dna_path)
                logger.debug(f"Saved DNA to {self.dna_path}")
                
                # Notify callbacks
                for callback in self._change_callbacks:
                    try:
                        callback(dna)
                    except Exception as e:
                        logger.warning(f"Change callback failed: {e}")
                
            except Exception as e:
                # Clean up temp file on failure
                if temp_path.exists():
                    temp_path.unlink()
                raise
    
    def _create_backup(self) -> None:
        """Create a timestamped backup of the current DNA."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"dna_{timestamp}.json"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(self.dna_path, backup_path)
        logger.debug(f"Created backup: {backup_path}")
        
        # Prune old backups
        self._prune_backups()
    
    def _prune_backups(self) -> None:
        """Remove old backups beyond max_backups limit."""
        backups = sorted(self.backup_dir.glob("dna_*.json"))
        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            oldest.unlink()
            logger.debug(f"Pruned old backup: {oldest}")
    
    def load_or_create(self, default_goals: Optional[List[str]] = None) -> DNA:
        """
        Load existing DNA or create fresh tabula rasa.
        """
        try:
            return self.load()
        except DNANotFoundError:
            logger.info("Creating fresh DNA (tabula rasa)")
            dna = DNA.create_tabula_rasa(default_goals)
            self.save(dna)
            return dna
    
    def on_change(self, callback: Callable[[DNA], None]) -> Callable[[], None]:
        """
        Register a callback for DNA changes.
        
        Returns:
            Unsubscribe function
        """
        self._change_callbacks.append(callback)
        
        def unsubscribe():
            if callback in self._change_callbacks:
                self._change_callbacks.remove(callback)
        
        return unsubscribe
    
    def list_backups(self) -> list[Path]:
        """List all available backup files."""
        return sorted(self.backup_dir.glob("dna_*.json"), reverse=True)
    
    def restore_backup(self, backup_path: Union[Path, str]) -> DNA:
        """
        Restore DNA from a backup file.
        
        Creates a backup of current state before restoring.
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise DNANotFoundError(
                f"Backup file not found: {backup_path}",
                context={"path": str(backup_path)}
            )
        
        with self._lock:
            # Backup current state first
            if self.dna_path.exists():
                self._create_backup()
            
            # Copy backup to main location
            shutil.copy2(backup_path, self.dna_path)
            logger.info(f"Restored DNA from backup: {backup_path}")
            
            return self.load()
    
    def export_for_architect(self, dna: DNA) -> dict:
        """
        Export DNA in a format optimized for Architect prompts.
        
        This is a simplified view focusing on what the Architect needs.
        """
        return {
            "goals": [g.description for g in dna.goals if not g.satisfied],
            "blueprint": {
                name: bp.description
                for name, bp in dna.blueprint.items()
            },
            "active_modules": dna.active_modules,
            "failures": [
                {
                    "module": f.module_name,
                    "error": f.error_message,
                    "attempts": f.attempt_count,
                }
                for f in dna.failures
            ],
        }
