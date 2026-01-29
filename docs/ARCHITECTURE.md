# 🧬 System Architecture

SEAAM is fundamentally different from traditional software architectures. Instead of a static codebase, it is a **dynamic biological system** designed to grow, heal, and evolve autonomously.

<div align="center">
  <img src="images/seaam_architecture_clean.png" alt="SEAAM Architecture" width="70%">
</div>

---

## 🗺 High-Level Overview

```mermaid
graph TD
    User((User)) -->|Queries| Interface[Interface Organ]
    Interface -->|Events| Bus[Nervous System]
    Bus -->|Events| Memory[Memory Organ]
    
    subgraph KERNEL [The Immutable Seed - seaam/kernel/]
        Genesis[Genesis Orchestrator]
        Bus
        Assimilator[Assimilator]
        Materializer[Materializer]
        Immunity[Immunity System]
        Genealogy[Genealogy (Git)]
    end
    
    subgraph CORTEX [The Mind - seaam/cortex/]
        Architect[Architect] -->|Reflects| DNA[(DNA.json)]
        Architect -->|Uses| PromptLoader[Prompt Loader]
        PromptLoader -->|Loads| Prompts[YAML Templates]
    end
    
    subgraph SOMA [The Body - soma/]
        Perception[perception/]
        Memory
        Interface
    end
    
    subgraph CONNECTORS [External - seaam/connectors/]
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

## 1. The Kernel (`seaam/kernel/`)

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
  <img src="images/seaam_event_bus.png" alt="EventBus Pattern" width="50%">
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
from seaam.kernel.bus import bus, subscribe, publish, Event

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
- **Atomic Writes**: Write to temp file, then rename (prevents corruption)
- **Package Structure**: Auto-creates `__init__.py` in all directories
- **Kernel Protection**: Cannot write to `seaam/*` paths

```python
class Materializer:
    def materialize(self, module_name: str, code: str) -> Path:
        self._check_protection(module_name)  # Raises if protected
        file_path = self._module_to_path(module_name)
        self._ensure_package_structure(file_path.parent)
        self._atomic_write(file_path, code)
        return file_path
```

### `immunity.py` - Error Recovery

The healing system for **dependency resolution** and error classification.

**Classification Logic:**
```mermaid
flowchart TD
    A[Missing Import] --> B{Starts with soma.?}
    B -->|Yes| C[Internal Organ\nRequest Evolution]
    B -->|No| D{Starts with seaam.?}
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

## 2. The Cortex (`seaam/cortex/`)

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
# seaam/cortex/prompts/architect_reflect.yaml
name: architect_reflect
version: 2
description: System reflection and design prompt
variables: [goals, blueprint, failures]
template: |
  You are SEAAM's Architect. Analyze the current system state:
  
  ## Goals
  {{ goals }}
  
  ## Current Blueprint
  {{ blueprint }}
  
  ## Recent Failures
  {{ failures }}
  
  Respond with JSON only...
```

---

## 3. The Connectors (`seaam/connectors/`)

### `llm_gateway.py` - LLM Provider Abstraction

Abstracts LLM providers with **validation and retry logic**.

**Providers:**
| Provider | Configuration | Features |
|----------|---------------|----------|
| Ollama | `OLLAMA_URL`, `OLLAMA_MODEL` | Local, fast, default |
| Gemini | `GEMINI_API_KEY` | Cloud fallback |

**Validation:**
- Every generated organ is validated for `start()` function
- Retry up to 3 times with specific error feedback
- Code cleaning (removes markdown fences)

```python
class ProviderGateway:
    def generate_code(self, module_name: str, description: str) -> Optional[str]:
        prompt = prompt_loader.render("agent_factory",
            module_name=module_name,
            description=description
        )
        
        for attempt in range(self.max_retries):
            code = self._call_provider(prompt)
            code = self._clean_code(code)
            
            if self._validate_code(code):
                return code
            
            prompt = self._add_error_feedback(prompt, "Missing start()")
        
        return None
```

---

## 4. The DNA (`seaam/dna/`)

The DNA is the **persistent memory** of the organism.

### `schema.py` - Data Models

Pydantic-style dataclasses with validation and legacy migration.

**Core Types:**
```python
@dataclass
class Goal:
    text: str
    created_at: datetime
    achieved: bool = False

@dataclass
class OrganBlueprint:
    name: str
    description: str
    dependencies: List[str]
    created_at: datetime
    version: int = 1

@dataclass
class Failure:
    module_name: str
    error_type: FailureType  # IMPORT, VALIDATION, RUNTIME, GENERATION
    message: str
    context: Dict[str, Any]
    attempt_count: int = 1

@dataclass
class DNA:
    goals: List[Goal]
    blueprint: Dict[str, OrganBlueprint]
    failures: List[Failure]
    active_modules: List[str]
    metadata: DNAMetadata
```

### `repository.py` - Persistence

Thread-safe DNA persistence with **atomic writes and backups**.

**Features:**
- Atomic writes (temp file + rename)
- Automatic backups on save
- Lock-based thread safety
- Legacy format migration

---

## 5. The Core (`seaam/core/`)

Foundational infrastructure used throughout the system.

### `logging.py` - Structured Logging

Production-ready logging with **two formats**:

| Format | Use Case | Output |
|--------|----------|--------|
| `colored` | Development | Human-readable with colors |
| `json` | Production | Machine-parseable JSON |

```python
from seaam.core.logging import get_logger

logger = get_logger("genesis")
logger.info("System awakening", cycles=0, organs=5)
```

### `config.py` - Configuration Management

Layered configuration with **priority system**:

1. Built-in defaults → 2. `config.yaml` → 3. Environment variables

```python
from seaam.core.config import config

# Access configuration
model = config.llm.model
allow_pip = config.security.allow_pip_install
```

### `exceptions.py` - Typed Exception Hierarchy

```
SEAAMError (base)
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

SEAAM follows a **security-first** design:

| Protection | Mechanism |
|------------|-----------|
| Kernel Immutability | Materializer rejects writes to `seaam/*` |
| Pip Disabled | `allow_pip_install: false` by default |
| Package Allowlist | Only approved packages can be installed |
| Atomic Writes | Prevents file corruption |
| Thread Isolation | Each organ runs in its own daemon thread |

---

## 9. Testing Architecture

The test suite covers all critical components:

```
tests/
├── conftest.py           # Shared fixtures
│   ├── temp_dir          # Isolated temp directories
│   ├── sample_dna        # Test DNA data
│   ├── mock_llm          # LLM response mocking
│   ├── reset_event_bus   # EventBus cleanup
│   └── soma_structure    # Temp soma/ directory
│
└── unit/
    ├── test_bus.py       # EventBus (12 tests)
    ├── test_schema.py    # DNA Schema (17 tests)
    ├── test_materializer.py  # Materializer (9 tests)
    └── test_assimilator.py   # Assimilator (6 tests)
```

**Run tests:**
```bash
python3 -m pytest tests/ -v
```
