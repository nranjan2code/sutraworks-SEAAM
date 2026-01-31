# SEAA Directory Structure

Organized reference for the Self-Evolving Autonomous Agent codebase.

## Root Level

| File/Folder | Purpose |
|-------------|---------|
| `main.py` | Entry point - Run the agent |
| `config.yaml` | System configuration |
| `install.sh` | One-command installation script |
| `setup.py` | Python package configuration |
| `requirements.txt` | Core dependencies |
| `requirements-dev.txt` | Development dependencies |
| `.gitignore` | Git configuration |
| `dna.json` | System state (DNA) - auto-generated |
| `.identity.json` | Instance identity - auto-generated |

## Documentation

```
├── INSTALL.md                      ← Start here for installation
├── QUICK_START.md                  ← Quick start guide
├── README.md                       ← Project overview
├── CLAUDE.md                       ← AI assistant guide
├── ARCHITECTURE_FINAL.md           ← System architecture
├── ARCHITECTURE_VISION.md          ← Long-term vision
├── ARCHITECTURE_EVOLUTION.md       ← Evolution history
├── CORE_ORGANS_DESIGN.md          ← Organ design patterns
├── CORE_ORGANS_IMPLEMENTATION.md  ← Implementation details
├── DIRECTORY.md                    ← This file
├── DOCUMENTATION_INDEX.md          ← All documentation
└── ...other docs
```

## Core Kernel (Immutable)

```
seaa/
├── kernel/                         # Immutable system seed (~2000 LOC)
│   ├── genesis.py                  # Main orchestrator
│   ├── bus.py                      # Event bus for communication
│   ├── assimilator.py              # Dynamic module loader
│   ├── materializer.py             # Atomic file writer
│   ├── immunity.py                 # Error recovery & healing
│   ├── identity.py                 # Instance identity (persists resets)
│   ├── beacon.py                   # Health endpoint (mesh-ready)
│   ├── observer.py                 # Local introspection
│   ├── protocols.py                # Observable contracts
│   ├── __init__.py
│   └── tests/
│
├── core/                           # Infrastructure
│   ├── logging.py                  # Structured logging (JSON/colored)
│   ├── config.py                   # YAML config + env overrides
│   ├── exceptions.py               # Typed exception hierarchy
│   └── __init__.py
│
├── dna/                            # DNA management (persistence)
│   ├── schema.py                   # Data structures
│   ├── repository.py               # Thread-safe persistence
│   └── __init__.py
│
├── cortex/                         # The mind
│   ├── architect.py                # System designer
│   ├── prompt_loader.py            # YAML template loader
│   ├── prompts/                    # Externalized prompts
│   │   ├── architect_reflect.yaml
│   │   ├── agent_factory.yaml
│   │   └── error_feedback.yaml
│   └── __init__.py
│
├── cli/                            # Interactive REPL (optional)
│   ├── __init__.py
│   ├── repl.py                     # REPL loop
│   ├── commands.py                 # Command registry
│   ├── runtime.py                  # Genesis background thread
│   ├── completers.py               # Tab completion
│   ├── parsers/                    # Natural language & fuzzy matching
│   │   ├── fuzzy.py
│   │   └── natural.py
│   ├── ui/                         # Terminal UI
│   │   ├── formatters.py
│   │   ├── panels.py
│   │   ├── tables.py
│   │   └── dashboard.py
│   └── tests/
│
├── connectors/                     # External integrations
│   ├── llm_gateway.py              # LLM abstraction (Ollama, Gemini, custom)
│   └── __init__.py
│
└── __init__.py
```

## Evolved Organs (Tracked Core Organs)

```
soma/                              # Evolved organs shipped with system
├── README.md
├── __init__.py
│
├── perception/                    # Sensors
│   ├── file_system_observer.py     # Monitor filesystem
│   ├── __init__.py
│   └── tests/
│
├── memory/                        # Storage
│   ├── journal.py                 # Event journal
│   ├── __init__.py
│   └── tests/
│
├── interface/                     # User interaction
│   ├── web_api.py                 # REST API
│   ├── __init__.py
│   └── tests/
│
├── storage/                       # Data persistence
│   ├── sqlite.py                  # SQLite database
│   ├── __init__.py
│   └── tests/
│
├── extensions/                    # Custom functionality
│   ├── metrics.py                 # System metrics
│   ├── __init__.py
│   └── tests/
│
├── learning/                      # Self-improvement
│   ├── autonomous_optimizer.py     # Auto-optimization
│   ├── feedback_loop.py            # Learning loop
│   ├── predictive_model.py         # Prediction engine
│   ├── recommendation_system.py    # Recommendations
│   ├── self_awareness.py           # Self-understanding
│   ├── user_interaction_analyzer.py # User pattern analysis
│   ├── __init__.py
│   └── tests/
│
└── kernel/                        # Extended kernel organs
    ├── code_validator.py
    ├── error_recovery.py
    ├── event_logger.py
    ├── goal_manager.py
    ├── memory_keeper.py
    ├── self_monitor.py
    ├── __init__.py
    └── tests/
```

## Tests

```
tests/
├── conftest.py                     # Shared fixtures
├── unit/                          # Unit tests
│   ├── test_kernel/
│   ├── test_dna/
│   ├── test_core/
│   └── ...
└── integration/                   # Integration tests
    ├── test_genesis/
    ├── test_cli/
    └── ...
```

## Data & Logs (Auto-Generated)

```
.
├── dna.json                       # System state (DNA)
├── dna.sha256                     # DNA integrity hash
├── .identity.json                 # Instance identity
├── .dna_backups/                  # DNA backups
├── logs/                          # Log files
└── data/                          # Application data
    └── seaa.db                    # SQLite database
```

## Configuration Files

```
.
├── config.yaml                    # Main configuration
├── .env                           # Environment variables (optional)
├── .gitignore                     # Git configuration
└── .claude/                       # Claude Code specific
```

## Virtual Environment (After install.sh)

```
venv/
├── bin/                           # Executables
├── lib/                           # Python packages
├── include/                       # Headers
└── pyvenv.cfg                     # Configuration
```

## Key File Purposes

### Kernel Files (Immutable)
- `seaa/kernel/*.py` - Never modified by the system
- `seaa/core/*.py` - Infrastructure, never modified
- `seaa/cortex/*.py` - Prompts and reasoning templates

### DNA (System State)
- `dna.json` - Complete system state
  * Active modules
  * Goals and their satisfaction
  * Failures and circuit breakers
  * Evolution history
  * Metadata

### Organs (Evolved Code)
- `soma/**/*.py` - Generated and hand-written organ code
- Core organs shipped with system
- Runtime-generated organs ignored by git

### Configuration
- `config.yaml` - System settings
  * LLM provider configuration
  * Metabolism (cycle intervals)
  * Resource limits
  * Security settings
  * Logging configuration

## Directory Cleanup Strategy

### Tracked in Git
```
seaa/                    # All kernel files
soma/                    # Core organs only
tests/                   # Test files
docs/                    # Documentation
*.md                     # Markdown docs
config.yaml              # Configuration
setup.py, install.sh     # Setup files
requirements*.txt        # Dependencies
```

### Ignored by Git
```
dna.json                 # State (runtime)
.identity.json          # Identity (runtime)
.dna_backups/           # Backups (runtime)
venv/                   # Virtual environment
__pycache__/            # Python cache
*.pyc, *.pyo            # Compiled Python
.pytest_cache/          # Test cache
logs/                   # Log files
data/                   # User data
.env                    # Secrets
```

### Runtime-Generated (Ignored)
```
soma/generated/         # Auto-generated organs
soma/experimental/      # Experimental organs
events.log              # Event log
memory_journal.json     # Memory journal
```

## Installation Locations

After running `./install.sh`:

| What | Where | Owner |
|------|-------|-------|
| SEAA source | `seaa/` | Tracked in git |
| Core organs | `soma/` | Tracked in git |
| Config | `config.yaml` | Tracked in git |
| Virtual env | `venv/` | Auto-created, git-ignored |
| State | `dna.json` | Auto-created, git-ignored |
| Identity | `.identity.json` | Auto-created, git-ignored |
| Tests | `tests/` | Tracked in git |
| Docs | `*.md` | Tracked in git |

## Getting Started

1. **Install**: `./install.sh`
2. **Read**: `INSTALL.md` → `QUICK_START.md`
3. **Run**: `python3 main.py` or `python3 main.py -i`
4. **Check**: `python3 main.py status`
5. **Learn**: `ARCHITECTURE_FINAL.md`

