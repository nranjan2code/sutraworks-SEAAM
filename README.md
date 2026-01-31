<div align="center">
  <h1>🧬 Self-Evolving Autonomous Agent (SEAA)</h1>
  <h3>The Agent That Writes Itself</h3>

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
  [![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()
  [![Autonomous Evolution](https://img.shields.io/badge/Autonomous-Evolving-blue.svg)]()

  > *An experiment in digital autopoiesis—code that creates, evolves, and improves itself.*

  [Installation](#-installation) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation) • [GitHub](https://github.com/nranjan2code/sutraworks-SEAAM)

</div>

---

## 🎯 What is SEAA?

SEAA is a self-evolving autonomous agent that:

- **Creates itself** - Starts with a minimal kernel and evolves by generating its own organs (Python modules)
- **Remembers itself** - Instance identity persists across resets (`.identity.json`)
- **Learns from failures** - All failures recorded in DNA; circuit breaker prevents cascading errors
- **Evolves autonomously** - System designs new capabilities, generates code, and integrates them without human intervention
- **Maintains clean code** - Immutable kernel protects core logic; runtime organs isolated from git history
- **Ships with everything** - 25 core organs included; ready to deploy and run

### Key Innovation: Dual-Layer Architecture

```
┌─────────────────────────────────────────┐
│  DEVELOPER LAYER (.git repository)      │
│  • seaa/ (immutable kernel)              │
│  • soma/ (25 core organs - tracked)      │
│  • tests/, docs/ (human-written)         │
├─────────────────────────────────────────┤
│  SYSTEM LAYER (DNA persistence)         │
│  • dna.json (current state)              │
│  • .dna_backups/ (evolution history)     │
│  • .identity.json (persists on resets!)  │
│  • soma/generated/ (runtime organs)      │
└─────────────────────────────────────────┘
```

**Result:** System evolves independently while developers maintain clean git history!

---

## ⚡ Installation

### One-Command Setup
```bash
git clone https://github.com/nranjan2code/sutraworks-SEAAM.git
cd sutraworks-SEAAM
./install.sh
```

The installer automatically:
- ✓ Checks Python 3.9+
- ✓ Creates isolated virtual environment
- ✓ Installs all dependencies
- ✓ Configures LLM (Ollama, Gemini, or custom)
- ✓ Verifies installation
- ✓ Runs tests

### Installation Options

```bash
./install.sh                  # Standard installation
./install.sh --dev            # With development tools
./install.sh --with-cli       # With interactive CLI
./install.sh --skip-llm       # Use existing LLM config
```

### Alternative: pip Installation
```bash
pip install git+https://github.com/nranjan2code/sutraworks-SEAAM.git
```

### LLM Configuration

**Ollama (Recommended for local development)**
```bash
ollama pull qwen2.5-coder:14b
ollama serve
```
SEAA is pre-configured for Ollama at `http://localhost:11434`

**Google Gemini (Cloud)**
```bash
export GOOGLE_API_KEY=your_key_here
```
Update `config.yaml` to use Gemini model.

See [docs/guides/INSTALL.md](docs/guides/INSTALL.md) for detailed setup.

---

## 🚀 Quick Start

### Using Management Script (Recommended)
The easiest way to start, manage, and monitor SEAA:

```bash
# Start the system (launches everything: API, web, evolution)
./manage.sh start

# Check status
./manage.sh status

# View logs
./manage.sh logs -f

# Stop when done
./manage.sh stop
```

See [MANAGEMENT.md](MANAGEMENT.md) for full management script guide.

### Or Start Directly
```bash
python3 main.py                     # Start system (auto-launches API & web)
python3 main.py -i                  # Interactive REPL mode
```

### Common Operations
```bash
./manage.sh health              # Detailed system health
./manage.sh organs              # List organs with status
./manage.sh watch               # Live event stream
./manage.sh goals               # Goal satisfaction progress
./manage.sh failures            # Failure records
./manage.sh restart             # Restart the system
./manage.sh reset               # Reset (keeps instance identity)
```

Full command reference: See [MANAGEMENT.md](MANAGEMENT.md) and [docs/guides/QUICK_START.md](docs/guides/QUICK_START.md)

---

## 🏗️ Architecture

### Four Biological Layers

#### 1. **Kernel** (Immutable Foundation)
Located in `seaa/kernel/`, the kernel is unchangeable at runtime and provides:
- `genesis.py` - Evolution orchestrator
- `bus.py` - Event communication
- `assimilator.py` - Dynamic module loading
- `materializer.py` - Atomic file operations
- `immunity.py` - Error recovery
- `identity.py` - Persistent instance identity
- `observer.py` - System introspection

**Protection:** Cannot be modified by the system itself; all code is validated before execution.

#### 2. **Cortex** (The Mind)
Located in `seaa/cortex/`, responsible for reasoning:
- `architect.py` - Designs new organs based on DNA
- `prompt_loader.py` - Loads YAML reasoning templates

#### 3. **Soma** (The Body)
`soma/` directory contains organs created by the system:

**Core Organs (shipped & tracked):**
- `soma/perception/` - File system monitoring
- `soma/memory/` - Event journaling
- `soma/interface/` - REST API & dashboards
- `soma/storage/` - Data persistence (SQLite)
- `soma/extensions/` - Metrics & health checks
- `soma/learning/` - Self-improvement modules
- Plus 19 more...

**Runtime Organs (auto-generated, not tracked):**
- `soma/generated/` - New organs created at runtime
- `soma/experimental/` - Experimental features

#### 4. **Observability** (The Eyes)
Always available, even when soma is broken:
- Instance identity (UUID, name, lineage)
- System health status
- Organ health metrics
- Event streaming
- Evolution timeline

---

## 🛡️ Autonomous Self-Correction

SEAA is designed to survive failures in its own evolution:

```
Organ Fails → Classify Error
             ├─→ Import Error → Missing soma module? → Add to blueprint
             ├─→ Validation Error → Invalid code? → Architect redesigns
             ├─→ Runtime Error → Stop organ, log failure
             └─→ Circuit Open → Skip for 30 min (configurable)
```

**Safety Mechanisms:**
- **Code Validation** - AST checking, forbidden imports detection (pip, subprocess, eval)
- **Circuit Breaker** - 3 failures = 30-minute cooldown (prevents cascading failures)
- **Module Contracts** - All organs must have valid `start()` function
- **DNA Integrity** - SHA-256 verification
- **Learning** - All failures recorded for the Architect to learn from

---

## 📚 Documentation

All documentation is organized in `docs/`:

| Need | Location |
|------|----------|
| **Installation Guide** | [docs/guides/INSTALL.md](docs/guides/INSTALL.md) |
| **5-Minute Quick Start** | [docs/guides/QUICK_START.md](docs/guides/QUICK_START.md) |
| **Where to Start** | [docs/guides/START_HERE.md](docs/guides/START_HERE.md) |
| **System Architecture** | [docs/architecture/ARCHITECTURE_FINAL.md](docs/architecture/ARCHITECTURE_FINAL.md) |
| **Dual-Layer Design** | [docs/architecture/ARCHITECTURE_LAYERS.md](docs/architecture/ARCHITECTURE_LAYERS.md) |
| **Design Patterns** | [docs/design/CORE_ORGANS_DESIGN.md](docs/design/CORE_ORGANS_DESIGN.md) |
| **Current Organs** | [docs/design/CORE_ORGANS_IMPLEMENTATION.md](docs/design/CORE_ORGANS_IMPLEMENTATION.md) |
| **Project Status** | [docs/evolution/CURRENT_STATUS.md](docs/evolution/CURRENT_STATUS.md) |
| **Documentation Hub** | [docs/README.md](docs/README.md) |

---

## 💡 Key Features

### ✅ Production Ready
- Comprehensive error handling
- Circuit breaker pattern
- DNA integrity verification
- Structured logging (JSON/colored output)
- Thread-safe operations

### ✅ Distribution Ready
- One-command installation (`./install.sh`)
- pip-installable package
- All core organs included
- Professional documentation (31 files)
- Clean repository (1 markdown file in root)

### ✅ Developer Friendly
- Clear architecture
- Extensive documentation
- Easy to extend with new organs
- Interactive REPL with rich UI
- Comprehensive CLI commands

### ✅ Autonomous Evolution
- Designs its own architecture
- Generates Python code
- Validates and integrates new modules
- Learns from failures
- Maintains evolution history

---

## 🔄 The Evolution Cycle

```
1. System analyzes DNA (current state)
2. Architect designs new organs to satisfy goals
3. System generates Python code
4. Code is validated (AST, imports, signature)
5. Organ is materialized (atomic file write)
6. Organ is assimilated (hot-loaded)
7. Results recorded in DNA for learning
```

This cycle repeats every 30 seconds (configurable).

---

## 🎓 For Different Roles

### Users
Want to deploy and run SEAA?
1. Clone repository
2. Run `./install.sh`
3. Start with `python3 main.py`
4. Read [QUICK_START.md](docs/guides/QUICK_START.md)

### Developers
Want to understand the system?
1. Read [START_HERE.md](docs/guides/START_HERE.md)
2. Study [ARCHITECTURE_FINAL.md](docs/architecture/ARCHITECTURE_FINAL.md)
3. Review [ARCHITECTURE_LAYERS.md](docs/architecture/ARCHITECTURE_LAYERS.md)
4. Explore source code in `seaa/`

### Contributors
Want to add features?
1. Follow [docs/internal/CLAUDE.md](docs/internal/CLAUDE.md)
2. Study [CORE_ORGANS_DESIGN.md](docs/design/CORE_ORGANS_DESIGN.md)
3. Check [IMPLEMENTATION_ROADMAP.md](docs/design/IMPLEMENTATION_ROADMAP.md)
4. Submit pull requests

### Researchers
Interested in the design?
1. Read [ARCHITECTURE_VISION.md](docs/architecture/ARCHITECTURE_VISION.md)
2. Review [ARCHITECTURE_EVOLUTION.md](docs/architecture/ARCHITECTURE_EVOLUTION.md)
3. Check [evolution reports](docs/evolution/)
4. Publish your findings!

---

## 📋 Directory Structure

```
.
├── README.md                 ← You are here
├── install.sh                ← One-command installer
├── setup.py                  ← pip configuration
├── main.py                   ← Entry point
├── config.yaml               ← System configuration
├── requirements.txt          ← Dependencies
├── requirements-dev.txt      ← Dev dependencies
│
├── seaa/                     ← Immutable kernel (never modified by system)
│   ├── kernel/               (orchestration, event bus, materializer)
│   ├── core/                 (logging, config, exceptions)
│   ├── dna/                  (persistence, validation)
│   ├── cortex/               (reasoning, design)
│   ├── cli/                  (interactive REPL)
│   └── connectors/           (LLM abstraction)
│
├── soma/                     ← Evolved organs
│   ├── perception/           (✓ tracked, file system monitoring)
│   ├── memory/               (✓ tracked, event journals)
│   ├── interface/            (✓ tracked, REST API)
│   ├── storage/              (✓ tracked, SQLite)
│   ├── extensions/           (✓ tracked, metrics)
│   ├── learning/             (✓ tracked, self-improvement)
│   ├── generated/            (runtime organs, ignored)
│   └── experimental/         (experimental, ignored)
│
├── tests/                    ← Comprehensive test suite
│
├── docs/                     ← Professional documentation
│   ├── guides/               (installation, quick start)
│   ├── architecture/         (system design)
│   ├── design/               (implementation specs)
│   ├── evolution/            (project history)
│   └── internal/             (reference materials)
│
└── .gitignore                ← Tracks core organs, ignores system state
```

See [docs/internal/DIRECTORY.md](docs/internal/DIRECTORY.md) for details.

---

## 🌱 Example: What SEAA Can Do

### Example 1: Autonomous Organ Evolution
SEAA detects it needs file system monitoring:
```
Genesis: "We need to perceive the file system"
    ↓
Architect: "I'll design a file_system_observer organ"
    ↓
[Generates Python code]
    ↓
Validator: "Code looks good ✓"
    ↓
Materializer: [Atomic file write to soma/perception/file_system_observer.py]
    ↓
Assimilator: [Hot-load the organ]
    ↓
DNA: "soma.perception.file_system_observer integrated ✓"
```

### Example 2: Error Recovery
A REST API organ crashes:
```
Error: "Connection refused"
    ↓
Immunity: "Attempt 1/3 - retry in 30 min"
    ↓
[30 minutes later]
    ↓
Immunity: "Attempt 2/3 - retry"
    ↓
If still failing after 3 attempts: Circuit Open → Skip for 30 min
    ↓
DNA: [Records failure for Architect to learn from]
```

### Example 3: Instance Persistence
User resets system:
```
python3 main.py --reset
    ↓
dna.json: [Wiped - back to initial state]
.identity.json: [PRESERVED - instance remembers itself!]
    ↓
System starts fresh but knows its own identity
$ python3 main.py identity
Robinson (550e8400-e29b-41d4-a716-446655440000)
```

---

## 🔗 Community & Support

- **Documentation**: [docs/README.md](docs/README.md)
- **Management Script**: [MANAGEMENT.md](MANAGEMENT.md) - Start, stop, monitor
- **Web API Launch**: [WEB_API_LAUNCH.md](WEB_API_LAUNCH.md) - API endpoints & frontend
- **Installation Help**: [docs/guides/INSTALL.md](docs/guides/INSTALL.md)
- **Troubleshooting**: [docs/guides/TROUBLESHOOTING.md](docs/guides/TROUBLESHOOTING.md)
- **Report Issues**: [GitHub Issues](https://github.com/nranjan2code/sutraworks-SEAAM/issues)
- **Contribute**: [docs/internal/CLAUDE.md](docs/internal/CLAUDE.md)

---

## 📄 License

SEAA is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <p><strong>Built with ❤️ for autonomous evolution</strong></p>
  <p><a href="https://github.com/nranjan2code/sutraworks-SEAAM">GitHub</a> • <a href="docs/">Documentation</a> • <a href="docs/guides/INSTALL.md">Install</a></p>
</div>
