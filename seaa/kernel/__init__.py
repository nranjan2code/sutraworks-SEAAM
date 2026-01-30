# SEAA Kernel
# The immutable core of the self-evolving system

from seaa.kernel.genesis import Genesis
from seaa.kernel.bus import bus, Event, subscribe, publish, create_event
from seaa.kernel.assimilator import Assimilator
from seaa.kernel.materializer import Materializer
from seaa.kernel.immunity import Immunity
from seaa.kernel.identity import (
    IdentityManager,
    InstanceIdentity,
    IdentityCorruptedError,
    get_identity,
    get_identity_manager,
    set_name,
    get_instance_id,
    get_instance_name,
)
from seaa.kernel.beacon import Beacon, get_beacon, get_vitals, is_healthy
from seaa.kernel.observer import Observer, get_observer, stream_events, get_timeline
from seaa.kernel.protocols import (
    Observable,
    LocalObservable,
    MeshDiscoverable,
    Vitals,
    OrganInfo,
    OrganHealth,
    GoalInfo,
    FailureInfo,
    MeshNodeInfo,
)

__all__ = [
    # Genesis
    "Genesis",
    # EventBus
    "bus",
    "Event",
    "subscribe",
    "publish",
    "create_event",
    # Core components
    "Assimilator",
    "Materializer",
    "Immunity",
    # Identity
    "IdentityManager",
    "InstanceIdentity",
    "IdentityCorruptedError",
    "get_identity",
    "get_identity_manager",
    "set_name",
    "get_instance_id",
    "get_instance_name",
    # Beacon
    "Beacon",
    "get_beacon",
    "get_vitals",
    "is_healthy",
    # Observer
    "Observer",
    "get_observer",
    "stream_events",
    "get_timeline",
    # Protocols
    "Observable",
    "LocalObservable",
    "MeshDiscoverable",
    "Vitals",
    "OrganInfo",
    "OrganHealth",
    "GoalInfo",
    "FailureInfo",
    "MeshNodeInfo",
]
