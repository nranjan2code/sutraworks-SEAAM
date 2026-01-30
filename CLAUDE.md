# CLAUDE.md - AI Assistant Guide

This file provides context for AI assistants (Claude, etc.) working on the Self-Evolving Autonomous Agent codebase.

## Project Overview

**Self-Evolving Autonomous Agent (SEAA)** is a self-modifying AI system that:
- Writes its own Python code
- Installs its own dependencies
- Hot-loads new capabilities at runtime
- Persists its state in DNA
- Maintains a persistent identity across resets
- Is mesh-ready for multi-instance deployments

## Architecture Summary

```
seaa/                      # Immutable kernel (CANNOT be modified by system)
├── core/                   # Infrastructure
│   ├── logging.py          # Structured logging (JSON/colored)
│   ├── config.py           # YAML config + env overrides
│   └── exceptions.py       # Typed exception hierarchy
│
├── dna/                    # DNA management
│   ├── schema.py           # Pydantic-style dataclasses
│   └── repository.py       # Thread-safe persistence
│
├── kernel/                 # The immutable seed
│   ├── genesis.py          # Slim orchestrator (~280 LOC)
│   ├── bus.py              # Async EventBus
│   ├── assimilator.py      # Dynamic module loader
│   ├── materializer.py     # Atomic file writer
│   ├── immunity.py         # Error recovery
│   ├── identity.py         # Instance identity (survives resets)
│   ├── beacon.py           # Minimal health endpoint (mesh-ready)
│   ├── observer.py         # Local introspection + event streaming
│   └── protocols.py        # Observable contracts for mesh
│
├── cortex/                 # The mind
│   ├── architect.py        # System designer
│   ├── prompt_loader.py    # YAML template manager
│   └── prompts/            # Externalized prompt templates
│
└── connectors/             # External integrations
    └── llm_gateway.py      # Ollama/Gemini abstraction

soma/                       # Evolved organs (SYSTEM-GENERATED)
├── perception/             # Sensors (filesystem, etc.)
├── memory/                 # Storage (journals, databases)
├── interface/              # UI/API (dashboards, endpoints) - evolvable
└── extensions/             # Custom metrics, health checks - evolvable
```

## Key Invariants

1. **Kernel Protection**: The system CANNOT modify files in `seaa/*`
2. **Organ Contract**: Every organ MUST have a `def start():` function with zero required args
3. **Thread Safety**: DNA access is locked, file writes are atomic
4. **Pip Disabled**: External package installation is disabled by default
5. **Code Validation**: All generated code is AST-validated before materialization
6. **Circuit Breaker**: Failing organs are auto-disabled after `max_attempts` failures
7. **Resource Limits**: `max_concurrent_organs` and `max_total_organs` caps enforced
8. **Config Validation**: Invalid configuration rejected at startup
9. **Path Traversal Protection**: Module names are strictly validated to prevent directory escape
10. **Module Name Validation**: Only `soma.*` with valid Python identifiers can be imported
11. **DNA Integrity**: SHA-256 hash verification detects tampering
12. **Prompt Injection Protection**: Error messages are sanitized before LLM prompts
13. **Identity Persistence**: Instance identity survives DNA resets (stored in `.identity.json`)

## CLI Commands

```bash
# Run the agent
python3 main.py

# Query commands (no agent startup)
python3 main.py status              # System health + vitals
python3 main.py organs              # List organs with health
python3 main.py goals               # Goal satisfaction progress
python3 main.py failures            # Failure records
python3 main.py identity            # Show instance identity
python3 main.py identity --name X   # Set instance name
python3 main.py timeline            # Evolution history
python3 main.py watch               # Live event stream

# All query commands support --json for programmatic access
python3 main.py status --json

# Options
python3 main.py --reset             # Reset to tabula rasa (preserves identity)
python3 main.py --config FILE       # Custom config file
python3 main.py --log-level DEBUG   # Override log level
```

## Common Tasks

### Running Tests
```bash
python3 -m pytest tests/ -v
```

### Adding a New Kernel Module
1. Create file in `seaa/kernel/`
2. Add to `seaa/kernel/__init__.py`
3. Write tests in `tests/unit/`
4. Update documentation

### Modifying Prompts
Edit YAML files in `seaa/cortex/prompts/`:
- `architect_reflect.yaml` - System reflection
- `agent_factory.yaml` - Code generation
- `error_feedback.yaml` - Error recovery

### Python Version
- **Minimum**: Python 3.9
- **Type Hints**: Use `Optional`, `Union`, `List`, `Dict` from `typing` (not `|` syntax)

## Code Conventions

### Logging
```python
from seaa.core.logging import get_logger
logger = get_logger("module_name")
logger.info("Message", key="value")
```

### Configuration
```python
from seaa.core.config import config
model = config.llm.model
```

### Exceptions
```python
from seaa.core.exceptions import MaterializationError
raise MaterializationError("message", context={"key": "value"})
```

### Events
```python
from seaa.kernel.bus import publish, subscribe, Event
handle = subscribe("event.type", handler)
publish(Event(event_type="event.type", data=payload))
handle.unsubscribe()
```

### Identity
```python
from seaa.kernel.identity import get_identity, set_name, get_instance_id

# Get identity (creates if not exists)
identity = get_identity()
print(identity.id)       # UUID
print(identity.name)     # Human-friendly name
print(identity.lineage)  # DNA hash at birth

# Set name
set_name("Robinson")
```

### Beacon (Health Endpoint)
```python
from seaa.kernel.beacon import get_beacon, get_vitals, is_healthy

# Get vitals (mesh-queryable format)
vitals = get_vitals()
print(vitals.organ_count)
print(vitals.healthy_organs)
print(vitals.goals_satisfied)

# Quick health check
if is_healthy():
    print("All systems go")
```

### Observer (Local Introspection)
```python
from seaa.kernel.observer import get_observer

observer = get_observer()

# Get detailed organ info
for organ in observer.get_organs():
    print(f"{organ.name}: {organ.health}")

# Stream events in real-time
for event in observer.stream_events():
    print(f"{event.event_type}: {event.data}")

# Get evolution timeline
for entry in observer.get_timeline(limit=10):
    print(f"{entry['type']}: {entry['organ']}")
```

### Protocols (Observable Contracts)
```python
from seaa.kernel.protocols import Observable, Vitals, OrganInfo, GoalInfo

# Beacon implements Observable protocol
# Can be used for type hints and mesh interoperability
def query_instance(obs: Observable) -> Vitals:
    return obs.get_vitals()
```

### Code Validation
```python
from seaa.connectors.llm_gateway import ProviderGateway
gateway = ProviderGateway()
is_valid, error = gateway.validate_code(code, "module_name")
# Checks: syntax, forbidden imports (pip, subprocess, eval, ctypes, socket, pickle, etc.),
#         star imports (from X import *), start() signature
```

### Module Name Validation
```python
from seaa.kernel.materializer import Materializer
materializer = Materializer()
# Module names must match: ^soma(\.[a-z_][a-z0-9_]*)+$
# Path traversal attempts (e.g., "soma..seaa") are rejected
materializer.materialize("soma.valid.name", code)  # OK
materializer.materialize("soma..evil", code)  # Raises MaterializationError
```

### Circuit Breaker
```python
from seaa.dna.schema import DNA
dna = DNA.from_dict(data)
if dna.should_attempt("soma.xyz", max_attempts=3, cooldown_minutes=30):
    # Safe to evolve
    pass
dna.reset_circuit("soma.xyz")  # Manual reset
```

### Goal Satisfaction
```python
from seaa.dna.schema import Goal
goal = Goal(description="Perceive files", required_organs=["soma.perception.*"])
# After soma.perception.observer becomes active:
newly_satisfied = dna.check_goal_satisfaction()  # Auto-satisfies matching goals
```

## Observability Layer

The observability layer is split into **static** (kernel) and **evolvable** (soma) components:

| Component | Location | Purpose |
|-----------|----------|---------|
| `identity.py` | Kernel (static) | Instance UUID, name, lineage - survives resets |
| `beacon.py` | Kernel (static) | Minimal vitals endpoint - mesh queryable |
| `observer.py` | Kernel (static) | Rich local introspection + event streaming |
| `protocols.py` | Kernel (static) | Observable contracts for mesh interop |
| `soma.interface.*` | Soma (evolvable) | Rich dashboards, TUI, web UI |
| `soma.extensions.*` | Soma (evolvable) | Custom metrics, health checks |
| `soma.mesh.*` | Soma (evolvable) | Fleet discovery, remote queries |

### Design Principle

The kernel provides the **universal observability contract** that:
- Survives soma reset
- Works for any instance
- Is mesh-queryable
- Doesn't assume what organs exist

Soma evolves the **rich interfaces** that:
- Vary per instance's needs
- Can aggregate across mesh
- Can be wiped and regrown differently

## Testing Patterns

### Fixtures (tests/conftest.py)
- `temp_dir` - Isolated temp directory
- `sample_dna` - Test DNA data
- `reset_event_bus` - Cleans EventBus state
- `mock_llm_response` - Mocks gateway responses
- `soma_structure` - Creates temp soma/ directory

### Test Structure
```python
class TestComponent:
    def test_feature_works(self, fixture):
        # Arrange
        component = Component()

        # Act
        result = component.do_thing()

        # Assert
        assert result == expected
```

## Recent Refactor (A+ Grade)

The codebase was recently refactored for robustness:

| Phase | Status | Changes |
|-------|--------|---------|
| Foundation | Done | logging, config, exceptions, DNA schema |
| Kernel Decomposition | Done | Split genesis into assimilator, materializer, immunity |
| Cortex Hardening | Done | Externalized prompts, prompt loader |
| Cleanup | Done | Removed dead code, updated __init__.py |
| Testing | Done | 109 tests (unit + integration), pytest fixtures |
| Documentation | Done | README, ARCHITECTURE, DESIGN, OPERATIONS, API |

### Latest Refactor (A+ Phase 2)

| Feature | Status | Description |
|---------|--------|-------------|
| Code Validation | Done | AST-based syntax, forbidden imports, start() signature |
| LLM Context | Done | active_modules passed to prompts |
| Circuit Breaker | Done | Auto-disable failing organs after max_attempts |
| Measurable Goals | Done | required_organs patterns, auto-satisfaction |
| Resource Limits | Done | max_concurrent_organs, max_total_organs |
| Config Validation | Done | validate() method, startup checks |
| Bug Fixes | Done | JSON cleaning, observer path, Py3.9 types |
| Integration Tests | Done | 28 new tests for all features |

### Security Hardening (Phase 3)

| Vulnerability | Status | Fix |
|---------------|--------|-----|
| Path Traversal | Done | Regex validation + path canonicalization in materializer.py |
| Module Injection | Done | Strict `soma.*` validation in assimilator.py |
| LLM Response Injection | Done | Module name validation in architect.py |
| Star Import Bypass | Done | `from X import *` detection in llm_gateway.py |
| Prompt Injection | Done | Error message sanitization before LLM prompts |
| Extended Forbidden Imports | Done | Added ctypes, socket, pickle, network modules |
| JSON Extraction | Done | Proper depth tracking instead of brace matching |
| Git Command Injection | Done | Config value validation in genealogy.py |
| Log Path Traversal | Done | Allowlist-based path validation in journal.py |
| DNA Tampering | Done | SHA-256 integrity verification in repository.py |
| Security Tests | Done | 8 new tests for path traversal scenarios |

### Observability Layer (Phase 4)

| Feature | Status | Description |
|---------|--------|-------------|
| Identity | Done | Instance UUID, name, lineage in `.identity.json` |
| Beacon | Done | Minimal health endpoint implementing Observable protocol |
| Observer | Done | Rich local introspection with event streaming |
| Protocols | Done | Observable, LocalObservable, MeshDiscoverable contracts |
| CLI Commands | Done | status, organs, goals, failures, watch, identity, timeline |
| JSON Output | Done | All commands support `--json` for programmatic access |
| Mesh-Ready | Done | Protocols designed for future multi-instance deployment |

## Debugging Tips

1. **Enable debug logging**: `python3 main.py --log-level DEBUG`
2. **Check DNA state**: `cat dna.json | python3 -m json.tool`
3. **Check identity**: `python3 main.py identity`
4. **List organs**: `python3 main.py organs`
5. **Check health**: `python3 main.py status`
6. **Watch events**: `python3 main.py watch`
7. **Reset system**: `python3 main.py --reset`

## File Locations

| What | Where |
|------|-------|
| Entry point | `main.py` |
| Configuration | `config.yaml` |
| DNA state | `dna.json` |
| Instance identity | `.identity.json` |
| Tests | `tests/` |
| Docs | `docs/` |
| Prompts | `seaa/cortex/prompts/` |
