"""
SEAA Observable Protocols

Defines the contracts that any SEAA instance must implement
to be observable. These protocols enable:

1. Local observation (this instance)
2. Remote observation (mesh queries)
3. Fleet aggregation (multiple instances)

Protocols are the UNIVERSAL CONTRACT - they work whether
you're querying locally or across a mesh network.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional, Iterator, Protocol, runtime_checkable
from enum import Enum


class OrganHealth(str, Enum):
    """Health status of an organ."""
    HEALTHY = "healthy"           # Running normally
    DEGRADED = "degraded"         # Running but has failures
    SICK = "sick"                 # Circuit breaker open
    STOPPED = "stopped"           # Not running


@dataclass
class OrganInfo:
    """
    Information about a single organ.

    This is the universal representation used by all observers.
    """
    name: str
    health: OrganHealth
    active: bool                  # Currently running?
    failure_count: int
    last_error: Optional[str]
    circuit_open: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "health": self.health.value,
            "active": self.active,
            "failure_count": self.failure_count,
            "last_error": self.last_error,
            "circuit_open": self.circuit_open,
        }


@dataclass
class GoalInfo:
    """
    Information about a goal.

    Used for querying goal satisfaction status.
    """
    description: str
    priority: int
    satisfied: bool
    required_organs: List[str]
    matching_organs: List[str]  # Which active organs satisfy this goal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "priority": self.priority,
            "satisfied": self.satisfied,
            "required_organs": self.required_organs,
            "matching_organs": self.matching_organs,
        }


@dataclass
class FailureInfo:
    """
    Information about a failure.

    Simplified view of failure records for observation.
    """
    module: str
    error_type: str
    message: str
    attempts: int
    circuit_open: bool
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Vitals:
    """
    Essential health metrics for an instance.

    This is the MINIMAL data needed to assess instance health.
    Designed for mesh protocols - lightweight and universal.
    """
    instance_id: str
    instance_name: str
    alive: bool
    uptime_seconds: float
    dna_hash: str               # Integrity check
    organ_count: int
    healthy_organs: int
    sick_organs: int            # Circuit breaker open
    pending_blueprints: int
    goals_satisfied: int
    goals_total: int
    total_evolutions: int
    total_failures: int
    last_evolution: Optional[str]  # ISO timestamp

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @property
    def health_ratio(self) -> float:
        """Ratio of healthy to total organs."""
        if self.organ_count == 0:
            return 1.0
        return self.healthy_organs / self.organ_count

    @property
    def goal_progress(self) -> float:
        """Ratio of satisfied to total goals."""
        if self.goals_total == 0:
            return 1.0
        return self.goals_satisfied / self.goals_total


@runtime_checkable
class Observable(Protocol):
    """
    Protocol for observable SEAA instances.

    Any class implementing this protocol can be observed,
    whether it's a local instance or a remote proxy.
    """

    def get_vitals(self) -> Vitals:
        """
        Get essential health metrics.

        This is the minimal query - works over network.
        """
        ...

    def get_organs(self) -> List[OrganInfo]:
        """
        Get status of all organs.
        """
        ...

    def get_goals(self) -> List[GoalInfo]:
        """
        Get all goals with satisfaction status.
        """
        ...

    def get_failures(self) -> List[FailureInfo]:
        """
        Get current failure records.
        """
        ...


@runtime_checkable
class LocalObservable(Observable, Protocol):
    """
    Extended protocol for local observation.

    Adds capabilities only available when observing locally:
    - Event streaming (requires EventBus access)
    - Timeline queries
    - Real-time updates
    """

    def stream_events(self, patterns: Optional[List[str]] = None) -> Iterator[Any]:
        """
        Stream events in real-time.

        Only available locally (requires EventBus access).
        """
        ...

    def get_timeline(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent evolution timeline.
        """
        ...


@dataclass
class MeshNodeInfo:
    """
    Information about a node in the mesh.

    Used for mesh discovery and coordination.
    """
    instance_id: str
    instance_name: str
    endpoint: str             # How to reach this node (URL, etc.)
    last_seen: str            # ISO timestamp
    vitals: Optional[Vitals]  # Cached vitals if available

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "instance_id": self.instance_id,
            "instance_name": self.instance_name,
            "endpoint": self.endpoint,
            "last_seen": self.last_seen,
        }
        if self.vitals:
            result["vitals"] = self.vitals.to_dict()
        return result


@runtime_checkable
class MeshDiscoverable(Protocol):
    """
    Protocol for mesh-discoverable instances.

    Instances implementing this can participate in mesh networks.
    """

    def announce(self) -> MeshNodeInfo:
        """
        Announce this instance to the mesh.

        Returns information other nodes need to find us.
        """
        ...

    def discover(self) -> List[MeshNodeInfo]:
        """
        Discover other instances in the mesh.
        """
        ...

    def query_remote(self, node: MeshNodeInfo) -> Optional[Vitals]:
        """
        Query a remote node's vitals.
        """
        ...
