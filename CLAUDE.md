# CLAUDE.md - AI Assistant Guide

This file provides context for AI assistants (Claude, etc.) working on the Self-Evolving Autonomous Agent codebase.

## Project Overview

**Self-Evolving Autonomous Agent (SEAA)** is a self-modifying AI system that:
- Writes its own Python code
- Installs its own dependencies
- Hot-loads new capabilities at runtime
- Persists its state in DNA

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
│   └── immunity.py         # Error recovery
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
└── interface/              # UI/API (dashboards, endpoints)
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

### Code Validation
```python
from seaa.connectors.llm_gateway import ProviderGateway
gateway = ProviderGateway()
is_valid, error = gateway.validate_code(code, "module_name")
# Checks: syntax, forbidden imports (pip, subprocess, eval), start() signature
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
| Foundation | ✅ | logging, config, exceptions, DNA schema |
| Kernel Decomposition | ✅ | Split genesis into assimilator, materializer, immunity |
| Cortex Hardening | ✅ | Externalized prompts, prompt loader |
| Cleanup | ✅ | Removed dead code, updated __init__.py |
| Testing | ✅ | 81 tests (unit + integration), pytest fixtures |
| Documentation | ✅ | README, ARCHITECTURE, DESIGN, OPERATIONS, API |

### Latest Refactor (A+ Phase 2)

| Feature | Status | Description |
|---------|--------|-------------|
| Code Validation | ✅ | AST-based syntax, forbidden imports, start() signature |
| LLM Context | ✅ | active_modules passed to prompts |
| Circuit Breaker | ✅ | Auto-disable failing organs after max_attempts |
| Measurable Goals | ✅ | required_organs patterns, auto-satisfaction |
| Resource Limits | ✅ | max_concurrent_organs, max_total_organs |
| Config Validation | ✅ | validate() method, startup checks |
| Bug Fixes | ✅ | JSON cleaning, observer path, Py3.9 types |
| Integration Tests | ✅ | 28 new tests for all features |

## Debugging Tips

1. **Enable debug logging**: `python3 main.py --log-level DEBUG`
2. **Check DNA state**: `cat dna.json | python3 -m json.tool`
3. **List organs**: `find soma/ -name "*.py" ! -name "__init__.py"`
4. **Reset system**: `python3 main.py --reset`

## File Locations

| What | Where |
|------|-------|
| Entry point | `main.py` |
| Configuration | `config.yaml` |
| DNA state | `dna.json` |
| Tests | `tests/` |
| Docs | `docs/` |
| Prompts | `seaa/cortex/prompts/` |
