# 🧬 System Architecture

SEAA is fundamentally different from traditional software architectures. Instead of a static codebase, it is a **dynamic biological system** designed to grow, heal, and evolve autonomously.

<div align="center">
  <img src="images/seaa_architecture_clean.png" alt="SEAA Architecture" width="70%">
</div>

---

## 🗺 High-Level Overview

```mermaid
graph TD
    User((User)) -->|Queries| Interface[Interface Organ]
    Interface -->|Events| Bus[Nervous System]
    Bus -->|Events| Memory[Memory Organ]
    
    subgraph KERNEL [The Immutable Seed - seaa/kernel/]
        Genesis[Genesis Orchestrator]
        Bus
        Assimilator[Assimilator]
        Materializer[Materializer]
        Immunity[Immunity System]
        Genealogy[Genealogy (Git)]
    end
    
    subgraph CORTEX [The Mind - seaa/cortex/]
        Architect[Architect] -->|Reflects| DNA[(DNA.json)]
        Architect -->|Uses| PromptLoader[Prompt Loader]
        PromptLoader -->|Loads| Prompts[YAML Templates]
    end
    
    subgraph SOMA [The Body - soma/]
        Perception[perception/]
        Memory
        Interface
    end
    
    subgraph CONNECTORS [External - seaa/connectors/]
        Gateway[LLM Gateway]
        Gateway -->|Ollama| Ollama[Local LLM]
        Gateway -->|Gemini| Gemini[Cloud LLM]
    end
    
    Genesis -->|Reads| DNA
    Genesis -->|Delegates| Assimilator
    Genesis -->|Delegates| Materializer
    Genesis -->|Delegates| Immunity
    Genesis -->|Asks| Architect
    Architect -->|Requests Code| Gateway
    Materializer -->|Writes| SOMA
    Assimilator -->|Hot-loads| SOMA
```

---

## 1. The Kernel (`seaa/kernel/`)

The Kernel is the **immutable core**—it enables life but does not dictate form. It cannot be modified by the system itself.

### `genesis.py` - The Slim Orchestrator

The "Primal Will". A lightweight coordinator (~280 LOC) that delegates all complex logic to specialized components.

**Responsibilities:**
- **Awakening**: Loads DNA, initializes components
- **Evolution**: Coordinates the reflect → design → generate → materialize → assimilate cycle
- **Lifecycle**: Signal handling, graceful shutdown
- **Event Emission**: Publishes lifecycle events to the bus

```python
# Simplified genesis flow
class Genesis:
    def __init__(self):
        self.dna_repo = DNARepository()
        self.assimilator = Assimilator(on_failure=self._handle_failure)
        self.materializer = Materializer()
        self.immunity = Immunity(on_blueprint_needed=self._request_blueprint)
        self.architect = Architect(on_code_request=self.gateway.generate_code)
        self.gateway = ProviderGateway()
    
    def awaken(self):
        self.dna = self.dna_repo.load_or_create()
        self._assimilate_existing()
        self._evolution_cycle()
```

### `bus.py` - The Nervous System

An **async-capable EventBus** that serves as the central communication mechanism.

<div align="center">
  <img src="images/seaa_event_bus.png" alt="EventBus Pattern" width="50%">
</div>

**Features:**
| Feature | Description |
|---------|-------------|
| Sync/Async | Both `publish()` (sync) and `publish_async()` (queued) |
| Unsubscribe | `handle.unsubscribe()` prevents memory leaks |
| Correlation IDs | Track event chains across the system |
| Timestamps | All events have creation timestamps |
| Backpressure | Queue-based with configurable limits |
| Graceful Shutdown | `stop_worker(drain=True)` processes remaining events |

```python
# Usage example
from seaa.kernel.bus import bus, subscribe, publish, Event

# Subscribe to events
handle = subscribe("organ.started", lambda e: print(f"Started: {e.data}"))

# Publish events
publish(Event(event_type="organ.started", data="soma.perception.observer"))

# Cleanup
handle.unsubscribe()
```

### `assimilator.py` - Module Integration

Responsible for **dynamic module loading** and thread-based activation.

**Flow:**
1. **Import**: `importlib.import_module()` with cache invalidation
2. **Validate**: Check for `start()` function with zero required args
3. **Activate**: Spawn daemon thread to run `start()`
4. **Track**: Monitor running organs

```python
class Assimilator:
    def integrate(self, module_name: str) -> bool:
        module = self._import_module(module_name)
        
        # Validation
        if not hasattr(module, "start"):
            raise ValidationFailedError(module_name, "Missing start()")
        
        # Activation
        thread = OrganThread(module_name, module.start)
        thread.start()
        self.running_organs[module_name] = thread
        return True
```

### `materializer.py` - Code Writer

Writes generated organ code to the filesystem with **safety guarantees**.

**Features:**
- **Module Name Validation**: Strict regex pattern `^soma(\.[a-z_][a-z0-9_]*)+$`
- **Path Traversal Protection**: Resolved paths verified to stay within root directory
- **Atomic Writes**: Write to temp file, then rename (prevents corruption)
- **Package Structure**: Auto-creates `__init__.py` in all directories
- **Kernel Protection**: Cannot write to `seaa/*` paths

```python
class Materializer:
    def materialize(self, module_name: str, code: str) -> Path:
        self._validate_module_name(module_name)  # Security: regex + identifier check
        self._check_protection(module_name)      # Raises if protected
        file_path = self._module_to_path(module_name)  # Includes path canonicalization
        self._ensure_package_structure(file_path.parent)
        self._atomic_write(file_path, code)
        return file_path
```

**Security Validation:**
```python
# Module names must match this pattern
MODULE_NAME_PATTERN = re.compile(r'^soma(\.[a-z_][a-z0-9_]*)+$', re.IGNORECASE)

# Path traversal detection
if ".." in module_name:
    raise MaterializationError("Path traversal detected")

# Path canonicalization
resolved_path = final_path.resolve()
resolved_path.relative_to(root_dir.resolve())  # Raises if escapes
```

### `immunity.py` - Error Recovery

The healing system for **dependency resolution** and error classification.

**Classification Logic:**
```mermaid
flowchart TD
    A[Missing Import] --> B{Starts with soma.?}
    B -->|Yes| C[Internal Organ\nRequest Evolution]
    B -->|No| D{Starts with seaa.?}
    D -->|Yes| E[Seed Error\nCannot Self-Heal]
    D -->|No| F{Known External?}
    F -->|Yes| G[pip install\nif allowed]
    F -->|No| H[Classify via Heuristics]
```

**Security:**
- Pip install disabled by default (`allow_pip_install: false`)
- Only allowlisted packages can be installed
- Pattern matching instead of hardcoded lists

---

## 2. The Cortex (`seaa/cortex/`)

The Cortex is the **intelligent reasoning layer**.

### `architect.py` - System Designer

The intelligent agent responsible for system design using **externalized prompts**.

**Responsibilities:**
- **Reflect**: Analyze DNA state (goals, failures, blueprint)
- **Design**: Propose new organs to fulfill goals
- **Learn**: Use failure history to improve designs

```python
class Architect:
    def reflect(self, dna: DNA) -> List[OrganBlueprint]:
        # Load externalized prompt
        prompt = prompt_loader.render("architect_reflect", 
            goals=dna.get_goals_text(),
            blueprint=dna.get_blueprint_summary(),
            failures=dna.get_failure_summary()
        )
        
        # Get LLM response
        response = self.on_code_request(prompt)
        
        # Parse and return blueprints
        return self._parse_response(response)
```

### `prompt_loader.py` - Template Management

Loads and renders **YAML prompt templates** with simple variable substitution.

**Features:**
- Caching for performance
- Jinja2-lite rendering (no dependency required)
- Works with or without PyYAML installed

**Template Format:**
```yaml
# seaa/cortex/prompts/architect_reflect.yaml
name: architect_reflect
version: 2
description: System reflection and design prompt
variables: [goals, blueprint, failures]
template: |
  You are SEAA's Architect. Analyze the current system state:
  
  ## Goals
  {{ goals }}
  
  ## Current Blueprint
  {{ blueprint }}
  
  ## Recent Failures
  {{ failures }}
  
  Respond with JSON only...
```

---

## 3. The Connectors (`seaa/connectors/`)

### `llm_gateway.py` - LLM Provider Abstraction

Abstracts LLM providers with **comprehensive code validation and retry logic**.

**Providers:**
| Provider | Configuration | Features |
|----------|---------------|----------|
| Ollama | `OLLAMA_URL`, `OLLAMA_MODEL` | Local, fast, default |
| Gemini | `GEMINI_API_KEY` | Cloud fallback |

**Code Validation (`validate_code()`):**
The gateway performs comprehensive AST-based validation:

1. **Syntax Check**: `ast.parse()` for Python syntax validation
2. **Forbidden Imports**: Rejects dangerous imports:
   - `pip`, `subprocess`, `os.system`, `os.popen`
   - `eval`, `exec`, `compile`, `__import__`
3. **Start Function**: Validates `start()` exists with zero required args

```python
class ProviderGateway:
    def validate_code(self, code: str, module_name: str) -> Tuple[bool, Optional[str]]:
        # 1. AST syntax check
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"

        # 2. Check forbidden imports via AST walk
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Check against FORBIDDEN_IMPORTS

        # 3. Validate start() signature
        return self._validate_start_signature(tree)

    def generate_code(self, module_name: str, description: str,
                      active_modules: Optional[List[str]] = None) -> Optional[str]:
        # Pass active_modules to LLM for context
        prompt = prompt_loader.render("agent_factory",
            module_name=module_name,
            description=description,
            active_modules=active_modules or []
        )

        for attempt in range(self.max_retries):
            code = self._call_provider(prompt)
            code = self._clean_code(code)

            is_valid, error = self.validate_code(code, module_name)
            if is_valid:
                return code

            prompt = self._add_error_feedback(prompt, error)

        return None
```

---

## 4. The DNA (`seaa/dna/`)

The DNA is the **persistent memory** of the organism.

### `schema.py` - Data Models

Pydantic-style dataclasses with validation and legacy migration.

**Core Types:**
```python
@dataclass
class Goal:
    description: str
    priority: int = 1
    satisfied: bool = False
    created_at: str
    required_organs: List[str] = []  # Patterns for auto-satisfaction, e.g., ["soma.perception.*"]

@dataclass
class OrganBlueprint:
    name: str
    description: str
    dependencies: List[str]
    created_at: str
    version: int = 1

@dataclass
class Failure:
    module_name: str
    error_type: FailureType  # IMPORT, VALIDATION, RUNTIME, GENERATION, MATERIALIZATION
    error_message: str
    timestamp: str
    attempt_count: int = 1
    context: Dict[str, Any]
    # Circuit breaker fields
    circuit_open: bool = False
    circuit_opened_at: Optional[str] = None

@dataclass
class DNA:
    goals: List[Goal]
    blueprint: Dict[str, OrganBlueprint]
    failures: List[Failure]
    active_modules: List[str]
    metadata: DNAMetadata

    # Circuit breaker methods
    def should_attempt(self, module_name: str, max_attempts: int, cooldown_minutes: int) -> bool
    def open_circuit(self, module_name: str) -> None
    def is_circuit_open(self, module_name: str) -> bool
    def reset_circuit(self, module_name: str) -> None

    # Goal satisfaction
    def check_goal_satisfaction(self) -> int  # Returns count of newly satisfied goals
```

### `repository.py` - Persistence

Thread-safe DNA persistence with **atomic writes and backups**.

**Features:**
- Atomic writes (temp file + rename)
- Automatic backups on save
- Lock-based thread safety
- Legacy format migration

---

## 5. The Core (`seaa/core/`)

Foundational infrastructure used throughout the system.

### `logging.py` - Structured Logging

Production-ready logging with **two formats**:

| Format | Use Case | Output |
|--------|----------|--------|
| `colored` | Development | Human-readable with colors |
| `json` | Production | Machine-parseable JSON |

```python
from seaa.core.logging import get_logger

logger = get_logger("genesis")
logger.info("System awakening", cycles=0, organs=5)
```

### `config.py` - Configuration Management

Layered configuration with **priority system**:

1. Built-in defaults → 2. `config.yaml` → 3. Environment variables

```python
from seaa.core.config import config

# Access configuration
model = config.llm.model
allow_pip = config.security.allow_pip_install
```

### `exceptions.py` - Typed Exception Hierarchy

```
SEAAError (base)
├── DNAError
│   ├── DNAValidationError
│   ├── DNANotFoundError
│   └── DNACorruptedError
├── EvolutionError
│   ├── BlueprintError
│   ├── CodeGenerationError
│   └── MaterializationError
├── AssimilationError
│   ├── ImportFailedError
│   ├── ValidationFailedError
│   └── ActivationFailedError
├── ImmunityError
│   ├── DependencyResolutionError
│   └── KernelProtectionError
└── GatewayError
    ├── ProviderUnavailableError
    ├── RateLimitError
    └── InvalidResponseError
```

---

## 6. The Soma (`soma/`)

The Soma is the **evolved body**—modules written by the system itself. These directories and files are created at runtime.

**Common Organs:**
- `soma/perception/observer.py` - Filesystem watcher
- `soma/memory/journal.py` - Event logging
- `soma/interface/dashboard.py` - Streamlit UI

**Organ Requirements:**
```python
# Every organ must have:
def start():
    """Zero-argument entry point."""
    # Organ logic here
    pass
```

---

## 7. Data Flow

### Evolution Cycle

```mermaid
sequenceDiagram
    participant G as Genesis
    participant A as Architect
    participant GW as Gateway
    participant M as Materializer
    participant AS as Assimilator
    participant DNA as DNA.json

    G->>DNA: Load DNA
    G->>AS: Assimilate existing organs
    
    loop Evolution Cycle
        G->>A: Request reflection
        A->>DNA: Read goals, failures
        A->>GW: Request code generation
        GW-->>A: Generated code
        A-->>G: OrganBlueprints
        
        G->>M: Materialize code
        M-->>G: File path
        
        G->>AS: Integrate module
        AS-->>G: Success/Failure
        
        G->>DNA: Update active_modules
    end
```

### Error Recovery Flow

```mermaid
sequenceDiagram
    participant AS as Assimilator
    participant IM as Immunity
    participant G as Genesis
    participant DNA as DNA.json

    AS->>AS: Import fails
    AS->>G: Report failure
    G->>IM: Classify error
    
    alt Internal Dependency
        IM->>G: Request blueprint
        G->>DNA: Add to blueprint
        Note right of G: Next cycle evolves it
    else Critical Failure (Auto-Immune)
        Note right of IM: Auto-Revert Triggered
        IM->>DNA: Log runtime failure
        IM->>G: trigger_revert()
        G->>Genealogy: revert_last()
    else External Package
        IM->>IM: Check allowlist
        alt Allowed
            IM->>IM: pip install
        else Not Allowed
            IM->>DNA: Log failure
        end
    end
```

---

## 8. Security Model

SEAA follows a **security-first** design with defense in depth:

| Protection | Mechanism |
|------------|-----------|
| Kernel Immutability | Materializer rejects writes to `seaa/*` |
| **Path Traversal Prevention** | Module names validated with regex: `^soma(\.[a-z_][a-z0-9_]*)+$` |
| **Module Name Validation** | Assimilator only imports validated `soma.*` modules |
| **Path Canonicalization** | Resolved paths verified to stay within `root_dir` |
| Code Validation | AST-based syntax + forbidden import checking |
| **Star Import Detection** | `from X import *` rejected for non-seaa modules |
| Forbidden Imports | `pip`, `subprocess`, `os.system`, `eval`, `exec`, `ctypes`, `socket`, `pickle`, etc. |
| **Prompt Injection Protection** | Error messages sanitized before embedding in LLM prompts |
| **DNA Integrity** | SHA-256 hash verification detects tampering |
| **JSON Parsing** | Proper depth tracking prevents manipulation |
| Pip Disabled | `allow_pip_install: false` by default |
| Package Allowlist | Only approved packages can be installed |
| Atomic Writes | Prevents file corruption |
| Thread Isolation | Each organ runs in its own daemon thread |
| Resource Limits | `max_concurrent_organs`, `max_total_organs` caps |
| Circuit Breaker | Failing organs auto-disabled after max attempts |
| Config Validation | Invalid configuration rejected at startup |
| **Git Config Validation** | User name/email validated before git commands |

---

## 9. Observability Layer

SEAA includes a built-in observability layer that provides introspection into the running system—even when soma is broken.

### Architecture: Static vs Evolvable

```mermaid
graph TD
    subgraph KERNEL [Kernel - Static, Always Works]
        Identity[identity.py<br/>Who am I?]
        Beacon[beacon.py<br/>Health endpoint]
        Observer[observer.py<br/>Local introspection]
        Protocols[protocols.py<br/>Observable contracts]
    end

    subgraph SOMA [Soma - Evolvable, Can Reset]
        Interface[soma.interface.*<br/>Rich dashboards]
        Extensions[soma.extensions.*<br/>Custom metrics]
        Mesh[soma.mesh.*<br/>Fleet discovery]
    end

    CLI[CLI Commands] --> Observer
    Observer --> Beacon
    Beacon --> Identity
    Beacon --> DNA[(dna.json)]

    Interface --> Observer
    Mesh --> Beacon
```

### `identity.py` - Instance Identity

Manages the unique identity of this SEAA instance. Identity is **separate from DNA** and persists across resets.

```python
@dataclass
class InstanceIdentity:
    id: str           # UUID, never changes
    name: str         # Human-friendly name (can be changed)
    genesis_time: str # When this instance was first created
    lineage: str      # Hash of initial DNA (genealogy)
    parent_id: Optional[str] = None  # If spawned from another instance
```

**Key properties:**
- Stored in `.identity.json` (NOT `dna.json`)
- Survives `--reset` command
- Enables mesh node identification
- Tracks genealogy/lineage

### `protocols.py` - Observable Contracts

Defines the universal contracts that any SEAA instance must implement to be observable:

```python
@runtime_checkable
class Observable(Protocol):
    """Any class implementing this can be observed."""
    def get_vitals(self) -> Vitals: ...
    def get_organs(self) -> List[OrganInfo]: ...
    def get_goals(self) -> List[GoalInfo]: ...
    def get_failures(self) -> List[FailureInfo]: ...

@runtime_checkable
class LocalObservable(Observable, Protocol):
    """Extended protocol for local observation."""
    def stream_events(self, patterns: Optional[List[str]] = None) -> Iterator[Event]: ...
    def get_timeline(self, limit: int = 20) -> List[Dict[str, Any]]: ...

@runtime_checkable
class MeshDiscoverable(Protocol):
    """Protocol for mesh-discoverable instances."""
    def announce(self) -> MeshNodeInfo: ...
    def discover(self) -> List[MeshNodeInfo]: ...
```

**Data Classes:**
- `Vitals` - Essential health metrics (mesh-queryable)
- `OrganInfo` - Organ name, health status, failure count
- `GoalInfo` - Goal description, satisfaction status
- `FailureInfo` - Module, error type, circuit state
- `MeshNodeInfo` - Instance ID, endpoint, cached vitals

### `beacon.py` - Minimal Health Endpoint

Implements the `Observable` protocol. This is the **universal query interface** that other instances can call.

```python
class Beacon(Observable):
    """The immutable health beacon for a SEAA instance."""

    def get_vitals(self) -> Vitals:
        """Essential health metrics for mesh protocols."""

    def get_organs(self) -> List[OrganInfo]:
        """Status of all organs with health indicators."""

    def get_goals(self) -> List[GoalInfo]:
        """Goals with satisfaction status and matching organs."""

    def get_failures(self) -> List[FailureInfo]:
        """Current failure records with circuit breaker state."""
```

**Key properties:**
- Read-only (never modifies state)
- Works even when soma is broken
- Designed for mesh queries

### `observer.py` - Extended Local Observation

Wraps Beacon and adds local-only capabilities:

```python
class Observer(LocalObservable):
    """Extended local observer for SEAA."""

    # Delegates to Beacon
    def get_vitals(self) -> Vitals: ...
    def get_organs(self) -> List[OrganInfo]: ...

    # Local-only features
    def stream_events(self, patterns: Optional[List[str]] = None) -> Iterator[Event]:
        """Stream events in real-time from EventBus."""

    def get_timeline(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent evolution timeline."""

    def watch_changes(self, callback: Callable[[DNA], None]) -> Callable[[], None]:
        """Register callback for DNA changes."""

    def get_system_summary(self) -> Dict[str, Any]:
        """Comprehensive system summary for dashboards."""
```

### CLI Commands

The observability layer is exposed via CLI commands in `main.py`:

| Command | Purpose |
|---------|---------|
| `status` | System health + vitals |
| `organs` | List organs with health |
| `goals` | Goal satisfaction progress |
| `failures` | Failure records |
| `identity` | Show/set instance identity |
| `timeline` | Evolution history |
| `watch` | Live event stream |

All commands support `--json` for programmatic access.

### Design Rationale

**Why separate from DNA?**
- Identity must survive resets
- DNA is mutable state; identity is not
- Enables mesh coordination without DNA coupling

**Why in kernel?**
- Must work when soma is broken
- Provides universal contract
- Enables mesh without evolved organs

**Why protocols?**
- Mesh instances can query each other
- Type-safe contracts
- Evolvable implementations

---

## 10. Testing Architecture

The test suite covers all critical components with **109 tests**.

```
tests/
├── conftest.py              # Shared fixtures
│   ├── temp_dir             # Isolated temp directories
│   ├── sample_dna           # Test DNA data
│   ├── mock_llm             # LLM response mocking
│   ├── reset_event_bus      # EventBus cleanup
│   └── soma_structure       # Temp soma/ directory
│
├── unit/
│   ├── test_bus.py          # EventBus (12 tests)
│   ├── test_schema.py       # DNA Schema (17 tests)
│   ├── test_materializer.py # Materializer (16 tests) - includes security tests
│   ├── test_assimilator.py  # Assimilator (6 tests)
│   ├── test_genealogy.py    # Git memory (4 tests)
│   └── test_auto_immune.py  # Auto-revert (3 tests)
│
└── integration/
    └── test_validation.py   # Integration tests (28 tests)
        ├── TestCodeValidation      # AST validation, forbidden imports
        ├── TestCircuitBreaker      # Circuit open/close/cooldown
        ├── TestGoalSatisfaction    # Pattern matching, auto-satisfy
        └── TestConfigValidation    # Config bounds checking

Security Tests (in test_materializer.py):
├── TestMaterializerSecurity
│   ├── test_path_traversal_double_dots_rejected
│   ├── test_path_traversal_many_dots_rejected
│   ├── test_invalid_identifier_rejected
│   ├── test_empty_component_rejected
│   ├── test_non_soma_prefix_rejected
│   ├── test_just_soma_rejected
│   └── test_valid_deep_nesting_accepted
```

**Run tests:**
```bash
python3 -m pytest tests/ -v
python3 -m pytest tests/integration/ -v  # Integration only
```
