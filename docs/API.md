# 📖 API Reference

Complete API documentation for SEAA internal modules.

---

## Table of Contents

1. [Core Module](#core-module)
2. [DNA Module](#dna-module)
3. [Kernel Module](#kernel-module)
4. [Cortex Module](#cortex-module)
5. [Connectors Module](#connectors-module)

---

## Core Module

Located in `seaa/core/`

### Logging (`seaa.core.logging`)

```python
from seaa.core.logging import get_logger, setup_logging, LogContext
```

#### `get_logger(name: str) -> logging.Logger`

Get a logger for a specific component.

```python
logger = get_logger("my_module")
logger.info("Hello world")
# Output: 14:32:15 INFO     [MY_MODULE   ] Hello world
```

#### `setup_logging(level: str, format_type: str, log_file: Optional[str]) -> None`

Configure the root SEAA logger.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | str | "INFO" | DEBUG, INFO, WARNING, ERROR |
| `format_type` | str | "colored" | "colored" or "json" |
| `log_file` | Optional[str] | None | Optional file path for logs |

```python
setup_logging(level="DEBUG", format_type="json", log_file="seaa.log")
```

#### `LogContext`

Context manager for adding extra fields to log messages.

```python
with LogContext(logger, request_id="abc123", user="admin"):
    logger.info("Processing request")
# JSON output: {..., "request_id": "abc123", "user": "admin"}
```

---

### Configuration (`seaa.core.config`)

```python
from seaa.core.config import config, SEAAConfig
```

#### `config` (Global Instance)

Pre-loaded configuration singleton.

```python
# Access configuration values
model = config.llm.model
allow_pip = config.security.allow_pip_install
log_level = config.logging.level
```

#### `SEAAConfig`

Configuration dataclass with nested config objects.

| Attribute | Type | Description |
|-----------|------|-------------|
| `llm` | `LLMConfig` | LLM provider settings |
| `paths` | `PathsConfig` | File path settings |
| `metabolism` | `MetabolismConfig` | Evolution cycle settings + resource limits |
| `circuit_breaker` | `CircuitBreakerConfig` | Circuit breaker settings |
| `security` | `SecurityConfig` | Security settings |
| `logging` | `LoggingConfig` | Logging settings |

```python
# Load custom configuration
custom_config = SEAAConfig.load("custom.yaml")

# Access nested config
print(custom_config.llm.model)
print(custom_config.security.allow_pip_install)
print(custom_config.circuit_breaker.max_attempts)  # 3
print(custom_config.metabolism.max_total_organs)   # 50

# Validate configuration
errors = custom_config.validate()
if errors:
    print(f"Invalid config: {errors}")
```

---

### Exceptions (`seaa.core.exceptions`)

```python
from seaa.core.exceptions import (
    SEAAError,
    DNAError,
    DNAValidationError,
    EvolutionError,
    AssimilationError,
    ImportFailedError,
    ValidationFailedError,
    ImmunityError,
    KernelProtectionError,
    GatewayError,
)
```

All exceptions inherit from `SEAAError` and support context:

```python
raise DNAValidationError("Invalid goal format", context={"goal": goal_data})
```

---

## DNA Module

Located in `seaa/dna/`

### Schema (`seaa.dna.schema`)

```python
from seaa.dna.schema import (
    DNA,
    Goal,
    OrganBlueprint,
    Failure,
    FailureType,
    DNAMetadata,
)
```

#### `DNA`

Main DNA dataclass containing all system state.

```python
# Create tabula rasa DNA with measurable goals
dna = DNA.create_tabula_rasa()
# Default goals include required_organs patterns like ["soma.perception.*"]

# Add blueprint
blueprint = dna.add_blueprint(
    name="soma.perception.observer",
    description="Watches filesystem",
    dependencies=["watchdog"]
)

# Add failure
dna.add_failure(
    module_name="soma.perception.observer",
    error_type=FailureType.IMPORT,
    message="No module named 'watchdog'"
)

# Mark as active
dna.mark_active("soma.perception.observer")

# Check goal satisfaction (auto-satisfies goals with matching required_organs)
newly_satisfied = dna.check_goal_satisfaction()  # Returns count

# Circuit breaker operations
if dna.should_attempt("soma.xyz", max_attempts=3, cooldown_minutes=30):
    # Safe to attempt evolution
    pass
else:
    # Circuit is open, skip

dna.is_circuit_open("soma.xyz")    # Check state
dna.open_circuit("soma.xyz")       # Manually open
dna.reset_circuit("soma.xyz")      # Reset to closed

# Serialize to dict
data = dna.to_dict()

# Load from dict
dna = DNA.from_dict(data)
```

#### `Goal`

Goal dataclass with optional measurable criteria.

```python
from seaa.dna.schema import Goal

goal = Goal(
    description="I must perceive the file system.",
    priority=1,
    satisfied=False,
    required_organs=["soma.perception.*"]  # Wildcard pattern
)
```

#### `FailureType`

Enum for classifying failure types.

| Value | Description |
|-------|-------------|
| `IMPORT` | ImportError during assimilation |
| `VALIDATION` | Missing start() or signature issue |
| `RUNTIME` | Exception during execution |
| `GENERATION` | LLM failed to generate valid code |
| `MATERIALIZATION` | Failed to write code to disk |

---

### Repository (`seaa.dna.repository`)

```python
from seaa.dna.repository import DNARepository
```

#### `DNARepository`

Thread-safe DNA persistence with atomic writes.

```python
repo = DNARepository(
    dna_path="dna.json",
    backup_dir="backups/"  # Optional
)

# Load or create
dna = repo.load_or_create(default_goals=["I must perceive."])

# Save with automatic backup
repo.save(dna)

# Create manual backup
backup_path = repo.backup()
```

---

## Kernel Module

Located in `seaa/kernel/`

### EventBus (`seaa.kernel.bus`)

```python
from seaa.kernel.bus import (
    EventBus,
    Event,
    bus,           # Global singleton
    subscribe,     # Module-level function
    publish,       # Module-level function
)
```

#### `Event`

Event dataclass for bus communication.

```python
event = Event(
    event_type="organ.started",
    data={"module": "soma.observer"},
    source="genesis"
)

# Create response event (preserves correlation_id)
response = event.with_response("organ.acknowledged", data="ok")
```

#### `EventBus`

Singleton event bus with async capabilities.

```python
bus = EventBus()

# Subscribe
def handler(event: Event):
    print(f"Received: {event.data}")

handle = bus.subscribe("my.event", handler)

# Publish synchronously
bus.publish(Event(event_type="my.event", data="hello"))

# Publish asynchronously (queued)
bus.start_worker()
bus.publish_async(Event(event_type="my.event", data="async"))
bus.stop_worker(drain=True)

# Unsubscribe
handle.unsubscribe()
```

#### Module-level Functions

```python
# Convenience functions using global bus
handle = subscribe("my.event", handler)
publish(Event(event_type="my.event", data="hello"))
```

---

### Assimilator (`seaa.kernel.assimilator`)

```python
from seaa.kernel.assimilator import Assimilator
```

#### `Assimilator`

Handles dynamic module loading and activation.

```python
def on_failure(module_name: str, error_type: str, message: str):
    print(f"Failed: {module_name} - {message}")

assimilator = Assimilator(on_failure=on_failure)

# Integrate a module
success = assimilator.integrate("soma.perception.observer")

# Check if running
is_running = assimilator.is_running("soma.perception.observer")

# Get all running
running = assimilator.get_running_organs()  # ["soma.perception.observer"]

# Stop tracking
assimilator.stop_organ("soma.perception.observer")

# Batch integration
results = assimilator.integrate_batch([
    "soma.perception.observer",
    "soma.memory.journal"
])  # {"soma.perception.observer": True, "soma.memory.journal": False}
```

---

### Materializer (`seaa.kernel.materializer`)

```python
from seaa.kernel.materializer import Materializer
```

#### `Materializer`

Writes organ code to filesystem with safety guarantees.

```python
materializer = Materializer(root_dir=".")

# Write code
code = '''
def start():
    print("Hello from organ!")
'''
path = materializer.materialize("soma.perception.observer", code)
# Returns: PosixPath('./soma/perception/observer.py')

# Check existence
exists = materializer.exists("soma.perception.observer")

# Read code
source = materializer.read("soma.perception.observer")

# List all organs
organs = materializer.list_organs()  # ["soma.perception.observer"]

# Delete organ
deleted = materializer.delete("soma.perception.observer")
```

---

### Immunity (`seaa.kernel.immunity`)

```python
from seaa.kernel.immunity import Immunity, DependencyClassification
```

#### `Immunity`

Error recovery and dependency resolution.

```python
def on_blueprint_needed(module_name: str, description: str):
    print(f"Need blueprint for: {module_name}")

def on_failure_report(module_name: str, error_type: FailureType, message: str):
    print(f"Reporting failure: {module_name}")

immunity = Immunity(
    root_dir=".",
    on_blueprint_needed=on_blueprint_needed,
    on_failure_report=on_failure_report
)

# Classify a dependency
classification = immunity.classify_dependency("watchdog")
print(classification.is_internal)  # False
print(classification.is_seed)      # False

# Attempt to heal
healed = immunity.heal("watchdog")
```

---

### Genesis (`seaa.kernel.genesis`)

```python
from seaa.kernel.genesis import Genesis
```

#### `Genesis`

Main orchestrator for the system lifecycle.

```python
genesis = Genesis(root_dir=".")

# Awaken the system
genesis.awaken()

# Start metabolic loop (blocking)
genesis.run()

# Graceful shutdown
genesis.shutdown()
```

---

### Identity (`seaa.kernel.identity`)

```python
from seaa.kernel.identity import (
    InstanceIdentity,
    IdentityManager,
    get_identity,
    set_name,
    get_instance_id,
    get_instance_name,
)
```

#### `InstanceIdentity`

Dataclass representing the instance's identity.

```python
@dataclass
class InstanceIdentity:
    id: str           # UUID, never changes
    name: str         # Human-friendly name
    genesis_time: str # ISO timestamp of first creation
    lineage: str      # Hash of initial DNA state
    parent_id: Optional[str] = None  # If spawned from another
```

#### Module-level Functions

```python
# Get the identity (creates if not exists)
identity = get_identity()
print(identity.id)       # "713d8815-6867-409c-87a1-a2ae27aa3276"
print(identity.name)     # "SEAA-713d8815"
print(identity.lineage)  # "56271deda1e156e0"

# Set instance name
identity = set_name("Robinson")

# Get just the ID or name
instance_id = get_instance_id()
instance_name = get_instance_name()
```

---

### Beacon (`seaa.kernel.beacon`)

```python
from seaa.kernel.beacon import Beacon, get_beacon, get_vitals, is_healthy
```

#### `Beacon`

Minimal health endpoint implementing the Observable protocol.

```python
beacon = Beacon(dna_path="dna.json")

# Get essential health metrics
vitals = beacon.get_vitals()
print(vitals.organ_count)      # 3
print(vitals.healthy_organs)   # 3
print(vitals.goals_satisfied)  # 2

# Get organ status
for organ in beacon.get_organs():
    print(f"{organ.name}: {organ.health.value}")

# Get goal satisfaction
for goal in beacon.get_goals():
    print(f"{goal.description}: {goal.satisfied}")

# Get failures
for failure in beacon.get_failures():
    print(f"{failure.module}: {failure.message}")

# Quick health check
if beacon.is_healthy():
    print("All organs healthy")
```

#### Module-level Functions

```python
# Get vitals from global beacon
vitals = get_vitals()

# Quick health check
if is_healthy():
    print("System healthy")

# Get beacon singleton
beacon = get_beacon()
```

---

### Observer (`seaa.kernel.observer`)

```python
from seaa.kernel.observer import Observer, get_observer, stream_events, get_timeline
```

#### `Observer`

Extended local observer with event streaming and timeline.

```python
observer = Observer(dna_path="dna.json")

# All Beacon methods are available
vitals = observer.get_vitals()
organs = observer.get_organs()
goals = observer.get_goals()

# Stream events in real-time (blocks)
for event in observer.stream_events():
    print(f"{event.event_type}: {event.data}")

# Stream specific event types
for event in observer.stream_events(["organ.evolved", "system.heartbeat"]):
    print(event)

# Get evolution timeline
for entry in observer.get_timeline(limit=20):
    print(f"{entry['type']}: {entry['organ']} at {entry['timestamp']}")

# Watch for DNA changes
def on_change(dna):
    print(f"DNA changed: {dna.metadata.total_evolutions} evolutions")

unsub = observer.watch_changes(on_change)
# ... later
unsub()

# Get comprehensive system summary
summary = observer.get_system_summary()
print(summary["identity"]["name"])
print(summary["health"]["status"])

# Get specific organ details
detail = observer.get_organ_detail("soma.perception.observer")
print(detail["health"])
print(detail["blueprint"]["description"])
```

#### Module-level Functions

```python
# Stream events from global observer
for event in stream_events():
    print(event)

# Get timeline
events = get_timeline(limit=10)

# Get observer singleton
observer = get_observer()
```

---

### Protocols (`seaa.kernel.protocols`)

```python
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
```

#### `Vitals`

Essential health metrics for an instance.

```python
@dataclass
class Vitals:
    instance_id: str
    instance_name: str
    alive: bool
    uptime_seconds: float
    dna_hash: str
    organ_count: int
    healthy_organs: int
    sick_organs: int
    pending_blueprints: int
    goals_satisfied: int
    goals_total: int
    total_evolutions: int
    total_failures: int
    last_evolution: Optional[str]

    @property
    def health_ratio(self) -> float:
        """Ratio of healthy to total organs."""

    @property
    def goal_progress(self) -> float:
        """Ratio of satisfied to total goals."""
```

#### `OrganHealth`

Enum for organ health status.

```python
class OrganHealth(str, Enum):
    HEALTHY = "healthy"    # Running normally
    DEGRADED = "degraded"  # Running but has failures
    SICK = "sick"          # Circuit breaker open
    STOPPED = "stopped"    # Not running
```

#### `OrganInfo`

Information about a single organ.

```python
@dataclass
class OrganInfo:
    name: str
    health: OrganHealth
    active: bool
    failure_count: int
    last_error: Optional[str]
    circuit_open: bool
```

#### `GoalInfo`

Information about a goal.

```python
@dataclass
class GoalInfo:
    description: str
    priority: int
    satisfied: bool
    required_organs: List[str]
    matching_organs: List[str]  # Active organs matching patterns
```

#### `FailureInfo`

Information about a failure.

```python
@dataclass
class FailureInfo:
    module: str
    error_type: str
    message: str
    attempts: int
    circuit_open: bool
    timestamp: str
```

#### Protocol Classes

```python
# Type checking with protocols
from seaa.kernel.protocols import Observable

def query_any_instance(obs: Observable) -> int:
    """Works with Beacon, Observer, or any Observable."""
    vitals = obs.get_vitals()
    return vitals.organ_count

# Check if an object implements Observable
if isinstance(beacon, Observable):
    print("Beacon implements Observable")
```

---

## Cortex Module

Located in `seaa/cortex/`

### Prompt Loader (`seaa.cortex.prompt_loader`)

```python
from seaa.cortex.prompt_loader import prompt_loader, PromptLoader, PromptTemplate
```

#### `prompt_loader` (Global Instance)

Pre-configured prompt loader.

```python
# Render a prompt template
prompt = prompt_loader.render(
    "architect_reflect",
    goals="I must perceive.",
    blueprint="{}",
    failures="None"
)
```

#### `PromptLoader`

Loads and caches YAML prompt templates.

```python
loader = PromptLoader(prompts_dir="custom/prompts")

# Load template
template = loader.load("architect_reflect")

# Render with variables
prompt = template.render(goals="...", blueprint="...")

# List available templates
templates = loader.list_templates()  # ["architect_reflect", "agent_factory", ...]

# Clear cache
loader.clear_cache()
```

---

### Architect (`seaa.cortex.architect`)

```python
from seaa.cortex.architect import Architect
```

#### `Architect`

System designer using LLM-based reflection.

```python
def on_code_request(prompt: str) -> str:
    # Send to LLM and return response
    return llm_response

architect = Architect(on_code_request=on_code_request)

# Reflect on DNA state
proposals = architect.reflect(dna)
# Returns list of OrganBlueprint objects
```

---

## Connectors Module

Located in `seaa/connectors/`

### LLM Gateway (`seaa.connectors.llm_gateway`)

```python
from seaa.connectors.llm_gateway import ProviderGateway
```

#### `ProviderGateway`

Abstraction layer for LLM providers with comprehensive code validation.

```python
gateway = ProviderGateway()

# Simple thinking
response = gateway.think("What is 2+2?")

# Generate organ code (with active_modules context)
code = gateway.generate_code(
    module_name="soma.perception.observer",
    description="Watches filesystem for changes",
    active_modules=["soma.memory.journal"]  # Optional context
)

# Validate code manually
is_valid, error = gateway.validate_code(code, "soma.test.module")
if not is_valid:
    print(f"Validation failed: {error}")
    # Possible errors:
    # - "Syntax error at line X: ..."
    # - "Forbidden imports/calls detected: pip, subprocess"
    # - "Missing required 'def start():' function"
    # - "start() has N required argument(s), must have zero"
```

**Forbidden Imports/Calls:**
- `pip`, `subprocess`, `os.system`, `os.popen`, `os.spawn*`, `os.exec*`
- `eval`, `exec`, `compile`, `__import__`

---

## Event Types Reference

Standard event types used throughout the system:

| Event Type | Source | Data | Description |
|------------|--------|------|-------------|
| `system.awakening` | Genesis | `{"version": "..."}` | System starting |
| `system.shutdown` | Genesis | `{}` | System stopping |
| `evolution.started` | Genesis | `{"cycle": N}` | Evolution cycle beginning |
| `evolution.completed` | Genesis | `{"organs": [...]}` | Evolution cycle finished |
| `organ.materialized` | Materializer | `{"module": "...", "path": "..."}` | Code written |
| `organ.integrated` | Assimilator | `{"module": "..."}` | Module loaded |
| `organ.failed` | Assimilator | `{"module": "...", "error": "..."}` | Module failed |
| `organ.started` | OrganThread | `{"module": "..."}` | Organ thread running |
| `healing.attempted` | Immunity | `{"package": "...", "action": "..."}` | Dependency fix |
