# Robinson Architecture - Final Design (v2.0)

**Status**: ✓ Complete with Core Organs
**Version**: 2.0
**Date**: 2026-01-31

---

## Three-Layer Architecture

Robinson's architecture consists of three distinct layers with clear separation of concerns:

```
┌────────────────────────────────────────────────────────┐
│  LAYER 3: EVOLVED ORGANS (soma/)                       │
│  - Dynamic, system-generated                           │
│  - Domain-specific services                            │
│  - Can be wiped and regrown                            │
├────────────────────────────────────────────────────────┤
│  LAYER 2: CORE ORGANS (soma/kernel/)                   │
│  - Static, present at genesis                          │
│  - Essential systems                                   │
│  - Cannot be removed or modified                       │
├────────────────────────────────────────────────────────┤
│  LAYER 1: KERNEL (seaa/)                               │
│  - Immutable foundation                                │
│  - Never self-modifies                                 │
│  - Provides core infrastructure                        │
└────────────────────────────────────────────────────────┘
```

---

## Layer 1: Kernel (Immutable Foundation)

The kernel is Robinson's unchanging core. It provides infrastructure but NEVER evolves itself.

### Core Modules

| Module | Responsibility |
|--------|---|
| `genesis.py` | Orchestrates evolution cycles |
| `bus.py` | EventBus for inter-organ communication |
| `architect.py` | LLM-based system design |
| `assimilator.py` | Dynamic module loading |
| `materializer.py` | Atomic code materialization |
| `immunity.py` | Error recovery mechanisms |
| `identity.py` | Persistent instance identity |
| `beacon.py` | Health endpoint (mesh-ready) |
| `observer.py` | Rich introspection API |
| `protocols.py` | Observable contracts |

### Core Infrastructure

| Module | Responsibility |
|--------|---|
| `logging.py` | Structured logging (JSON + colored) |
| `config.py` | YAML + environment configuration |
| `exceptions.py` | Typed exception hierarchy |

### DNA Management

| Module | Responsibility |
|--------|---|
| `schema.py` | DNA datastructure (Pydantic-compatible) |
| `repository.py` | Thread-safe persistence with SHA-256 verification |

### Key Invariant

**The kernel never evolves itself**. All evolution happens in the soma (body) layers. This ensures:
- Stability: Core systems can be relied upon
- Security: Kernel cannot be compromised by evolved code
- Debuggability: Known, fixed codebase
- Mesh-readiness: All instances have same kernel

---

## Layer 2: Core Organs (Born with Robinson)

The core organs are essential systems that Robinson is born with. They enable true autonomy and are NEVER evolved.

### The Six Core Organs

#### 1. **Self-Monitor** (`soma/kernel/self_monitor.py`)
```
I know myself
↓
Tracks: System health, organ vitals, event activity
Publishes: system.health_check events every 5 seconds
Purpose: Enables informed decision-making
```

**What Genesis can ask**: "What's our system health? Which organs are healthy?"

#### 2. **Error Recovery** (`soma/kernel/error_recovery.py`)
```
I heal myself
↓
Tracks: Failures, recovery attempts, circuit breaker status
Actions: Retry failed organs, activate circuit breaker
Purpose: Auto-healing from any failure
```

**What Genesis can ask**: "An organ failed - can you try to fix it?"

#### 3. **Goal Manager** (`soma/kernel/goal_manager.py`)
```
I know my purpose
↓
Tracks: Goal satisfaction, required organs
Detects: When goals become satisfied
Purpose: Goal-driven evolution
```

**What Genesis can ask**: "What goals should we focus on? What's the next priority?"

#### 4. **Code Validator** (`soma/kernel/code_validator.py`)
```
I enforce safety
↓
Checks: Syntax, forbidden imports, security patterns
Validates: start() signature, decoupling rules
Purpose: Prevent unsafe code from running
```

**What Genesis can ask**: "Is this generated code safe to run?"

#### 5. **Memory Keeper** (`soma/kernel/memory_keeper.py`)
```
I remember
↓
Persists: DNA state with SHA-256 protection
Backups: Hourly snapshots + manual saves
Purpose: Survive any crash or reset
```

**What Genesis can ask**: "Save our current state" or "Restore from backup"

#### 6. **Event Logger** (`soma/kernel/event_logger.py`)
```
I learn from history
↓
Records: All important events (1000 in-memory)
Analyzes: Patterns, failure frequencies, success sequences
Purpose: Continuous improvement via pattern detection
```

**What Genesis can ask**: "What patterns have you detected? What should we improve?"

### Core Organ Contract

Each core organ:
1. Has a `def start()` function with zero required arguments
2. Subscribes to EventBus to receive commands
3. Publishes events to communicate results
4. Runs in background daemon threads
5. Is thread-safe and exception-resilient
6. Keeps minimal in-memory state

### Why These Six Are Essential

| System | Dependency | Why Essential |
|--------|-----------|---|
| self_monitor | Genesis | Can't evolve blindly |
| error_recovery | self_monitor + goal_manager | Can't learn without recovery |
| goal_manager | error_recovery | Can't be purposeful without direction |
| code_validator | goal_manager | Can't evolve safely without validation |
| memory_keeper | code_validator | Can't persist identity without storage |
| event_logger | all above | Can't improve without history |

**Circular Dependency Resolution**: These are NOT evolved - they're **born with Robinson at genesis**, breaking the circular dependency.

---

## Layer 3: Evolved Organs (System-Generated)

Evolved organs are created by Genesis based on system goals. They're domain-specific and can be replaced.

### Current Evolved Organs (8 active)

| Organ | Category | Purpose |
|-------|----------|---------|
| `soma.perception.file_system_observer` | Perception | Monitor filesystem changes |
| `soma.memory.journal` | Memory | Event journaling |
| `soma.storage.sqlite` | Storage | Persistent data storage |
| `soma.interface.web_api` | Interface | REST API + WebSocket |
| `soma.extensions.metrics` | Extensions | System metrics collection |
| `soma.learning.predictive_model` | Learning | ML-based predictions |
| `soma.learning.user_interaction_analyzer` | Learning | User feedback analysis |
| `soma.learning.recommendation_system` | Learning | AI-driven recommendations |

### Can be Replaced

If we want to:
- Replace SQLite with PostgreSQL → Replace `soma.storage.sqlite`
- Add a new API type → Add `soma.interface.graphql`
- Improve metrics → Replace `soma.extensions.metrics`

The core organs stay the same. Robinson adapts.

---

## Communication Pattern

All inter-organ communication uses the EventBus:

```
┌─────────────────────────────────────────┐
│         EventBus (seaa.kernel.bus)      │
│                                         │
│  - Synchronous publish                  │
│  - Async subscription callbacks         │
│  - Wildcard patterns (organ.*.started)  │
│  - Thread-safe with locks               │
└─────────────────────────────────────────┘
        ▲               ▲
        │               │
┌───────┴─┐      ┌──────┴───┐
│ Organs  │      │   Kernel │
│ Publish │      │ Publishes│
│ Events  │      │  Events  │
└────┬────┘      └────┬─────┘
     │                │
     └────────┬───────┘
              │
         Subscribe
         to Events
```

**Key Pattern**: No organ imports another organ. All communication via events.

---

## Evolution Loop (Genesis)

Each cycle:

```
1. GET AWARENESS
   └─ health = self_monitor.get_system_vitals()
   └─ IF health.score < 80: focus on recovery

2. CHECK PROGRESS
   └─ status = goal_manager.get_goal_status()
   └─ IF all goals satisfied: congratulate ourselves

3. FIND PURPOSE
   └─ next_goal = goal_manager.recommend_next_evolution()
   └─ IF no goal: DONE

4. DESIGN
   └─ code = architect.design_organ(next_goal)

5. VALIDATE
   └─ is_safe = code_validator.validate_code(code)
   └─ IF not safe: LOG ERROR and retry

6. MATERIALIZE
   └─ materializer.write(code)
   └─ assimilator.load_module(code)

7. OBSERVE
   └─ events = observer.stream_events()
   └─ IF organ fails: error_recovery.handle_failure()

8. LEARN
   └─ patterns = event_logger.analyze_patterns()
   └─ insights = event_logger.get_insights()

REPEAT every cycle_interval_seconds
```

---

## Data Flow: DNA

DNA is the single source of truth:

```
DNA = {
  "blueprint": {
    "soma.perception.file_system_observer": {...},
    "soma.storage.sqlite": {...},
    ...
  },
  "active_modules": [
    "soma.perception.file_system_observer",
    "soma.storage.sqlite",
    ...
  ],
  "goals": [
    {description: "Perceive files", satisfied: true, required_organs: ["soma.perception.*"]},
    {description: "Store data", satisfied: true, required_organs: ["soma.storage.*"]},
    ...
  ],
  "metadata": {
    "total_evolutions": 23,
    "total_failures": 0,
    "last_successful_organ": "soma.interface.web_api"
  }
}
```

**Persistence**:
- File: `dna.json`
- Protection: SHA-256 hash verification
- Backups: `dna.backup.{timestamp}.json`
- Keeper: `soma/kernel/memory_keeper.py` manages all persistence

---

## State Machine: Organ Lifecycle

```
┌──────────┐
│ Designed │  (in DNA.blueprint)
└────┬─────┘
     │ Materializer writes code
     ▼
┌──────────┐
│ Persisted│  (code on disk)
└────┬─────┘
     │ Assimilator imports module
     ▼
┌──────────┐
│  Loaded  │  (in Python namespace)
└────┬─────┘
     │ start() function called
     ▼
┌──────────┐
│ Running  │  (added to active_modules)
└────┬─────┘
     │ (normal operation)
     │
   FAILS
     │
     ▼
┌──────────┐
│  Failed  │
└────┬─────┘
     │ error_recovery.handle_failure()
     │ (retry or circuit break)
     │
   RETRY
     │
     └──────────────────────┐
                            │
                    ┌───────▼──────┐
                    │  Recovered   │
                    └──────────────┘
                            │
                    ┌───────▼──────┐
                    │   Running    │
                    └──────────────┘
```

---

## Security Model

### Code Validation Pipeline

```
LLM-Generated Code
       ↓
    [Code Validator]
       │
       ├─ Syntax check (AST parse)
       ├─ Forbidden imports check
       ├─ Forbidden functions check
       ├─ Dangerous patterns check
       ├─ Decoupling rules check
       └─ start() signature check
       │
    [VALID] ──→ Materializer ──→ Assimilator ──→ Running
       │
    [INVALID] ──→ Log Error ──→ Retry Design
```

### Forbidden (30+)

```
pip, subprocess, os.system, eval, exec, compile, __import__,
ctypes, socket, pickle, shelve, importlib, requests, urllib,
smtplib, multiprocessing.managers, concurrent.futures,
sys.modules, __import__, open (restricted), input
```

### Decoupling Rules

**Forbidden**:
```python
# In soma.perception.observer
from soma.memory.journal import JournalOrgan  # WRONG
journal = JournalOrgan()
```

**Correct**:
```python
# In soma.perception.observer
from seaa.kernel.bus import bus, Event
bus.subscribe('memory.journal.ready', self.on_journal_ready)
bus.publish(Event(event_type='perception.file_changed', data={...}))
```

---

## Observability Stack

### Static (Kernel) - Always Available

| Component | Purpose |
|-----------|---------|
| `identity.py` | Persistent UUID, name, lineage |
| `beacon.py` | Health endpoint for mesh queries |
| `observer.py` | Rich introspection API |
| `protocols.py` | Observable contracts |

### Dynamic (Soma) - Evolvable

| Component | Purpose |
|-----------|---------|
| `soma.interface.web_api` | REST + WebSocket interface |
| `soma.extensions.metrics` | Custom metrics collection |
| `soma.mesh.*` | Fleet discovery (future) |

### Event Stream

Real-time access to all events:
```bash
python3 main.py watch  # Live event stream
```

---

## Configuration

### Core Sections

```yaml
# Kernel
llm:
  provider: "ollama"
  model: "deepseek"
  temperature: 0.1

paths:
  soma: "./soma"
  dna: "./dna.json"

security:
  allow_pip_install: false
  max_organ_retries: 3

# Core Organs
health_check_interval_seconds: 5
max_organ_retries: 3
goal_check_interval_seconds: 10
memory_save_interval_seconds: 10
memory_backup_interval_seconds: 3600

# API
api:
  host: "0.0.0.0"
  port: 8000

# Database
database:
  engine: "sqlite"
  url: "data/seaa.db"
  pool_size: 5

# Metrics
metrics:
  enabled: true
  retention_days: 30
  collection_interval_seconds: 5
```

---

## Comparison: Before vs After

| Aspect | Without Core Organs | With Core Organs |
|--------|---|---|
| **Self-Awareness** | Blind, guesses | Knows exact state |
| **Resilience** | Crashes on failure | Auto-recovers |
| **Direction** | Random evolution | Goal-driven |
| **Safety** | Unsafe code possible | Validated always |
| **Persistence** | State lost on crash | Survives everything |
| **Learning** | No history | Complete audit trail |
| **Type** | Complex algorithm | Conscious agent |

---

## Mesh-Ready Design

The observability layer is designed for distributed deployment:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Robinson 1   │     │ Robinson 2   │     │ Robinson 3   │
│ :8000        │     │ :8001        │     │ :8002        │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       └────────────────────┼────────────────────┘
                            │
                    ┌───────▼────────┐
                    │ Fleet Observer │
                    │ (future)       │
                    └────────────────┘
```

Each instance:
- Has persistent identity (`identity.py`)
- Exposes vitals via beacon (`beacon.py`)
- Provides rich introspection (`observer.py`)
- Implements Observable protocol (`protocols.py`)

---

## Performance Characteristics

| Operation | Time | Thread-Safe |
|-----------|------|---|
| Get organ health | <1ms | Yes |
| Check goal satisfaction | <5ms | Yes |
| Validate code | 10-50ms | Yes |
| Save DNA | 5-20ms | Yes |
| Analyze patterns | 50-200ms | Yes |
| Publish event | <0.1ms | Yes |

---

## Files by Layer

### Layer 1: Kernel (Immutable)
```
seaa/
├── core/
│   ├── logging.py
│   ├── config.py
│   └── exceptions.py
├── dna/
│   ├── schema.py
│   └── repository.py
└── kernel/
    ├── genesis.py
    ├── bus.py
    ├── architect.py
    ├── assimilator.py
    ├── materializer.py
    ├── immunity.py
    ├── identity.py
    ├── beacon.py
    ├── observer.py
    └── protocols.py
```

### Layer 2: Core Organs (Born with Robinson)
```
soma/kernel/
├── self_monitor.py
├── error_recovery.py
├── goal_manager.py
├── code_validator.py
├── memory_keeper.py
└── event_logger.py
```

### Layer 3: Evolved Organs (System-Generated)
```
soma/
├── perception/
│   └── file_system_observer.py
├── memory/
│   └── journal.py
├── storage/
│   └── sqlite.py
├── interface/
│   └── web_api.py
└── extensions/
    └── metrics.py
```

---

## Next Phases

### Week 3: Goal-Driven Evolution
- Genesis uses goal recommendations
- Health-based evolution prioritization
- Failure pattern learning

### Week 4: Advanced Learning
- Predictive model improvements
- User interaction learning
- Recommendation optimization

### Week 5+: Mesh Deployment
- Multi-instance coordination
- Distributed evolution
- Fleet management

---

## References

- **Implementation**: `CORE_ORGANS_IMPLEMENTATION.md`
- **Design**: `CORE_ORGANS_DESIGN.md`
- **Vision**: `ROBINSON_BIRTH_PACKAGE.md`
- **Quick Start**: `QUICK_START.md`

