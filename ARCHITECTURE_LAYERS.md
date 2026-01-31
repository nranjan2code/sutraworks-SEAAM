# SEAA Dual-Layer Architecture

## Overview

SEAA operates with **two independent persistence layers**:

1. **DEVELOPER LAYER** - Traditional git repository for human developers
2. **SYSTEM LAYER** - DNA-based persistence for autonomous system evolution

This architecture allows:
- ✅ System to evolve independently (create organs, modify behavior)
- ✅ Developers to manage code via version control (git)
- ✅ Clean separation of concerns
- ✅ System identity and evolution to survive developer resets
- ✅ Independent improvement of both layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    SEAA Dual-Layer System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  DEVELOPER LAYER (.git repository)                              │
│  └─ seaa/               (Immutable kernel - never modified)    │
│  └─ soma/ (core)        (Core organs shipped with system)      │
│  └─ tests/              (Test suite)                           │
│  └─ docs/               (Documentation)                        │
│  └─ config.yaml         (Configuration)                        │
│  └─ *.md                (Markdown guides)                      │
│  └─ setup.py, install.sh, requirements*.txt                   │
│                                                                  │
│  SYSTEM LAYER (DNA persistence)                                 │
│  └─ dna.json            (Current system state)                 │
│  └─ .dna_backups/       (Evolution history)                    │
│  └─ .identity.json      (Instance identity - persists resets) │
│  └─ events.log          (Runtime event log)                    │
│  └─ soma/generated/     (Runtime-created organs)               │
│  └─ soma/experimental/  (Experimental organs)                  │
│  └─ memory_journal.json (System memory log)                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Layer 1: Developer Layer (Git Repository)

### Purpose
Maintain the stable, human-curated foundation of the system.

### Contents

#### Kernel (Immutable)
```
seaa/
├── kernel/         # Core orchestrator, bus, materializer, immunity
├── core/           # Logging, config, exceptions
├── dna/            # Data structures and persistence
├── cortex/         # Prompts and reasoning templates
├── cli/            # Interactive REPL and commands
└── connectors/     # LLM abstraction layer
```

**Key Property:** The kernel CANNOT be modified by the system itself. It's the trusted foundation.

#### Core Organs (Tracked)
```
soma/
├── perception/     # file_system_observer.py
├── memory/         # journal.py (event storage)
├── interface/      # web_api.py (REST endpoints)
├── storage/        # sqlite.py (database)
├── extensions/     # metrics.py (metrics collection)
├── learning/       # 6 self-improvement organs
└── kernel/         # Extended kernel organs
```

**Key Property:** These are the "starter organs" shipped with every SEAA instance. They provide essential capabilities.

#### Configuration & Metadata
```
config.yaml         # System settings
setup.py            # pip configuration
install.sh          # Installation script
requirements*.txt   # Dependencies
.gitignore          # Git configuration (explains both layers)
```

#### Documentation
```
INSTALL.md          # Installation guide
DIRECTORY.md        # Repository structure
ARCHITECTURE_FINAL.md
ARCHITECTURE_LAYERS.md  # This file
QUICK_START.md
...and more
```

#### Tests
```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── conftest.py     # Test fixtures
```

### Git Operations

```bash
# Core organs are tracked
git add soma/perception/
git add soma/memory/
git commit -m "feat: Add new core organ"

# System state is never committed
git add -A  # Only adds tracked files, not dna.json

# To see what's tracked
git ls-files soma/
```

### Development Workflow

1. **Add Core Organ:** If system discovers a need for a standard organ
   ```bash
   git add soma/new_organ/
   git commit -m "feat: Add soma.new_organ capability"
   ```

2. **Update Kernel:** If kernel fixes are needed
   ```bash
   git add seaa/kernel/component.py
   git commit -m "fix: kernel security or performance"
   ```

3. **Update Documentation:** Keep guides in sync
   ```bash
   git add ARCHITECTURE_LAYERS.md
   git commit -m "docs: Update architecture explanation"
   ```

4. **Never commit system state:**
   ```bash
   # ❌ DON'T DO THIS
   git add dna.json              # Never!
   git add .identity.json        # Never!
   git add .dna_backups/         # Never!
   ```

## Layer 2: System Layer (DNA Persistence)

### Purpose
Track the system's autonomous evolution and maintain identity across resets.

### Contents

#### Current State (dna.json)
```json
{
  "system_version": "1.0.0",
  "blueprint": {
    "soma.perception.observer": { ... },
    "soma.memory.journal": { ... }
  },
  "active_modules": ["soma.perception.observer", ...],
  "goals": [ ... ],
  "failures": [ ... ],
  "metadata": {
    "total_evolutions": 42,
    "uptime_seconds": 3600
  }
}
```

**Purpose:** Complete system state that can be loaded to restore the agent.

#### Evolution History (.dna_backups/)
```
.dna_backups/
├── dna_20260131_131905.json  # Snapshot from 13:19:05
├── dna_20260131_132005.json  # Snapshot from 13:20:05
├── dna_20260131_132040.json  # Snapshot from 13:20:40
└── ...                        # One backup per state change
```

**Purpose:** Full history of system evolution. Can trace all changes.

**Retention:** Keeps backups for debugging and learning.

#### Instance Identity (.identity.json)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Robinson",
  "genesis_time": "2026-01-30T10:45:00Z",
  "lineage": "dna_hash_at_birth",
  "parent_id": null
}
```

**Key Property:** This SURVIVES resets. The system can be reset to tabula rasa, but retains its identity.

```bash
# Reset system (new DNA, same identity)
python3 main.py --reset

# Identity persists
python3 main.py identity
# Output: Robinson (550e8400...)
```

#### System Logs

**events.log** - Event stream from event bus
```
[2026-01-31T13:20:05.123Z] module.loaded: soma.perception.observer
[2026-01-31T13:20:06.456Z] organ.started: soma.perception.observer
[2026-01-31T13:20:07.789Z] goal.satisfied: I must perceive filesystem
```

**memory_journal.json** - System memory and observations
```json
{
  "observations": [
    { "timestamp": "...", "type": "goal_achieved", "data": {...} },
    { "timestamp": "...", "type": "organ_failure", "data": {...} }
  ],
  "insights": [ ... ]
}
```

#### Runtime-Generated Organs

**soma/generated/** - Created by system at runtime
```
soma/generated/
├── autonomous_scheduler/     # Auto-created scheduler
├── advanced_learning/        # Advanced learning system
└── mesh_coordinator/         # Multi-instance orchestration
```

**Key Property:** These are NOT tracked in git. They're created based on system needs and discarded on `--reset`.

**soma/experimental/** - Experimental organs
```
soma/experimental/
├── new_idea_v1/
├── test_hypothesis/
└── prototype_organ/
```

**Key Property:** System tries experimental organs here before promoting to production.

### System Operations

```bash
# Save current state (automatic every cycle)
# dna.json updated, backup created

# Check evolution history
ls -lh .dna_backups/ | tail -5

# Reset to tabula rasa (but keep identity!)
python3 main.py --reset
# Identity preserved: .identity.json unchanged
# DNA reset: dna.json reset to initial state
# Backup saved: dna_backup.json created

# View system identity
cat .identity.json

# View DNA state
cat dna.json | python3 -m json.tool
```

## Interaction Between Layers

### System Evolution Flow

```
1. Developer releases SEAA with core organs (Layer 1)
   └─ soma/perception/, soma/memory/, etc.

2. User runs: python3 main.py
   └─ System loads dna.json (or creates if missing)
   └─ System loads core organs from soma/
   └─ System initializes .identity.json

3. System cycles and evolves
   └─ Creates new organs in soma/generated/
   └─ Updates dna.json with new blueprint
   └─ Saves backup to .dna_backups/
   └─ Logs events to events.log
   └─ Records memory in memory_journal.json

4. Developer wants to add core capability
   └─ Designs new organ in soma/learning/
   └─ Commits to git: git add soma/learning/new_thing.py
   └─ Tags release: v1.2.0

5. User upgrades SEAA (git pull)
   └─ New core organs available
   └─ System loads them on next start
   └─ Can integrate them into blueprint
   └─ Existing identity preserved!

6. User resets (python3 main.py --reset)
   └─ dna.json wiped (back to initial state)
   └─ .identity.json preserved (same instance!)
   └─ soma/generated/ deleted
   └─ Core organs still available from Layer 1
```

## File Ownership & Modification Rights

| Layer | File/Folder | Owner | Can Modify | Tracked | Notes |
|-------|-------------|-------|-----------|---------|-------|
| **Developer** | seaa/kernel/ | Developers | ✅ Carefully | Git | Immutable at runtime |
| **Developer** | soma/(core) | Both | ✅ Dev → Git | Git | Core organs shipped |
| **Developer** | tests/ | Developers | ✅ | Git | Test suite |
| **Developer** | docs/ | Developers | ✅ | Git | Documentation |
| **System** | dna.json | System | ✅ Auto | Git-ignored | Current state |
| **System** | .dna_backups/ | System | ✅ Auto | Git-ignored | Evolution history |
| **System** | .identity.json | System | ✅ Auto | Git-ignored | Instance identity |
| **System** | soma/generated/ | System | ✅ Auto | Git-ignored | Runtime organs |
| **System** | events.log | System | ✅ Auto | Git-ignored | Event stream |

## .gitignore Strategy

The `.gitignore` file explicitly documents this dual-layer design:

```
# DEVELOPER LAYER (tracked in git)
# seaa/          - Immutable kernel
# soma/          - Core organs
# tests/         - Test suite
# docs/          - Documentation

# SYSTEM LAYER (ignored - system manages this)
dna.json                  # Current state
.dna_backups/            # Evolution history
.identity.json           # Instance identity
soma/generated/          # Runtime organs
events.log               # Event stream
```

### Adding New Core Organs

If adding a new core organ that should ship with the system:

1. **Create the organ in soma/**
   ```bash
   mkdir soma/your_capability/
   echo "def start(): pass" > soma/your_capability/__init__.py
   ```

2. **Update .gitignore** (if needed)
   ```
   # If it's NOT soma/generated or soma/experimental,
   # it's automatically tracked!
   ```

3. **Commit to git**
   ```bash
   git add soma/your_capability/
   git commit -m "feat: Add soma.your_capability core organ"
   ```

## Benefits of Dual-Layer Design

### For System Evolution
✅ System can create organs without git noise
✅ System maintains identity across resets
✅ System has full evolution history in .dna_backups/
✅ System can experiment in soma/generated/ and soma/experimental/
✅ System learns from its own failures (in dna.json)

### For Developers
✅ Clean git history (no auto-generated files)
✅ Easy to track code changes
✅ Core capabilities always available
✅ Can upgrade SEAA without losing system state
✅ Can reset system without code changes

### For Distribution
✅ One git repo with everything needed
✅ Clone + install.sh = working system
✅ System evolution is data (dna.json), not code
✅ Can inspect evolution by reading dna.json
✅ Can publish new versions as system learns

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      SEAA Instance                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ DEVELOPER LAYER (.git)                                 │  │
│  │ Humans manage these with git                           │  │
│  │                                                        │  │
│  │ seaa/kernel/    (Immutable seed)                       │  │
│  │ seaa/core/      (Infrastructure)                       │  │
│  │ seaa/cortex/    (Reasoning templates)                  │  │
│  │ soma/           (Core organs - 25 files)               │  │
│  │ tests/          (Test suite)                           │  │
│  │ docs/           (Documentation)                        │  │
│  │ config.yaml     (Configuration)                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ SYSTEM LAYER (DNA persistence)                         │  │
│  │ System manages these automatically                      │  │
│  │                                                        │  │
│  │ dna.json           (Current state)                      │  │
│  │ .dna_backups/      (Evolution history)                  │  │
│  │ .identity.json     (Instance identity)                  │  │
│  │ soma/generated/    (Runtime organs)                     │  │
│  │ soma/experimental/ (Experimental organs)                │  │
│  │ events.log         (Event stream)                       │  │
│  │ memory_journal.json (System memory)                     │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Typical Workflows

### Workflow 1: Deploy SEAA
```bash
git clone https://github.com/sutraworks/seaa.git
cd seaa
./install.sh

# Now you have:
# ✅ Developer layer from git
# ✅ System layer created on first run
#    - dna.json initialized
#    - .identity.json created
#    - core organs loaded from soma/
```

### Workflow 2: System Evolves
```bash
# System discovers it needs new capability
# Creates: soma/generated/new_organ/

# System improves itself
# Updates: dna.json with new blueprint
# Backup: .dna_backups/dna_20260131_132337.json

# Developers can inspect
cat dna.json | python3 -m json.tool | less
ls -lh .dna_backups/ | tail -10
```

### Workflow 3: Developer Adds Core Organ
```bash
# Developer creates new core capability
mkdir soma/mesh_coordination/
git add soma/mesh_coordination/
git commit -m "feat: Add mesh coordination capability"
git push

# Users can upgrade
git pull
python3 main.py  # New organs available!

# System's identity & history preserved
cat .identity.json  # Same instance ID!
```

### Workflow 4: System Reset with Persistence
```bash
# System has evolved 100 iterations
python3 main.py status
# Organs: 45/50 healthy, goals: 8/10 satisfied

# Reset to initial state (but keep identity)
python3 main.py --reset

# Backup created, DNA reset, but identity preserved
cat .identity.json  # Still Robinson!
python3 main.py status
# Organs: 25/25 healthy (core only), goals: 2/10 satisfied
```

## Key Takeaways

1. **Two Independent Layers**
   - Developer layer: git-tracked code
   - System layer: DNA-based persistence

2. **Core Organs Ship with System**
   - soma/perception/, soma/memory/, etc.
   - Available from day 1
   - Tracked in git for everyone to use

3. **System Can Evolve Autonomously**
   - Creates soma/generated/ organs at runtime
   - Not tracked (clean git history)
   - Discarded on reset

4. **Identity Persists Across Resets**
   - .identity.json survives --reset
   - Instance is reborn but remembers itself
   - Enables long-term persistence

5. **Evolution is Traceable**
   - .dna_backups/ keeps all history
   - Can inspect what changed and why
   - Supports analysis and learning

This architecture makes SEAA uniquely capable of autonomous, persistent, self-directed evolution while remaining manageable and distributable by human developers.
