# SEAA Quick Start Guide

**Get Robinson running and understand the system in 10 minutes.**

---

## Installation (1 minute)

```bash
# Already installed if you're here!
# Just verify Python 3.9+
python3 --version

# Install minimal dependencies if needed
pip install watchdog pyyaml prompt-toolkit rich
```

---

## First Run (2 minutes)

```bash
# Start the system (runs for ~30 seconds)
python3 main.py

# You'll see:
# ✓ Genesis awakening
# ✓ Events being published
# ✓ Organs being assimilated
# ✓ Graceful shutdown

# Press Ctrl+C to stop
```

---

## Check Status (1 minute)

```bash
# System health
python3 main.py status

# List organs
python3 main.py organs

# Show goals
python3 main.py goals

# See evolution history
python3 main.py timeline

# Watch events live
python3 main.py watch
```

---

## Interactive Mode (3 minutes)

```bash
# Launch Rich UI with REPL
python3 main.py -i

# In the REPL, try:
status           # System status
organs           # Active organs
goals            # Goals progress
dashboard        # Full screen live view
watch            # Event stream
help             # All commands

# To exit:
exit
```

---

## Understand the Architecture (3 minutes)

### The Layers

```
┌─ KERNEL (seaa/)
│  - Orchestrates everything
│  - Makes decisions
│  - Never changes
│
├─ SOMA (soma/)
│  - Generated organs
│  - Do the work
│  - Can be rewritten
│
└─ DNA (dna.json)
   - System memory
   - Goals & blueprints
   - Persists across resets
```

### The Flow

```
Genesis (orchestrator)
  ↓
Architect (planner - "we need a journal")
  ↓
Gateway (calls LLM - "write Python code for journal")
  ↓
Materializer (writes code safely)
  ↓
Assimilator (hot-loads it)
  ↓
Event Bus (organs communicate via events)
  ↓
Observer (watches everything)
```

### What's Running Now

```
✓ soma.perception.file_system_observer
  └─ Watches filesystem for changes
  └─ Publishes file.created, file.modified, file.deleted events

⏳ soma.memory.journal
  └─ Designed but not yet active
  └─ Will store events when it evolves

⏳ soma.interface.web_api
  └─ Designed but not yet active
  └─ Will provide REST API when it evolves
```

---

## Common Commands

### View System State

```bash
# Full status with vitals
python3 main.py status

# Status as JSON (for parsing)
python3 main.py status --json

# List all organs
python3 main.py organs

# Show goal progress
python3 main.py goals

# Show evolution timeline
python3 main.py timeline --limit 50

# Show failures and recoveries
python3 main.py failures
```

### Monitor in Real-Time

```bash
# Watch events streaming
python3 main.py watch

# Watch specific event types
python3 main.py watch --pattern file.created

# Interactive mode (best UX)
python3 main.py -i
> dashboard          # Full screen live view
> watch              # Event stream
```

### Control the System

```bash
# Run the system (in foreground)
python3 main.py

# Run in interactive mode
python3 main.py -i
> start              # Start genesis
> stop               # Stop genesis

# Reset to clean state (keeps identity)
python3 main.py --reset

# With debug logging
python3 main.py --log-level DEBUG
```

### Manage Identity

```bash
# Show current identity
python3 main.py identity

# Set a custom name
python3 main.py identity --name "MyRobinson"

# View as JSON
python3 main.py identity --json
```

---

## Understanding Events

Events are the system's language. Every organ publishes events.

### Event Format

```json
{
  "event_type": "file.created",
  "timestamp": "2026-01-31T12:00:00Z",
  "data": {
    "path": "/Users/nisheethranjan/myfile.txt",
    "size": 1024
  }
}
```

### Common Events

```
soma.perception.file_system_observer publishes:
  - file.created
  - file.modified
  - file.deleted
  - file.moved

Genesis publishes:
  - organ.evolved
  - organ.assimilated
  - organ.failed

All organs publish:
  - organ.started
  - organ.stopped
  - organ.error
```

### Watch Specific Events

```bash
# Watch file changes only
python3 main.py watch --pattern file.

# Watch organ events only
python3 main.py watch --pattern organ.

# Watch everything (default)
python3 main.py watch
```

---

## Understanding DNA

DNA is the system's memory. It persists across restarts.

### What's in DNA?

```json
{
  "system_name": "SEAA-TabulaRasa",
  "system_version": "1.0.0",
  "blueprint": {
    "soma.perception.file_system_observer": {
      "status": "active",
      "version": 1
    },
    "soma.memory.journal": {
      "status": "designed",
      "version": 1
    }
  },
  "goals": [
    {
      "description": "I must perceive filesystem",
      "satisfied": true,
      "priority": 1
    }
  ],
  "active_modules": ["soma.perception.file_system_observer"],
  "failures": [],
  "metadata": {}
}
```

### View DNA

```bash
# Pretty-print the DNA
cat dna.json | python3 -m json.tool

# See goals
cat dna.json | jq .goals

# See active modules
cat dna.json | jq .active_modules

# See blueprint
cat dna.json | jq .blueprint
```

---

## Understanding Circuit Breakers

The system automatically disables organs that fail too much.

### How It Works

```
Organ tries to run
  ↓
If it fails:
  ↓
Increment attempt counter
  ↓
If attempts >= 3:
  ↓
Open circuit breaker (disable organ)
  ↓
Wait 30 minutes before retrying
  ↓
After 30 minutes: Try again
```

### View Circuit Breaker Status

```bash
# See failures
python3 main.py failures

# Status includes:
# - organ name
# - failure type
# - attempt count
# - last error message
```

### Reset Circuit Breaker (Manual)

```bash
# Reset via Python
python3 << 'EOF'
from seaa.dna.repository import DNARepository
from pathlib import Path
repo = DNARepository(Path('dna.json'))
dna = repo.load()
dna.reset_circuit('soma.organ.name')
repo.save(dna)
EOF
```

---

## Exploring the Code

### Key Files

```
main.py
  └─ Entry point, command handlers

seaa/
├── kernel/
│   ├── genesis.py           ← Main orchestrator
│   ├── bus.py               ← Event system
│   ├── assimilator.py       ← Module loader
│   ├── materializer.py      ← Code writer
│   ├── identity.py          ← Instance identity
│   └── observer.py          ← Introspection
├── cortex/
│   ├── architect.py         ← System designer
│   └── prompts/             ← LLM templates
├── core/
│   ├── config.py            ← Configuration
│   ├── logging.py           ← Structured logging
│   └── exceptions.py        ← Error types
└── cli/
    ├── repl.py              ← Interactive mode
    ├── commands.py          ← CLI commands
    └── ui/                  ← Rich dashboards

soma/
├── perception/
│   └── file_system_observer.py  (generated)
├── memory/                      (to be generated)
└── interface/                   (to be generated)

dna.json
  └─ System state & memory
```

### Reading Order

1. **main.py** - Understand commands
2. **seaa/kernel/genesis.py** - The orchestrator
3. **seaa/kernel/bus.py** - Event system
4. **seaa/dna/schema.py** - Data structures
5. **seaa/cortex/architect.py** - Design decisions
6. **soma/perception/file_system_observer.py** - Example organ

---

## Configuration

Config file: `config.yaml` (automatically loaded)

### Current Config Sections

```yaml
llm:
  provider: "ollama"         # or "gemini"
  model: "qwen2.5-coder:14b" # or "gemini-1.5-flash"
  temperature: 0.1           # Lower = more deterministic

paths:
  soma: "soma"               # Where organs go
  dna: "dna.json"            # System memory

metabolism:
  cycle_interval_seconds: 30 # How often to evolve
  max_organs_per_cycle: 3    # Limits

security:
  allow_pip_install: false   # Stay safe!
  allowed_pip_packages:
    - watchdog
    - fastapi

logging:
  level: "INFO"              # or "DEBUG"
  format: "colored"          # or "json"
```

### Override with Environment

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python3 main.py

# Use different LLM
LLM_PROVIDER=gemini python3 main.py
```

---

## Troubleshooting

### System won't start

```bash
# Check Python version
python3 --version  # Need 3.9+

# Check dependencies
pip install watchdog pyyaml prompt-toolkit rich

# Enable debug logging
python3 main.py --log-level DEBUG
```

### Organ failed

```bash
# View failures
python3 main.py failures

# It will auto-retry after 30 minutes
# Or manually reset: (see Circuit Breaker section)
```

### Want to see the DNA

```bash
cat dna.json | python3 -m json.tool
```

### Want to reset everything

```bash
# Reset to clean state (keeps identity + name)
python3 main.py --reset

# Then run again
python3 main.py
```

---

## Next Steps

1. **Try the interactive mode**:
   ```bash
   python3 main.py -i
   ```
   Then type: `dashboard`

2. **Watch it evolve**:
   ```bash
   python3 main.py watch
   ```
   Run for 5 minutes, see events flow

3. **Read the full docs**:
   - PLATFORM_REVIEW.md (architecture)
   - IMPLEMENTATION_ROADMAP.md (future)
   - ARCHITECTURE_VISION.md (4-week plan)

4. **When ready, deploy Week 1 organs**:
   - soma.memory.journal
   - soma.interface.web_api
   - React frontend

---

## Key Insights

### This is Not Normal Software

```
Traditional App:
  Developer → Code → Deploy → Runs

SEAA:
  System → Decides → Generates → Validates → Runs → Learns
```

### The Magic Ingredients

1. **Self-generated code** (LLM writes Python)
2. **AST validation** (safe code only)
3. **Hot-loading** (no restarts)
4. **Event bus** (organs communicate)
5. **Persistent memory** (DNA survives resets)
6. **Identity** (Robinson is always Robinson)

### What It Means

The system can:
- **Evolve** to meet new goals
- **Learn** what works and doesn't
- **Heal** its own failures
- **Improve** over time

---

## Commands Cheat Sheet

```bash
# Status & monitoring
python3 main.py status              # System health
python3 main.py organs              # Active organs
python3 main.py goals               # Goal progress
python3 main.py timeline            # Evolution history
python3 main.py watch               # Live events

# Identity
python3 main.py identity            # Show identity
python3 main.py identity --name X   # Set name

# Control
python3 main.py                     # Run (foreground)
python3 main.py -i                  # Interactive mode
python3 main.py --reset             # Clean state

# Output format
python3 main.py status --json       # JSON output
python3 main.py organs --json       # JSON organs

# Logging
python3 main.py --log-level DEBUG   # Debug mode
```

---

## Feeling Ready?

You now understand:
- ✓ How to run the system
- ✓ How to monitor it
- ✓ How it evolves
- ✓ How it recovers from failures
- ✓ The architecture

**Next:** Read IMPLEMENTATION_ROADMAP.md to understand the 4-week plan.

Then: Let Robinson grow! 🚀

