# 📂 Project Structure

Complete breakdown of the SEAAM codebase after the A+ Grade refactor.

---

## Root Directory

```
sutraworks-SEAAM/
├── main.py                     # Entry point with CLI
├── config.yaml                 # System configuration
├── dna.json                    # Persistent DNA state
├── pyproject.toml              # Build configuration & dependencies
├── requirements.txt            # Legacy requirements (optional)
├── README.md                   # Main documentation
├── CLAUDE.md                   # AI assistant guide
│
├── seaam/                      # Core system (immutable)
├── soma/                       # Evolved organs (system-generated)
├── tests/                      # Test suite
└── docs/                       # Documentation
```

---

## Core System (`seaam/`)

The immutable kernel that cannot be modified by the system itself.

```
seaam/
├── __init__.py                 # Package exports
│
├── core/                       # 🔧 Infrastructure
│   ├── __init__.py
│   ├── logging.py              # Structured logging (JSON/colored)
│   ├── config.py               # YAML config + env overrides
│   └── exceptions.py           # Typed exception hierarchy
│
├── dna/                        # 🧬 DNA Management
│   ├── __init__.py
│   ├── schema.py               # Pydantic-style dataclasses
│   └── repository.py           # Thread-safe persistence
│
├── kernel/                     # ⚡ The Immutable Seed
│   ├── __init__.py
│   ├── genesis.py              # Slim orchestrator (~280 LOC)
│   ├── bus.py                  # Async EventBus
│   ├── assimilator.py          # Dynamic module loader
│   ├── materializer.py         # Atomic file writer
│   ├── immunity.py             # Error recovery & healing
│   └── genealogy.py            # Evolutionary memory (Git)
│
├── cortex/                     # 🧠 The Mind
│   ├── __init__.py
│   ├── architect.py            # System designer
│   ├── prompt_loader.py        # YAML template manager
│   └── prompts/                # Externalized prompt templates
│       ├── architect_reflect.yaml
│       ├── agent_factory.yaml
│       └── error_feedback.yaml
│
└── connectors/                 # 🔌 External Integrations
    ├── __init__.py
    └── llm_gateway.py          # Ollama/Gemini abstraction
```

---

## Evolved Organs (`soma/`)

System-generated code. This directory starts empty and is populated by SEAAM.

```
soma/                           # 🫀 The Evolved Body
├── __init__.py                 # Auto-generated
│
├── perception/                 # Sensors
│   ├── __init__.py
│   └── observer.py             # Filesystem watcher
│
├── memory/                     # Storage
│   ├── __init__.py
│   └── journal.py              # Event logger
│
└── interface/                  # UI/API
    ├── __init__.py
    └── dashboard.py            # Streamlit dashboard
```

> **Note**: The contents of `soma/` are examples. The actual organs depend on the system's goals.

---

## Test Suite (`tests/`)

Comprehensive testing with pytest.

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
│
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_bus.py             # EventBus (12 tests)
│   ├── test_schema.py          # DNA Schema (17 tests)
│   ├── test_materializer.py    # Materializer (9 tests)
│   └── test_assimilator.py     # Assimilator (6 tests)
│
└── integration/                # Integration tests
    └── __init__.py
```

### Running Tests

```bash
# All tests
python3 -m pytest tests/ -v

# With coverage
python3 -m pytest tests/ --cov=seaam

# Specific file
python3 -m pytest tests/unit/test_bus.py -v
```

---

## Documentation (`docs/`)

Complete system documentation.

```
docs/
├── ARCHITECTURE.md             # System architecture deep dive
├── DESIGN.md                   # Design specifications & protocols
├── OPERATIONS.md               # Operations manual & troubleshooting
├── API.md                      # API reference
├── PROJECT_STRUCTURE.md        # This file
│
└── images/                     # Diagrams and visuals
    ├── seaam_hero_logo.png
    ├── seaam_architecture_clean.png
    ├── seaam_evolution_flow.png
    ├── seaam_dna_structure.png
    ├── seaam_module_diagram.png
    ├── seaam_event_bus.png
    └── seaam_security_layers.png
```

<div align="center">
  <img src="images/seaam_module_diagram.png" alt="Module Dependencies" width="60%">
  <p><em>Package dependencies - clean UML-style view</em></p>
</div>

---

## Configuration Files

### `config.yaml`

```yaml
llm:
  provider: ollama
  model: qwen2.5-coder:14b
  temperature: 0.1

security:
  allow_pip_install: false
  protected_prefixes:
    - seaam.
    - seaam/

logging:
  level: INFO
  format: colored
```

### `pyproject.toml`

```toml
[project]
name = "seaam"
version = "1.0.0"
requires-python = ">=3.9"

dependencies = [
    "requests>=2.28.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
]
```

### `dna.json`

```json
{
  "goals": [...],
  "blueprint": {...},
  "failures": [...],
  "active_modules": [...],
  "metadata": {...}
}
```

---

## Module Responsibilities

| Module | Location | Purpose |
|--------|----------|---------|
| **Logging** | `seaam/core/logging.py` | JSON/colored structured logging |
| **Config** | `seaam/core/config.py` | YAML + env variable configuration |
| **Exceptions** | `seaam/core/exceptions.py` | Typed exception hierarchy |
| **Schema** | `seaam/dna/schema.py` | DNA dataclass definitions |
| **Repository** | `seaam/dna/repository.py` | Thread-safe DNA persistence |
| **Genesis** | `seaam/kernel/genesis.py` | Slim orchestrator |
| **EventBus** | `seaam/kernel/bus.py` | Async pub/sub messaging |
| **Assimilator** | `seaam/kernel/assimilator.py` | Dynamic module loading |
| **Materializer** | `seaam/kernel/materializer.py` | Atomic file writing |
| **Immunity** | `seaam/kernel/immunity.py` | Error recovery & healing |
| **Genealogy** | `seaam/kernel/genealogy.py` | Evolutionary memory & rollback |
| **Architect** | `seaam/cortex/architect.py` | System designer |
| **PromptLoader** | `seaam/cortex/prompt_loader.py` | YAML template management |
| **LLMGateway** | `seaam/connectors/llm_gateway.py` | LLM provider abstraction |

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point with `--reset`, `--config`, `--log-level` |
| `config.yaml` | System configuration (LLM, paths, security, logging) |
| `dna.json` | Persistent state (goals, blueprint, failures, active modules) |
| `pyproject.toml` | Dependencies, build config, pytest settings |
| `CLAUDE.md` | AI assistant context guide |

---

## Data Flow

```
main.py
    ↓
Genesis (orchestrator)
    ├── DNARepository → dna.json
    ├── Architect → PromptLoader → prompts/*.yaml
    │                   ↓
    │              LLMGateway → Ollama/Gemini
    │                   ↓
    ├── Materializer → soma/**/*.py
    │                   ↓
    └── Assimilator → Running Threads
              ↓
         EventBus ←→ All Organs
```

---

## Test Coverage Summary

| Component | Tests | Coverage |
|-----------|-------|----------|
| EventBus | 12 | Subscribe, publish, async, unsubscribe, drain |
| DNA Schema | 17 | Serialization, migration, all operations |
| Materializer | 9 | Writes, protection, packages, atomic |
| Assimilator | 6 | Loading, validation, batch |
| **Total** | **46** | **All passing** |
