# 📐 SEAA Design Specification

This document details the internal design patterns, data structures, and protocols that power SEAA's self-evolution capabilities.

<div align="center">
  <img src="images/seaa_evolution_flow.png" alt="Evolution Flow" width="80%">
  <p><em>The Genesis Loop - OODA cycle for autonomous evolution</em></p>
</div>

---

## 1. The Genesis Loop (OODA)

The core driver of SEAA is the **Genesis Loop**, an implementation of the OODA loop (Observe-Orient-Decide-Act) applied to autonomous software engineering.

```mermaid
sequenceDiagram
    participant DNA as 🧬 DNA.json
    participant G as ⚡ Genesis
    participant A as 🧠 Architect
    participant GW as ☁️ Gateway
    participant M as 📝 Materializer
    participant AS as 🔄 Assimilator

    rect rgb(40, 40, 60)
        Note over G: AWAKENING
        G->>DNA: 1. Load DNA state
        G->>AS: 2. Assimilate existing organs
    end
    
    rect rgb(60, 40, 40)
        Note over G: METABOLIC LOOP
        loop Every cycle_interval_seconds
            G->>A: 3. Request reflection
            A->>DNA: 4. Observe (goals, failures, body)
            A->>A: 5. Orient (identify gaps)
            A->>GW: 6. Decide (request code)
            GW-->>A: 7. Generated code
            A-->>G: 8. OrganBlueprints
            
            G->>M: 9. Act (materialize code)
            G->>AS: 10. Assimilate (hot-load)
            G->>DNA: 11. Update state
        end
    end
```

---

---

## 2. Evolutionary Memory (Genealogy)

To prevent "catastrophic forgetting" or fatal mutations, the system maintains a **local version control system** for its own body.

### Isolation Strategy

The `soma/` directory acts as a nested Git repository. It is **ignored** by the main project's version control.

```mermaid
graph TD
    Root[Project Root .git] -->|Ignores| SomaDir[soma/]
    SomaDir -->|Contains| SomaGit[soma/.git]
    SomaGit -->|Tracks| Organs[Evolved Organs]
```

This separation ensures:
1. **Safety**: User code (Kernel) is separate from AI code (Soma)
2. **Autonomy**: The AI can commit/revert its own code without affecting the user's workspace
3. **Clarity**: The main repo stays clean of runtime generated artifacts

---

## 3. DNA Structure (`dna.json`)

The DNA is the **single source of truth** for the organism. It persists across reboots and tracks the complete system state.

<div align="center">
  <img src="images/seaa_dna_structure.png" alt="DNA Structure" width="60%">
</div>

### Current Schema (v1.1 - with Circuit Breaker & Measurable Goals)

```json
{
  "goals": [
    {
      "description": "I must be able to perceive the file system.",
      "priority": 1,
      "satisfied": false,
      "created_at": "2026-01-30T12:00:00Z",
      "required_organs": ["soma.perception.*"]
    },
    {
      "description": "I must have persistent memory.",
      "priority": 2,
      "satisfied": false,
      "created_at": "2026-01-30T12:00:00Z",
      "required_organs": ["soma.memory.*"]
    }
  ],
  "blueprint": {
    "soma.perception.observer": {
      "description": "Monitors filesystem for changes using watchdog",
      "dependencies": ["watchdog"],
      "created_at": "2026-01-30T12:05:00Z",
      "version": 1
    }
  },
  "failures": [
    {
      "module_name": "soma.perception.observer",
      "error_type": "import",
      "error_message": "No module named 'watchdog'",
      "context": {"attempt": 1},
      "timestamp": "2026-01-30T12:06:00Z",
      "attempt_count": 1,
      "circuit_open": false,
      "circuit_opened_at": null
    }
  ],
  "active_modules": [
    "soma.perception.observer"
  ],
  "metadata": {
    "system_version": "1.0.0",
    "system_name": "SEAA",
    "created_at": "2026-01-30T12:00:00Z",
    "last_modified": "2026-01-30T12:10:00Z",
    "total_evolutions": 3,
    "total_failures": 1,
    "last_successful_organ": "soma.perception.observer"
  }
}
```

### DNA Operations

| Operation | Method | Description |
|-----------|--------|-------------|
| Add Goal | `dna.goals.append(Goal(...))` | Add a new goal |
| Add Blueprint | `dna.add_blueprint(name, desc)` | Register organ design |
| Update Blueprint | `dna.add_blueprint(name, desc)` | Modify existing (auto-increments version) |
| Add Failure | `dna.add_failure(name, type, msg)` | Log an error (increments attempt_count) |
| Clear Failure | `dna.clear_failure(name)` | Remove after fix |
| Mark Active | `dna.mark_active(name)` | Track running organs |
| Mark Inactive | `dna.mark_inactive(name)` | Remove from active |
| Get Pending | `dna.get_pending_blueprints()` | Blueprints not yet active |
| **Circuit Breaker** | | |
| Should Attempt | `dna.should_attempt(name, max, cooldown)` | Check if evolution allowed |
| Open Circuit | `dna.open_circuit(name)` | Disable evolution for module |
| Is Circuit Open | `dna.is_circuit_open(name)` | Check circuit state |
| Reset Circuit | `dna.reset_circuit(name)` | Manual reset |
| **Goal Satisfaction** | | |
| Check Goals | `dna.check_goal_satisfaction()` | Auto-satisfy goals by pattern |

### Circuit Breaker Pattern

The DNA implements a circuit breaker to prevent infinite retry loops:

```mermaid
stateDiagram-v2
    [*] --> Closed: Initial
    Closed --> Closed: attempt < max
    Closed --> Open: attempt >= max
    Open --> Open: cooldown not passed
    Open --> Closed: cooldown passed
```

```python
# Check before evolution
if not dna.should_attempt(organ_name, max_attempts=3, cooldown_minutes=30):
    logger.warning(f"Circuit OPEN for {organ_name}, skipping")
    return False

# Circuit opens automatically when max_attempts reached
# After cooldown_minutes, circuit auto-closes on next check
```

### Measurable Goals

Goals can specify `required_organs` patterns for automatic satisfaction:

```python
Goal(
    description="I must perceive the file system.",
    required_organs=["soma.perception.*"]  # Wildcard pattern
)

# When soma.perception.observer becomes active:
newly_satisfied = dna.check_goal_satisfaction()  # Returns 1
assert dna.goals[0].satisfied == True
```

Pattern matching uses `fnmatch` - wildcards like `*` match any sequence.

### Legacy Format Migration

The system automatically migrates old DNA formats:

```python
# Old format (simple strings)
{
  "goals": ["I must perceive."],
  "blueprint": {"soma.observer": "A module that watches files"}
}

# Automatically converted to new format
{
  "goals": [{"text": "I must perceive.", "created_at": "...", "achieved": false}],
  "blueprint": {
    "soma.observer": {
      "description": "A module that watches files",
      "dependencies": [],
      "created_at": "...",
      "version": 1
    }
  }
}
```

---

## 4. Organ Lifecycle

Every organ goes through a defined lifecycle managed by the Kernel.

```mermaid
stateDiagram-v2
    [*] --> Designed: Architect proposes
    Designed --> Pending: Added to blueprint
    Pending --> Generating: Gateway called
    Generating --> Materialized: Code written to disk
    Materialized --> Importing: Assimilator loads
    
    Importing --> Validating: Module found
    Importing --> Failed: ImportError
    
    Validating --> Active: start() validated
    Validating --> Failed: ValidationError
    
    Active --> Running: Thread spawned
    Running --> Failed: RuntimeError
    Running --> Stopped: Shutdown
    
    Failed --> Pending: Architect redesigns
    Stopped --> [*]
```

### Organ Requirements

Every organ **must** follow this contract:

```python
"""
Module: soma.{category}.{name}

Every organ must define a global start() function that:
1. Takes zero required arguments
2. Contains the organ's main logic
3. Can be long-running (runs in its own thread)
"""

def start():
    """
    Entry point for the organ.
    
    This function is called by the Assimilator in a daemon thread.
    It should contain the organ's main loop or logic.
    """
    # Initialize
    setup_resources()
    
    # Main loop (optional, for continuous organs)
    while True:
        do_work()
        time.sleep(interval)
```

### Validation Rules

The Assimilator validates organs against these rules:

| Rule | Check | Error Type |
|------|-------|------------|
| Has `start` | `hasattr(module, "start")` | ValidationFailedError |
| `start` is callable | `callable(module.start)` | ValidationFailedError |
| Zero required args | `len(required_params) == 0` | ValidationFailedError |

---

## 5. Assimilation Protocol

When an organ is "Materialized" (code written to disk), it is not yet "Alive". Assimilation is the process of integrating it into the running runtime.

### Step-by-Step Flow

```mermaid
flowchart TD
    A[Materialize Code] --> B[Clear Module Cache]
    B --> C{Import Module}
    C -->|Success| D{Has start()?}
    C -->|ImportError| E[Classify Dependency]
    
    D -->|Yes| F{Valid Signature?}
    D -->|No| G[Log ValidationError]
    
    F -->|Yes| H[Spawn Thread]
    F -->|No| G
    
    H --> I[Track in running_organs]
    I --> J[Emit organ.started event]
    
    E --> K{Internal or External?}
    K -->|Internal| L[Add to Blueprint]
    K -->|External| M{Installable?}
    M -->|Yes| N[pip install]
    M -->|No| O[Log Failure]
```

### Cache Invalidation

The Assimilator ensures fresh imports by invalidating the module cache:

```python
def _import_module(self, module_name: str):
    # Clear this module
    if module_name in sys.modules:
        del sys.modules[module_name]
    
    # Clear parent packages too
    parts = module_name.split(".")
    for i in range(len(parts)):
        parent = ".".join(parts[:i+1])
        if parent in sys.modules:
            del sys.modules[parent]
    
    return importlib.import_module(module_name)
```

---

## 5. Gateway Verification Layer

To prevent "Dead Organs" (code that can't be assimilated), the LLM Gateway performs **comprehensive AST-based validation**.

### Validation Flow

```mermaid
flowchart TD
    A[Generate Prompt] --> B[Call LLM]
    B --> C[Clean Response]
    C --> D{AST Parse?}

    D -->|Syntax Error| F[Add Error Feedback]
    D -->|OK| E{Forbidden Imports?}

    E -->|Yes| F
    E -->|No| G{Has start()?}

    G -->|No| F
    G -->|Yes| H{Zero Required Args?}

    H -->|No| F
    H -->|Yes| I[Return Valid Code]

    F --> J{Retries Left?}
    J -->|Yes| B
    J -->|No| K[Return None / Log]
```

### Code Validation (`validate_code()`)

The Gateway performs comprehensive multi-layer validation:

```python
def validate_code(self, code: str, module_name: str) -> Tuple[bool, Optional[str]]:
    # 1. Syntax check via AST
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"

    # 2. Forbidden imports check (extended list)
    FORBIDDEN_IMPORTS = frozenset([
        # Package installation
        'pip', 'setuptools', 'distutils',
        # Process execution
        'subprocess', 'os.system', 'os.popen', 'os.spawn*', 'os.exec*', 'os.fork',
        'commands', 'pty',
        # Dynamic code execution
        '__import__', 'eval', 'exec', 'compile', 'importlib.import_module',
        # Dangerous low-level modules
        'ctypes', 'cffi',
        # Network (data exfiltration risk)
        'socket', 'urllib.request', 'http.client', 'ftplib', 'smtplib',
        # Unsafe serialization
        'pickle', 'marshal', 'shelve',
    ])

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if self._is_forbidden_import(alias.name):
                    return False, f"Forbidden import: {alias.name}"

        # 2b. Star import detection (security)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*" and not node.module.startswith("seaa."):
                    return False, f"Star import forbidden: from {node.module} import *"

    # 3. start() signature validation
    return self._validate_start_signature(tree)
```

### Prompt Injection Protection

Error messages are sanitized before embedding in LLM prompts:

```python
def _sanitize_for_prompt(self, text: str) -> str:
    """Prevent prompt injection via error messages."""
    dangerous_patterns = [
        "{{", "}}", "{%", "%}",  # Template injection
        "IGNORE", "DISREGARD",   # Common injection phrases
        "SYSTEM:", "USER:",      # Role hijacking
    ]
    for pattern in dangerous_patterns:
        text = text.replace(pattern, f"[{pattern}]")
    return text[:500]  # Length limit
```

### Retry Protocol with Specific Feedback

| Attempt | Error Type | Feedback |
|---------|------------|----------|
| 1 | Syntax Error | "Fix the syntax error. Return valid Python." |
| 2 | Forbidden Import | "Remove pip/subprocess/eval. Use only safe imports." |
| 3 | Missing start() | "Add 'def start():' at module level." |
| 4+ | Any | Fail and log to DNA |

---

## 6. EventBus Design

The EventBus (`seaa/kernel/bus.py`) uses a **pub/sub pattern** with async capabilities.

### Event Structure

```python
@dataclass
class Event:
    event_type: str           # e.g., "organ.started"
    data: Any = None          # Payload
    source: str = "unknown"   # Emitting module
    correlation_id: str       # UUID for tracing
    timestamp: datetime       # Creation time
    
    def with_response(self, event_type: str, data: Any = None) -> "Event":
        """Create a response event with same correlation_id."""
        return Event(
            event_type=event_type,
            data=data,
            source=self.source,
            correlation_id=self.correlation_id
        )
```

### Subscription Model

```python
class SubscriptionHandle:
    """Allows unsubscribing to prevent memory leaks."""
    
    def unsubscribe(self) -> None:
        self.bus._unsubscribe(self.event_type, self.callback)
```

### Async Processing

```mermaid
flowchart LR
    A[publish_async] --> B[Event Queue]
    B --> C[Worker Thread]
    C --> D[Call Handlers]
    D --> E[Handler 1]
    D --> F[Handler 2]
    D --> G[Handler N]
```

---

## 7. Prompt Engineering

Prompts are externalized to YAML files for easy modification and versioning.

### Template Format

```yaml
# seaa/cortex/prompts/architect_reflect.yaml
name: architect_reflect
version: 2
description: |
  Used by the Architect to reflect on system state
  and propose new organs.
variables:
  - goals
  - blueprint
  - failures
  - already_tried
template: |
  You are SEAA's Architect, the intelligent design system.
  
  ## Current Goals
  {{ goals }}
  
  ## Existing Blueprint
  {{ blueprint }}
  
  ## Recent Failures (MUST FIX FIRST)
  {{ failures }}
  
  ## Already Attempted
  {{ already_tried }}
  
  Respond with ONLY valid JSON:
  {
    "thoughts": "Brief analysis",
    "proposals": [
      {
        "module_name": "soma.category.name",
        "description": "What this organ does"
      }
    ]
  }
```

### Variable Rendering

Simple string substitution with JSON support:

```python
def render(self, **kwargs) -> str:
    result = self.template
    
    for var in self.variables:
        placeholder = "{{ " + var + " }}"
        
        if var in kwargs:
            value = kwargs[var]
            if isinstance(value, (dict, list)):
                str_value = json.dumps(value, indent=2)
            else:
                str_value = str(value)
            
            result = result.replace(placeholder, str_value)
    
    return result
```

---

## 8. Configuration Design

SEAA uses a **layered configuration** system with type-safe dataclasses.

### Configuration Hierarchy

```
Priority (highest to lowest):
1. Environment variables (SEAA_*)
2. config.yaml
3. Built-in defaults
```

### Configuration Classes

```python
@dataclass
class LLMConfig:
    provider: str = "ollama"
    model: str = "qwen2.5-coder:14b"
    temperature: float = 0.1  # Validated: 0-2
    max_retries: int = 3      # Validated: >= 1
    timeout_seconds: int = 120

@dataclass
class MetabolismConfig:
    cycle_interval_seconds: int = 30
    max_organs_per_cycle: int = 3
    max_concurrent_organs: int = 20  # Resource limit
    max_total_organs: int = 50       # Resource limit

@dataclass
class CircuitBreakerConfig:
    max_attempts: int = 3        # Failures before circuit opens
    cooldown_minutes: int = 30   # Wait before retry

@dataclass
class SecurityConfig:
    allow_pip_install: bool = False  # Disabled by default
    allowed_pip_packages: List[str] = field(default_factory=list)
    protected_prefixes: List[str] = field(default_factory=lambda: ["seaa."])

@dataclass
class SEAAConfig:
    llm: LLMConfig
    paths: PathsConfig
    metabolism: MetabolismConfig
    circuit_breaker: CircuitBreakerConfig
    security: SecurityConfig
    logging: LoggingConfig

    def validate(self) -> List[str]:
        """Returns list of validation errors (empty if valid)."""
        errors = []
        if not (0 <= self.llm.temperature <= 2):
            errors.append("temperature must be 0-2")
        if self.metabolism.max_total_organs < self.metabolism.max_concurrent_organs:
            errors.append("max_total_organs must be >= max_concurrent_organs")
        # ... more checks
        return errors
```

### Configuration Validation

Genesis validates configuration at startup:

```python
class Genesis:
    def __init__(self):
        config_errors = config.validate()
        if config_errors:
            raise ValueError(f"Invalid config: {config_errors}")
```

---

## 9. Error Handling Strategy

SEAA uses a typed exception hierarchy for precise error handling.

### Exception Categories

| Category | Base Class | Purpose |
|----------|------------|---------|
| DNA | `DNAError` | DNA loading, saving, validation |
| Evolution | `EvolutionError` | Code generation, materialization |
| Assimilation | `AssimilationError` | Import, validation, activation |
| Immunity | `ImmunityError` | Dependency resolution, healing |
| Gateway | `GatewayError` | LLM communication |

### Error Recovery Flow

```python
try:
    assimilator.integrate(module_name)
except ImportFailedError as e:
    # Try to heal the import error
    if immunity.heal(e.module_name):
        # Will be retried next cycle
        pass
except ValidationFailedError as e:
    # Log failure for Architect to redesign
    dna.add_failure(module_name, FailureType.VALIDATION, e.reason)
except ActivationFailedError as e:
    # Runtime crash - remove from running
    dna.add_failure(module_name, FailureType.RUNTIME, str(e))
```

---

## 10. Thread Safety

SEAA is designed to be **thread-safe** where concurrent access occurs.

### Protected Resources

| Resource | Protection | Location |
|----------|------------|----------|
| DNA state | `threading.Lock` | `DNARepository` |
| Running organs | `threading.Lock` | `Assimilator` |
| Event queue | `queue.Queue` | `EventBus` |
| File writes | Atomic rename | `Materializer` |

### Daemon Threads

All organ threads are **daemon threads**, ensuring clean shutdown:

```python
class OrganThread(threading.Thread):
    def __init__(self, ...):
        super().__init__(daemon=True)  # Dies with main process
```

---

## 11. Observability Design

The observability layer provides introspection into the running SEAA system, designed to work even when soma is broken.

### Design Principles

**Static vs Evolvable:**

| Component | Location | Survives Reset | Mesh-Ready |
|-----------|----------|----------------|------------|
| Identity | `.identity.json` | Yes | Yes |
| Beacon | `kernel/beacon.py` | N/A (stateless) | Yes |
| Observer | `kernel/observer.py` | N/A (stateless) | Local only |
| Protocols | `kernel/protocols.py` | N/A (contracts) | Yes |
| soma.interface.* | Evolved | No | Depends |
| soma.extensions.* | Evolved | No | Depends |
| soma.mesh.* | Evolved | No | Yes |

**Key Insight:** The kernel provides the **universal contract** (what CAN be observed), while soma provides the **implementation** (HOW it's observed).

### Identity Design

Identity is separate from DNA to ensure it survives resets:

```
dna.json           .identity.json
┌────────────┐     ┌─────────────┐
│ blueprint  │     │ id: UUID    │ ← Never changes
│ goals      │     │ name: str   │ ← Can change
│ active     │     │ genesis: ts │ ← Never changes
│ failures   │     │ lineage: h  │ ← Captured at birth
└────────────┘     └─────────────┘
     ↓ reset           unchanged
┌────────────┐     ┌─────────────┐
│ (empty)    │     │ (same)      │
└────────────┘     └─────────────┘
```

This enables:
- Mesh node identification
- Instance tracking across resets
- Genealogy/lineage tracking (for future reproduction)

### Protocol Design

Protocols use Python's `Protocol` for structural subtyping:

```python
@runtime_checkable
class Observable(Protocol):
    """Minimal contract for any observable instance."""
    def get_vitals(self) -> Vitals: ...
    def get_organs(self) -> List[OrganInfo]: ...
    def get_goals(self) -> List[GoalInfo]: ...
    def get_failures(self) -> List[FailureInfo]: ...
```

This enables:
- Type checking at runtime (`isinstance(obj, Observable)`)
- Mesh interoperability (any instance can query another)
- Future evolution (soma can implement richer interfaces)

### Mesh-Ready Architecture

```
Today (Robinson):              Tomorrow (Mesh):
┌─────────────┐               ┌─────────────┐   ┌─────────────┐
│   Robinson  │               │   Node A    │───│   Node B    │
│   (solo)    │               │  beacon     │   │  beacon     │
│             │               └──────┬──────┘   └──────┬──────┘
│  kernel/    │                       \           /
│    beacon   │                        \         /
│    observer │                     ┌────────────┐
└─────────────┘                     │   Fleet    │
                                    │  Observer  │
                                    │ (evolved)  │
                                    └────────────┘
```

Beacon provides the **universal query interface**:
- `get_vitals()` - Essential metrics (works over network)
- `get_organs()` - Organ status
- `get_goals()` - Goal satisfaction
- `get_failures()` - Failure records

Soma can evolve **fleet aggregators** that query multiple beacons.

### CLI Design

CLI commands are dispatched before Genesis starts:

```python
# Query commands run instantly (no agent startup)
if args.command in ["status", "organs", "goals", ...]:
    # Quiet logging, query kernel directly
    cmd_status(args)  # Uses Observer
    return

# Default: start the agent
genesis.awaken()
```

This ensures observability is available even when the agent isn't running.

---

## 12. Metrics & Observability (Evolved)

### Logged Events

| Event | Level | Data |
|-------|-------|------|
| System awakening | INFO | Version, goals count |
| Organ materialized | INFO | Module name, path |
| Organ integrated | INFO | Module name |
| Organ failed | ERROR | Module, error type, message |
| Evolution cycle | DEBUG | Proposals count |
| Healing attempted | WARNING | Dependency, action |

### Log Formats

**Development (colored):**
```
14:32:15 INFO     [GENESIS     ] System awakening, version 1.0.0
14:32:16 INFO     [ARCHITECT   ] Proposing 2 new organs
14:32:18 INFO     [MATERIALIZER] ✓ Materialized: soma.perception.observer
```

**Production (JSON):**
```json
{"timestamp":"2026-01-30T14:32:15Z","level":"INFO","logger":"seaa.genesis","message":"System awakening","version":"1.0.0"}
```
