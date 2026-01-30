"""
SEAA Beacon

The minimal health endpoint that any instance exposes.
Implements the Observable protocol for mesh interoperability.

This is the IMMUTABLE observation layer:
- Always works, even when soma is broken
- Provides universal query interface
- Enables mesh coordination

The Beacon answers: "Is this instance alive? What's its state?"
"""

import fnmatch
import hashlib
import threading
import time
from pathlib import Path
from typing import List, Optional, Union

from seaa.core.logging import get_logger
from seaa.dna.repository import DNARepository
from seaa.dna.schema import DNA
from seaa.kernel.identity import get_identity, InstanceIdentity
from seaa.kernel.protocols import (
    Observable,
    Vitals,
    OrganInfo,
    OrganHealth,
    GoalInfo,
    FailureInfo,
)

logger = get_logger("beacon")


class Beacon(Observable):
    """
    The immutable health beacon for a SEAA instance.

    Implements Observable protocol - can be queried by:
    - Local CLI commands
    - Local evolved interfaces (soma.interface.*)
    - Remote mesh nodes
    - Fleet aggregators

    This class ONLY reads state, never modifies it.
    """

    # Default cache TTL in seconds (short enough to catch changes, long enough to avoid thrashing)
    DEFAULT_CACHE_TTL = 1.0

    def __init__(
        self,
        dna_path: Union[Path, str] = "dna.json",
        start_time: Optional[float] = None,
        cache_ttl: float = DEFAULT_CACHE_TTL,
    ):
        self._dna_path = Path(dna_path)
        self._repo = DNARepository(dna_path, verify_integrity=False)  # Read-only, skip write checks
        self._start_time = start_time or time.time()
        self._dna_unavailable = False  # Track if DNA is unavailable
        self._last_dna_error: Optional[str] = None

        # DNA caching for efficient queries
        self._cache_ttl = cache_ttl
        self._cached_dna: Optional[DNA] = None
        self._cache_time: float = 0.0
        self._cache_lock = threading.Lock()

        logger.debug("Beacon initialized")

    def _load_dna(self) -> DNA:
        """Load current DNA state with caching."""
        with self._cache_lock:
            now = time.time()
            if self._cached_dna is not None and (now - self._cache_time) < self._cache_ttl:
                return self._cached_dna

            try:
                dna = self._repo.load()
                self._dna_unavailable = False
                self._last_dna_error = None
                self._cached_dna = dna
                self._cache_time = now
                return dna
            except Exception as e:
                self._dna_unavailable = True
                self._last_dna_error = str(e)
                self._cached_dna = DNA()
                self._cache_time = now
                logger.warning(f"DNA unavailable: {e}")
                return self._cached_dna

    def invalidate_cache(self) -> None:
        """Invalidate the DNA cache to force a fresh load."""
        with self._cache_lock:
            self._cached_dna = None
            self._cache_time = 0.0

    def _compute_dna_hash(self) -> str:
        """Compute current DNA hash for integrity check."""
        try:
            if self._dna_path.exists():
                content = self._dna_path.read_bytes()
                return hashlib.sha256(content).hexdigest()[:16]
            return "no-file"
        except Exception:
            return "error"

    def is_dna_available(self) -> bool:
        """Check if DNA was successfully loaded."""
        return not self._dna_unavailable

    def get_dna_error(self) -> Optional[str]:
        """Get the last DNA load error, if any."""
        return self._last_dna_error

    def _get_organ_health(self, module_name: str, dna: DNA) -> OrganHealth:
        """Determine health status of an organ."""
        for failure in dna.failures:
            if failure.module_name == module_name:
                if failure.circuit_open:
                    return OrganHealth.SICK
                elif failure.attempt_count > 0:
                    return OrganHealth.DEGRADED
        return OrganHealth.HEALTHY

    def _matches_pattern(self, module: str, patterns: List[str]) -> bool:
        """Check if module matches any of the patterns."""
        for pattern in patterns:
            if fnmatch.fnmatch(module, pattern):
                return True
        return False

    # =========================================
    # Observable Protocol Implementation
    # =========================================

    def get_vitals(self) -> Vitals:
        """
        Get essential health metrics.

        This is the PRIMARY query - minimal data for mesh protocols.
        """
        identity = get_identity()
        dna = self._load_dna()

        # Count healthy vs sick organs
        sick_count = sum(1 for f in dna.failures if f.circuit_open)
        healthy_count = len(dna.active_modules) - sick_count

        # Count satisfied goals
        satisfied_count = sum(1 for g in dna.goals if g.satisfied)

        return Vitals(
            instance_id=identity.id,
            instance_name=identity.name,
            alive=True,
            uptime_seconds=time.time() - self._start_time,
            dna_hash=self._compute_dna_hash(),
            organ_count=len(dna.active_modules),
            healthy_organs=max(0, healthy_count),
            sick_organs=sick_count,
            pending_blueprints=len(dna.get_pending_blueprints()),
            goals_satisfied=satisfied_count,
            goals_total=len(dna.goals),
            total_evolutions=dna.metadata.total_evolutions,
            total_failures=dna.metadata.total_failures,
            last_evolution=dna.metadata.last_modified,
        )

    def get_organs(self) -> List[OrganInfo]:
        """
        Get status of all organs.

        Returns both active and failed organs for complete visibility.
        """
        dna = self._load_dna()
        result: List[OrganInfo] = []

        # Build failure lookup
        failure_map = {f.module_name: f for f in dna.failures}

        # Active organs
        for module in dna.active_modules:
            failure = failure_map.get(module)
            health = self._get_organ_health(module, dna)

            result.append(OrganInfo(
                name=module,
                health=health,
                active=True,
                failure_count=failure.attempt_count if failure else 0,
                last_error=failure.error_message if failure else None,
                circuit_open=failure.circuit_open if failure else False,
            ))

        # Failed organs not in active (circuit breaker opened before activation)
        for module, failure in failure_map.items():
            if module not in dna.active_modules:
                result.append(OrganInfo(
                    name=module,
                    health=OrganHealth.SICK if failure.circuit_open else OrganHealth.STOPPED,
                    active=False,
                    failure_count=failure.attempt_count,
                    last_error=failure.error_message,
                    circuit_open=failure.circuit_open,
                ))

        return result

    def get_goals(self) -> List[GoalInfo]:
        """
        Get all goals with satisfaction status.

        Includes which organs match each goal's required_organs patterns.
        """
        dna = self._load_dna()
        result: List[GoalInfo] = []

        for goal in sorted(dna.goals, key=lambda g: g.priority):
            # Find matching active organs
            matching = []
            for module in dna.active_modules:
                if self._matches_pattern(module, goal.required_organs):
                    matching.append(module)

            result.append(GoalInfo(
                description=goal.description,
                priority=goal.priority,
                satisfied=goal.satisfied,
                required_organs=goal.required_organs,
                matching_organs=matching,
            ))

        return result

    def get_failures(self) -> List[FailureInfo]:
        """
        Get current failure records.

        Only returns modules with active failures (attempt_count > 0 or circuit_open).
        """
        dna = self._load_dna()
        result: List[FailureInfo] = []

        for failure in dna.failures:
            if failure.attempt_count > 0 or failure.circuit_open:
                result.append(FailureInfo(
                    module=failure.module_name,
                    error_type=failure.error_type.value if hasattr(failure.error_type, 'value') else str(failure.error_type),
                    message=failure.error_message[:200],  # Truncate for safety
                    attempts=failure.attempt_count,
                    circuit_open=failure.circuit_open,
                    timestamp=failure.timestamp,
                ))

        return result

    # =========================================
    # Additional Beacon Methods
    # =========================================

    def get_identity(self) -> InstanceIdentity:
        """Get the instance identity."""
        return get_identity()

    def is_healthy(self) -> bool:
        """Quick health check - are there any sick organs?"""
        vitals = self.get_vitals()
        return vitals.sick_organs == 0

    def get_pending_work(self) -> List[str]:
        """Get list of pending blueprints (organs waiting to be evolved)."""
        dna = self._load_dna()
        return list(dna.get_pending_blueprints().keys())


# Convenience: Module-level singleton
_beacon: Optional[Beacon] = None
_beacon_lock = threading.Lock()


def get_beacon(
    dna_path: Union[Path, str] = "dna.json",
    start_time: Optional[float] = None,
) -> Beacon:
    """Get or create the beacon singleton (thread-safe)."""
    global _beacon
    if _beacon is None:
        with _beacon_lock:
            if _beacon is None:  # Double-check locking
                _beacon = Beacon(dna_path, start_time)
    return _beacon


def get_vitals() -> Vitals:
    """Get vitals from the beacon."""
    return get_beacon().get_vitals()


def is_healthy() -> bool:
    """Quick health check."""
    return get_beacon().is_healthy()
