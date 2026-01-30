"""
SEAA Observer

Extended local observation with features not available remotely:
- Real-time event streaming
- Evolution timeline
- DNA change notifications
- Detailed organ introspection

The Observer wraps Beacon and adds local-only capabilities.
This is what CLI commands and local evolved interfaces use.
"""

import queue
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Union, Callable

from seaa.core.logging import get_logger
from seaa.dna.repository import DNARepository
from seaa.dna.schema import DNA
from seaa.kernel.bus import bus, Event, SubscriptionHandle
from seaa.kernel.beacon import Beacon, get_beacon
from seaa.kernel.identity import get_identity
from seaa.kernel.protocols import (
    LocalObservable,
    Vitals,
    OrganInfo,
    GoalInfo,
    FailureInfo,
)

logger = get_logger("observer")


class Observer(LocalObservable):
    """
    Extended local observer for SEAA.

    Implements LocalObservable protocol, adding:
    - Event streaming (tap into EventBus)
    - Evolution timeline
    - DNA change callbacks

    Use this for local observation (CLI, local dashboards).
    For remote/mesh observation, use Beacon directly.
    """

    def __init__(
        self,
        dna_path: Union[Path, str] = "dna.json",
        start_time: Optional[float] = None,
    ):
        self._beacon = Beacon(dna_path, start_time)
        self._repo = DNARepository(dna_path, verify_integrity=False)
        self._dna_path = Path(dna_path)

        logger.debug("Observer initialized")

    # =========================================
    # Observable Protocol (delegated to Beacon)
    # =========================================

    def get_vitals(self) -> Vitals:
        """Get essential health metrics."""
        return self._beacon.get_vitals()

    def get_organs(self) -> List[OrganInfo]:
        """Get status of all organs."""
        return self._beacon.get_organs()

    def get_goals(self) -> List[GoalInfo]:
        """Get all goals with satisfaction status."""
        return self._beacon.get_goals()

    def get_failures(self) -> List[FailureInfo]:
        """Get current failure records."""
        return self._beacon.get_failures()

    # =========================================
    # LocalObservable Protocol (local-only)
    # =========================================

    def stream_events(self, patterns: Optional[List[str]] = None) -> Iterator[Event]:
        """
        Stream events in real-time.

        Yields events as they occur. Blocks until stopped.
        Use patterns to filter (e.g., ["organ.*", "system.*"]).

        Usage:
            for event in observer.stream_events():
                print(event)
        """
        event_queue: queue.Queue = queue.Queue()
        handles: List[SubscriptionHandle] = []

        # Default: subscribe to key system events
        if patterns is None:
            patterns = [
                "organ.evolved",
                "organ.integrated",
                "system.heartbeat",
            ]

        def make_handler(pattern: str):
            """Create handler that queues matching events."""
            def handler(event: Event):
                event_queue.put(event)
            return handler

        # Subscribe to each pattern
        for pattern in patterns:
            handle = bus.subscribe(pattern, make_handler(pattern))
            handles.append(handle)
            logger.debug(f"Streaming events: {pattern}")

        try:
            while True:
                try:
                    event = event_queue.get(timeout=1.0)
                    yield event
                except queue.Empty:
                    continue
        finally:
            # Cleanup subscriptions
            for handle in handles:
                handle.unsubscribe()
            logger.debug("Stopped event stream")

    def get_timeline(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent evolution timeline.

        Combines blueprint creation times and active module timestamps.
        Returns most recent events first.
        """
        try:
            dna = self._repo.load()
        except Exception:
            return []

        events: List[Dict[str, Any]] = []

        # Blueprint design events
        for name, bp in dna.blueprint.items():
            events.append({
                "type": "designed",
                "organ": name,
                "description": bp.description[:100] + "..." if len(bp.description) > 100 else bp.description,
                "timestamp": bp.created_at,
                "version": bp.version,
            })

        # Integration events (approximated from metadata)
        for name in dna.active_modules:
            bp = dna.blueprint.get(name)
            events.append({
                "type": "integrated",
                "organ": name,
                "timestamp": bp.updated_at if bp else dna.metadata.last_modified,
            })

        # Failure events
        for failure in dna.failures:
            events.append({
                "type": "failure",
                "organ": failure.module_name,
                "error": failure.error_message[:100],
                "timestamp": failure.timestamp,
                "circuit_open": failure.circuit_open,
            })

        # Sort by timestamp, most recent first
        events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)

        return events[:limit]

    # =========================================
    # Additional Observer Methods
    # =========================================

    def watch_changes(self, callback: Callable[[DNA], None]) -> Callable[[], None]:
        """
        Register callback for DNA changes.

        Returns unsubscribe function.

        Usage:
            def on_change(dna):
                print(f"DNA changed: {dna.metadata.total_evolutions} evolutions")

            unsub = observer.watch_changes(on_change)
            # ... later
            unsub()
        """
        return self._repo.on_change(callback)

    def get_blueprint_details(self, organ_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed blueprint for a specific organ."""
        try:
            dna = self._repo.load()
            bp = dna.blueprint.get(organ_name)
            if bp:
                return {
                    "name": bp.name,
                    "description": bp.description,
                    "dependencies": bp.dependencies,
                    "version": bp.version,
                    "created_at": bp.created_at,
                    "updated_at": bp.updated_at,
                }
            return None
        except Exception:
            return None

    def get_system_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive system summary.

        This is a rich view for local dashboards.
        """
        vitals = self.get_vitals()
        identity = get_identity()

        return {
            "identity": {
                "id": identity.id,
                "name": identity.name,
                "short_id": identity.short_id(),
                "genesis": identity.genesis_time,
                "lineage": identity.lineage,
            },
            "vitals": vitals.to_dict(),
            "health": {
                "status": "healthy" if vitals.sick_organs == 0 else "degraded",
                "organ_health_ratio": vitals.health_ratio,
                "goal_progress": vitals.goal_progress,
            },
            "evolution": {
                "total": vitals.total_evolutions,
                "pending": vitals.pending_blueprints,
                "failures": vitals.total_failures,
            },
        }

    def get_organ_detail(self, organ_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific organ."""
        organs = self.get_organs()
        for organ in organs:
            if organ.name == organ_name:
                # Get blueprint if exists
                blueprint = self.get_blueprint_details(organ_name)

                return {
                    "name": organ.name,
                    "health": organ.health.value,
                    "active": organ.active,
                    "failure_count": organ.failure_count,
                    "last_error": organ.last_error,
                    "circuit_open": organ.circuit_open,
                    "blueprint": blueprint,
                }
        return None

    def search_events(
        self,
        event_type: Optional[str] = None,
        organ: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search timeline events with filters.

        Args:
            event_type: Filter by type ("designed", "integrated", "failure")
            organ: Filter by organ name (supports wildcards)
            limit: Max results
        """
        import fnmatch

        timeline = self.get_timeline(limit=200)  # Get more, then filter

        results = []
        for event in timeline:
            # Filter by type
            if event_type and event.get("type") != event_type:
                continue

            # Filter by organ
            if organ and not fnmatch.fnmatch(event.get("organ", ""), organ):
                continue

            results.append(event)

            if len(results) >= limit:
                break

        return results


# Convenience: Module-level singleton
_observer: Optional[Observer] = None
_observer_lock = threading.Lock()


def get_observer(
    dna_path: Union[Path, str] = "dna.json",
    start_time: Optional[float] = None,
) -> Observer:
    """Get or create the observer singleton (thread-safe)."""
    global _observer
    if _observer is None:
        with _observer_lock:
            if _observer is None:  # Double-check locking
                _observer = Observer(dna_path, start_time)
    return _observer


def stream_events(patterns: Optional[List[str]] = None) -> Iterator[Event]:
    """Stream events from the observer."""
    return get_observer().stream_events(patterns)


def get_timeline(limit: int = 20) -> List[Dict[str, Any]]:
    """Get evolution timeline."""
    return get_observer().get_timeline(limit)


def get_system_summary() -> Dict[str, Any]:
    """Get comprehensive system summary."""
    return get_observer().get_system_summary()
