"""
SEAA DNA Repository

Persistent storage for DNA with:
- Atomic writes (prevent corruption)
- Automatic backups
- Validation on load/save
- Thread-safe operations
- Integrity verification (SHA-256)
"""

import hashlib
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
    - Integrity verification (SHA-256 checksums)
    """

    def __init__(
        self,
        dna_path: Union[Path, str],
        backup_dir: Optional[Union[Path, str]] = None,
        max_backups: int = 10,
        verify_integrity: bool = True,
    ):
        self.dna_path = Path(dna_path)
        self.backup_dir = Path(backup_dir) if backup_dir else self.dna_path.parent / ".dna_backups"
        self.max_backups = max_backups
        self.verify_integrity = verify_integrity
        self._lock = threading.RLock()
        self._change_callbacks: List[Callable[[DNA], None]] = []

        # Path for integrity hash file
        self._hash_path = self.dna_path.with_suffix(".sha256")

        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _compute_hash(self, content: bytes) -> str:
        """
        SECURITY: Compute SHA-256 hash of content.
        """
        return hashlib.sha256(content).hexdigest()

    def _save_hash(self, content_hash: str) -> None:
        """
        SECURITY: Save integrity hash to file.
        """
        try:
            self._hash_path.write_text(content_hash)
            logger.debug(f"Saved integrity hash: {content_hash[:16]}...")
        except Exception as e:
            logger.warning(f"Failed to save integrity hash: {e}")

    def _verify_hash(self, content: bytes) -> bool:
        """
        SECURITY: Verify content against stored hash.

        Returns:
            True if hash matches or no hash file exists (first run)
            False if hash mismatch (tampering detected)
        """
        if not self._hash_path.exists():
            logger.debug("No integrity hash file found (first run)")
            return True

        try:
            stored_hash = self._hash_path.read_text().strip()
            computed_hash = self._compute_hash(content)

            if stored_hash != computed_hash:
                logger.error(
                    f"SECURITY: DNA integrity check FAILED! "
                    f"Expected: {stored_hash[:16]}..., Got: {computed_hash[:16]}..."
                )
                return False

            logger.debug("DNA integrity check passed")
            return True
        except Exception as e:
            logger.warning(f"Failed to verify integrity: {e}")
            return True  # Allow on error to prevent lockout
    
    def load(self) -> DNA:
        """
        Load DNA from disk with integrity verification.

        SECURITY: Verifies file integrity before loading.

        Raises:
            DNANotFoundError: If file doesn't exist
            DNACorruptedError: If file contains invalid JSON or fails integrity check
            DNAValidationError: If JSON doesn't match schema
        """
        with self._lock:
            if not self.dna_path.exists():
                logger.warning(f"DNA file not found: {self.dna_path}")
                raise DNANotFoundError(
                    f"DNA file not found: {self.dna_path}",
                    context={"path": str(self.dna_path)}
                )

            # Read raw content for integrity check
            try:
                raw_content = self.dna_path.read_bytes()
            except Exception as e:
                logger.error(f"Failed to read DNA file: {e}")
                raise DNACorruptedError(
                    f"Failed to read DNA file: {e}",
                    context={"path": str(self.dna_path), "error": str(e)}
                )

            # SECURITY: Verify integrity before parsing
            if self.verify_integrity and not self._verify_hash(raw_content):
                raise DNACorruptedError(
                    "DNA file integrity check failed - possible tampering detected",
                    context={"path": str(self.dna_path)}
                )

            try:
                raw_data = json.loads(raw_content.decode('utf-8'))
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
        Save DNA to disk atomically with integrity hash.

        SECURITY: Computes and saves SHA-256 hash for integrity verification.

        1. Create backup of existing file
        2. Write to temporary file
        3. Atomic rename to target
        4. Save integrity hash
        """
        with self._lock:
            # Backup existing file
            if self.dna_path.exists():
                self._create_backup()

            # Update metadata
            dna.metadata.last_modified = datetime.utcnow().isoformat() + "Z"

            # Serialize to JSON
            json_content = json.dumps(dna.to_dict(), indent=2)
            content_bytes = json_content.encode('utf-8')

            # Write to temp file
            temp_path = self.dna_path.with_suffix(".tmp")
            try:
                with open(temp_path, "wb") as f:
                    f.write(content_bytes)

                # Atomic rename
                temp_path.rename(self.dna_path)
                logger.debug(f"Saved DNA to {self.dna_path}")

                # SECURITY: Save integrity hash
                if self.verify_integrity:
                    content_hash = self._compute_hash(content_bytes)
                    self._save_hash(content_hash)

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
    
    def recalculate_integrity_hash(self) -> Optional[str]:
        """
        SECURITY: Recalculate and save the integrity hash for current DNA file.

        Use this after legitimate external modifications to the DNA file.

        Returns:
            The new hash, or None if file doesn't exist
        """
        with self._lock:
            if not self.dna_path.exists():
                logger.warning("Cannot recalculate hash: DNA file not found")
                return None

            try:
                content = self.dna_path.read_bytes()
                new_hash = self._compute_hash(content)
                self._save_hash(new_hash)
                logger.info(f"Recalculated integrity hash: {new_hash[:16]}...")
                return new_hash
            except Exception as e:
                logger.error(f"Failed to recalculate integrity hash: {e}")
                return None

    def disable_integrity_check(self) -> None:
        """
        Temporarily disable integrity checking.

        WARNING: Only use for debugging or recovery.
        """
        logger.warning("SECURITY: Integrity checking disabled")
        self.verify_integrity = False

    def enable_integrity_check(self) -> None:
        """
        Re-enable integrity checking.
        """
        self.verify_integrity = True
        logger.info("Integrity checking enabled")

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
