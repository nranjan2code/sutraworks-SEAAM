"""
SEAA Instance Identity

Manages the unique identity of this SEAA instance.
Identity is separate from DNA and persists across resets.

Key properties:
- id: UUID that never changes (born once)
- name: Human-friendly name (can be changed)
- genesis_time: When this instance was first created
- lineage: Hash of initial DNA (genealogy tracking)

This enables:
- Mesh node identification
- Instance tracking across resets
- Genealogy/lineage tracking
"""

import json
import hashlib
import threading
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
from uuid import uuid4

from seaa.core.logging import get_logger

logger = get_logger("identity")

# Default identity file location
DEFAULT_IDENTITY_PATH = ".identity.json"


class IdentityCorruptedError(Exception):
    """Raised when identity file exists but cannot be loaded."""
    pass


@dataclass
class InstanceIdentity:
    """
    The immutable identity of a SEAA instance.

    Unlike DNA, this persists even through total resets.
    """
    id: str                    # UUID, never changes
    name: str                  # Human-friendly name
    genesis_time: str          # ISO timestamp of first creation
    lineage: str               # Hash of initial DNA state
    parent_id: Optional[str] = None  # If spawned from another instance

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "InstanceIdentity":
        return cls(
            id=data["id"],
            name=data["name"],
            genesis_time=data["genesis_time"],
            lineage=data["lineage"],
            parent_id=data.get("parent_id"),
        )

    def short_id(self) -> str:
        """Return first 8 chars of ID for display."""
        return self.id[:8]


class IdentityManager:
    """
    Manages instance identity with thread-safe persistence.

    Identity is created once and persists forever, even
    across DNA resets. This enables mesh coordination and
    genealogy tracking.
    """

    _instance: Optional["IdentityManager"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        identity_path: Union[Path, str] = DEFAULT_IDENTITY_PATH,
        dna_path: Union[Path, str] = "dna.json",
    ):
        if self._initialized:
            return

        self._identity_path = Path(identity_path)
        self._dna_path = Path(dna_path)
        self._identity: Optional[InstanceIdentity] = None
        self._file_lock = threading.RLock()

        self._initialized = True
        logger.debug(f"IdentityManager initialized: {self._identity_path}")

    def _compute_lineage(self) -> str:
        """
        Compute lineage hash from DNA state.

        This captures the "genetic origin" of this instance.
        """
        try:
            if self._dna_path.exists():
                content = self._dna_path.read_bytes()
                return hashlib.sha256(content).hexdigest()[:16]
            return "tabula-rasa"
        except Exception as e:
            logger.warning(f"Failed to compute lineage: {e}")
            return "unknown"

    def _create_identity(self, name: Optional[str] = None) -> InstanceIdentity:
        """Create a new identity for this instance."""
        instance_id = str(uuid4())
        default_name = f"SEAA-{instance_id[:8]}"

        identity = InstanceIdentity(
            id=instance_id,
            name=name or default_name,
            genesis_time=datetime.utcnow().isoformat() + "Z",
            lineage=self._compute_lineage(),
        )

        logger.info(f"Created new identity: {identity.name} ({identity.short_id()})")
        return identity

    def _load_identity(self) -> Optional[InstanceIdentity]:
        """Load identity from disk."""
        if not self._identity_path.exists():
            return None

        try:
            with open(self._identity_path, "r") as f:
                data = json.load(f)
            return InstanceIdentity.from_dict(data)
        except Exception as e:
            # Identity file exists but is corrupted - this is critical
            logger.error(f"Identity file corrupted: {e}")
            raise IdentityCorruptedError(
                f"Identity file '{self._identity_path}' exists but cannot be loaded: {e}. "
                f"To create a new identity, delete the file or call force_recreate()."
            )

    def _save_identity(self, identity: InstanceIdentity) -> None:
        """Save identity to disk atomically."""
        temp_path = self._identity_path.with_suffix(".tmp")

        try:
            with open(temp_path, "w") as f:
                json.dump(identity.to_dict(), f, indent=2)
            temp_path.rename(self._identity_path)
            logger.debug(f"Saved identity: {identity.short_id()}")
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise

    def get_identity(self) -> InstanceIdentity:
        """
        Get the instance identity, creating if needed.

        This is the primary interface - always returns a valid identity.
        """
        with self._file_lock:
            if self._identity is not None:
                return self._identity

            # Try to load existing
            self._identity = self._load_identity()

            if self._identity is None:
                # First run - create new identity
                self._identity = self._create_identity()
                self._save_identity(self._identity)
            else:
                logger.debug(f"Loaded identity: {self._identity.name} ({self._identity.short_id()})")

            return self._identity

    def set_name(self, name: str) -> InstanceIdentity:
        """
        Change the instance name.

        The ID never changes, but the name can be updated.
        """
        with self._file_lock:
            identity = self.get_identity()
            identity.name = name
            self._save_identity(identity)
            logger.info(f"Renamed instance to: {name}")
            return identity

    def exists(self) -> bool:
        """Check if identity file exists."""
        return self._identity_path.exists()

    def force_recreate(self, name: Optional[str] = None, backup: bool = True) -> InstanceIdentity:
        """
        Force recreation of identity after corruption.

        This should only be called when identity is corrupted and
        you explicitly want to create a new one.

        Args:
            name: Optional name for the new identity
            backup: If True, rename corrupted file to .identity.json.bak
        """
        with self._file_lock:
            if self._identity_path.exists():
                if backup:
                    backup_path = self._identity_path.with_suffix(".json.bak")
                    logger.warning(f"Backing up corrupted identity to: {backup_path}")
                    self._identity_path.rename(backup_path)
                else:
                    logger.warning("Deleting corrupted identity file")
                    self._identity_path.unlink()

            # Create fresh identity
            self._identity = self._create_identity(name)
            self._save_identity(self._identity)
            logger.info(f"Recreated identity: {self._identity.name} ({self._identity.short_id()})")
            return self._identity

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton (for testing only)."""
        with cls._lock:
            if cls._instance:
                cls._instance._identity = None
                cls._instance._initialized = False
                cls._instance = None


# Convenience: Module-level singleton access
_manager: Optional[IdentityManager] = None
_manager_lock = threading.Lock()


def get_identity_manager(
    identity_path: Union[Path, str] = DEFAULT_IDENTITY_PATH,
    dna_path: Union[Path, str] = "dna.json",
) -> IdentityManager:
    """Get or create the identity manager singleton (thread-safe)."""
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:  # Double-check locking
                _manager = IdentityManager(identity_path, dna_path)
    return _manager


def get_identity() -> InstanceIdentity:
    """Get the current instance identity."""
    return get_identity_manager().get_identity()


def set_name(name: str) -> InstanceIdentity:
    """Set the instance name."""
    return get_identity_manager().set_name(name)


def get_instance_id() -> str:
    """Get just the instance ID."""
    return get_identity().id


def get_instance_name() -> str:
    """Get just the instance name."""
    return get_identity().name
