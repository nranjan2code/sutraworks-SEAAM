# 📖 API Reference

Complete API documentation for SEAAM internal modules.

---

## Table of Contents

1. [Core Module](#core-module)
2. [DNA Module](#dna-module)
3. [Kernel Module](#kernel-module)
4. [Cortex Module](#cortex-module)
5. [Connectors Module](#connectors-module)

---

## Core Module

Located in `seaam/core/`

### Logging (`seaam.core.logging`)

```python
from seaam.core.logging import get_logger, setup_logging, LogContext
```

#### `get_logger(name: str) -> logging.Logger`

Get a logger for a specific component.

```python
logger = get_logger("my_module")
logger.info("Hello world")
# Output: 14:32:15 INFO     [MY_MODULE   ] Hello world
```

#### `setup_logging(level: str, format_type: str, log_file: Optional[str]) -> None`

Configure the root SEAAM logger.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | str | "INFO" | DEBUG, INFO, WARNING, ERROR |
| `format_type` | str | "colored" | "colored" or "json" |
| `log_file` | Optional[str] | None | Optional file path for logs |

```python
setup_logging(level="DEBUG", format_type="json", log_file="seaam.log")
```

#### `LogContext`

Context manager for adding extra fields to log messages.

```python
with LogContext(logger, request_id="abc123", user="admin"):
    logger.info("Processing request")
# JSON output: {..., "request_id": "abc123", "user": "admin"}
```

---

### Configuration (`seaam.core.config`)

```python
from seaam.core.config import config, SEAAMConfig
```

#### `config` (Global Instance)

Pre-loaded configuration singleton.

```python
# Access configuration values
model = config.llm.model
allow_pip = config.security.allow_pip_install
log_level = config.logging.level
```

#### `SEAAMConfig`

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
custom_config = SEAAMConfig.load("custom.yaml")

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

### Exceptions (`seaam.core.exceptions`)

```python
from seaam.core.exceptions import (
    SEAAMError,
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

All exceptions inherit from `SEAAMError` and support context:

```python
raise DNAValidationError("Invalid goal format", context={"goal": goal_data})
```

---

## DNA Module

Located in `seaam/dna/`

### Schema (`seaam.dna.schema`)

```python
from seaam.dna.schema import (
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
from seaam.dna.schema import Goal

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

### Repository (`seaam.dna.repository`)

```python
from seaam.dna.repository import DNARepository
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

Located in `seaam/kernel/`

### EventBus (`seaam.kernel.bus`)

```python
from seaam.kernel.bus import (
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

### Assimilator (`seaam.kernel.assimilator`)

```python
from seaam.kernel.assimilator import Assimilator
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

### Materializer (`seaam.kernel.materializer`)

```python
from seaam.kernel.materializer import Materializer
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

### Immunity (`seaam.kernel.immunity`)

```python
from seaam.kernel.immunity import Immunity, DependencyClassification
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

### Genesis (`seaam.kernel.genesis`)

```python
from seaam.kernel.genesis import Genesis
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

## Cortex Module

Located in `seaam/cortex/`

### Prompt Loader (`seaam.cortex.prompt_loader`)

```python
from seaam.cortex.prompt_loader import prompt_loader, PromptLoader, PromptTemplate
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

### Architect (`seaam.cortex.architect`)

```python
from seaam.cortex.architect import Architect
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

Located in `seaam/connectors/`

### LLM Gateway (`seaam.connectors.llm_gateway`)

```python
from seaam.connectors.llm_gateway import ProviderGateway
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
