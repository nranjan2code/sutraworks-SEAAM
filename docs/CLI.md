# SEAA Interactive CLI

Complete guide to the SEAA Interactive Command Line Interface.

---

## Overview

The SEAA Interactive CLI provides a best-in-class terminal experience for interacting with the Self-Evolving Autonomous Agent. It features:

- **Interactive REPL** - Conversational interface with history and completion
- **Rich Terminal UI** - Tables, panels, spinners, and live dashboards
- **Natural Language** - Ask questions like "how are you?" or "show organs"
- **Typo Tolerance** - Fuzzy matching auto-corrects commands like "staus" to "status"
- **Tab Completion** - Complete commands, arguments, and organ names
- **Background Genesis** - Run the agent while interacting with it

---

## Installation

The interactive CLI requires additional dependencies:

```bash
# Install CLI dependencies
pip install seaa[cli]

# Or install manually
pip install rich prompt_toolkit humanize
```

---

## Quick Start

### Interactive Mode

```bash
# Launch interactive REPL
python main.py -i

# Or with the entry point
seaa -i
```

### One-Shot Commands

Existing commands still work without the interactive mode:

```bash
python main.py status
python main.py organs --all
python main.py goals --json
```

---

## The REPL

### Prompt

The REPL prompt shows:
- **Status indicator**: Green dot = Genesis running, Red dot = stopped
- **Instance name**: Your SEAA instance's name

```
● Robinson >
```

### Features

| Feature | Description |
|---------|-------------|
| History | Commands saved to `~/.seaa_history` |
| Tab completion | Press Tab for suggestions |
| History search | Ctrl+R to search history |
| Auto-suggest | Grayed suggestions from history |

### Example Session

```
● Robinson > status
╭──────────────────────────────────────╮
│  Robinson (713d8815)                 │
├──────────────────────────────────────┤
│  Status:     HEALTHY                 │
│  Genesis:    STOPPED                 │
│  Organs:     3/3 healthy             │
│  Goals:      2/4 satisfied           │
╰──────────────────────────────────────╯

● Robinson > how are you?
╭──────────────────────────────────────╮
│  Robinson (713d8815)                 │
...

● Robinson > staus
Auto-corrected: staus -> status
...

● Robinson > start
Starting Genesis...
Genesis awakened.

● Robinson > exit
Stopping Genesis...
Goodbye!
```

---

## Commands

### Observation Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `status` | `s` | Show system health and vitals |
| `organs` | `o`, `list` | List all organs with health |
| `goals` | `g` | Show goals and satisfaction |
| `failures` | `f`, `errors` | Show failure records |
| `dashboard` | `d`, `dash` | Live full-screen dashboard |
| `watch` | `w` | Stream events in real-time |
| `timeline` | `t`, `history` | Show evolution timeline |

### Control Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `start` | `run`, `awaken` | Start Genesis in background |
| `stop` | `kill`, `sleep` | Stop Genesis gracefully |
| `evolve` | `e`, `grow` | Trigger evolution cycle |

### Identity Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `identity` | `id`, `who` | Show or set identity |

### General Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `help` | `?`, `commands` | Show available commands |
| `clear` | `cls` | Clear the screen |
| `exit` | `q`, `quit`, `bye` | Exit the REPL |

---

## Natural Language

The CLI understands natural language queries:

### Status Queries
- "how are you?"
- "how's it going?"
- "what's up?"
- "health check"

### Organ Queries
- "show organs"
- "list organs"
- "what organs do you have?"

### Goal Queries
- "what's the progress?"
- "show goals"
- "objectives"

### Control
- "wake up" / "awaken" → start
- "go to sleep" / "shutdown" → stop
- "grow" / "evolve" → evolve

### Meta
- "who are you?" → identity
- "help me" → help
- "bye" / "goodbye" → exit

---

## Fuzzy Matching

The CLI corrects typos automatically:

| You Type | Corrected To |
|----------|--------------|
| `staus` | `status` |
| `oragns` | `organs` |
| `gaols` | `goals` |
| `dashbaord` | `dashboard` |

For close matches (>80% similarity), auto-correction is automatic.
For moderate matches (60-80%), you're asked for confirmation.

---

## Rich UI Components

### Status Panel

```
╭──────────────────────────────────────╮
│  Robinson (713d8815)                 │
├──────────────────────────────────────┤
│  Status:     HEALTHY                 │
│  Genesis:    RUNNING                 │
│  Uptime:     2h 15m                  │
│  DNA:        56271deda1e156e0        │
│                                      │
│  Organs:     3/3 healthy             │
│  Goals:      2/4 satisfied (50%)     │
│  Evolutions: 12                      │
╰──────────────────────────────────────╯
```

### Organs Table

```
                    Organs
┏━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃   ┃ Name                      ┃ Health   ┃
┡━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ ● │ soma.perception.observer  │ ● healthy│
│ ● │ soma.memory.journal       │ ● healthy│
│ ○ │ soma.interface.dashboard  │ ○ stopped│
└───┴───────────────────────────┴──────────┘
```

### Goals Table

```
                    Goals
┏━━━┳━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃   ┃ P ┃ Description                     ┃
┡━━━╇━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ✓ │ 1 │ I must perceive the filesystem  │
│ ✓ │ 1 │ I must have a memory            │
│ ○ │ 2 │ I must be observable            │
└───┴───┴─────────────────────────────────┘
```

---

## Live Dashboard

The dashboard provides a full-screen, auto-updating view:

```bash
● Robinson > dashboard
```

Layout:
```
┌─────────────────────────────────────────────────┐
│  Robinson (713d8815) - Genesis: RUNNING         │
├────────────────────────┬────────────────────────┤
│  Vitals                │  Organs                │
│  ─────────────────     │  ─────────────────     │
│  Health:  HEALTHY      │  ● soma.perception     │
│  Uptime:  2h 15m       │  ● soma.memory         │
│  Organs:  3/3          │  ● soma.interface      │
│                        │                        │
├────────────────────────┼────────────────────────┤
│  Goals                 │  Recent Events         │
│  ─────────────────     │  ─────────────────     │
│  ✓ Perceive files      │  14:32:15 ↑ evolved    │
│  ✓ Have memory         │  14:32:16 ↑ integrated │
│  ○ Be observable       │  14:32:45 • heartbeat  │
├────────────────────────┴────────────────────────┤
│  q quit  r refresh  s start/stop Genesis        │
└─────────────────────────────────────────────────┘
```

Press `q` or `Ctrl+C` to exit.

---

## Event Streaming

Watch events in real-time:

```bash
● Robinson > watch
Streaming events... (Ctrl+C to stop)

14:32:15 organ.evolved organ=soma.perception.observer
14:32:16 organ.integrated organ=soma.perception.observer
14:32:45 system.heartbeat running_organs=3, pending=0
```

Filter by pattern:
```bash
● Robinson > watch organ.evolved
```

---

## Background Genesis

The REPL can start/stop Genesis in the background:

```bash
● Robinson > start
Starting Genesis...
Genesis awakened.

● Robinson > status
...
Genesis:    RUNNING
...

● Robinson > stop
Stopping Genesis...
Genesis asleep.
```

While Genesis runs, you can:
- Query status and organs
- Watch events
- Trigger evolution cycles
- Use the live dashboard

---

## Tab Completion

Press Tab to complete:

### Commands
```
● Robinson > sta<Tab>
start   status  stop
```

### Arguments
```
● Robinson > organs --<Tab>
--all   --json   --help
```

### Organ Names (for watch/timeline)
```
● Robinson > watch soma.<Tab>
soma.perception.observer   soma.memory.journal
```

---

## Command Arguments

### status
```bash
status              # Rich panel output
status --json       # JSON output
```

### organs
```bash
organs              # Active organs only
organs --all        # Include stopped organs
organs --json       # JSON output
```

### goals
```bash
goals               # Rich table output
goals --json        # JSON output
```

### failures
```bash
failures            # Rich table output
failures --json     # JSON output
```

### timeline
```bash
timeline            # Last 20 events
timeline --limit 50 # Last 50 events
timeline --json     # JSON output
```

### identity
```bash
identity            # Show current identity
identity --name X   # Set instance name
identity --json     # JSON output
```

### watch
```bash
watch               # All events
watch organ.evolved # Filter by pattern
```

---

## Architecture

### Package Structure

```
seaa/cli/
├── __init__.py          # Package init with lazy imports
├── commands.py          # Command registry
├── handlers.py          # Command implementations
├── completers.py        # Tab completion
├── repl.py              # REPL loop
├── runtime.py           # Genesis background manager
├── parsers/
│   ├── fuzzy.py         # Typo correction
│   └── natural.py       # Natural language
└── ui/
    ├── formatters.py    # Output helpers
    ├── panels.py        # Rich panels
    ├── tables.py        # Rich tables
    └── dashboard.py     # Live dashboard
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `rich` | >=13.0.0 | Terminal UI (tables, panels, live) |
| `prompt_toolkit` | >=3.0.0 | REPL infrastructure |
| `humanize` | >=4.0.0 | Human-readable times (optional) |

---

## Configuration

### History File

Command history is saved to `~/.seaa_history` by default.

### Prompt Style

The prompt uses ANSI colors:
- Green dot: Genesis running
- Red dot: Genesis stopped
- Cyan: Instance name

---

## Troubleshooting

### "Interactive mode requires additional dependencies"

Install the CLI dependencies:
```bash
pip install seaa[cli]
# or
pip install rich prompt_toolkit
```

### Tab completion not working

Ensure `prompt_toolkit` is installed and you're using a compatible terminal.

### Dashboard not rendering correctly

- Use a terminal that supports Unicode
- Ensure terminal is at least 80x24
- Try resizing the terminal

### Genesis won't start

Check the logs:
```bash
python main.py --log-level DEBUG
```

Common issues:
- Ollama not running
- Invalid configuration
- Port conflicts

---

## API Reference

### Command Registry

```python
from seaa.cli.commands import get_registry, Command

# Get registry
registry = get_registry()

# Register custom command
cmd = Command(
    name="mycommand",
    handler=my_handler,
    description="My custom command",
    aliases=["mc"],
    natural_triggers=["do my thing"],
)
registry.register(cmd)
```

### Fuzzy Matching

```python
from seaa.cli.parsers.fuzzy import fuzzy_match, get_best_match

# Find matches
matches = fuzzy_match("staus", ["status", "stop"], threshold=0.6)
# [("status", 0.83)]

# Get best match
result = get_best_match("staus", ["status", "stop"])
# ("status", 0.83)
```

### Natural Language

```python
from seaa.cli.parsers.natural import detect_intent

intent = detect_intent("how are you?")
# "status"

intent = detect_intent("show organs")
# "organs"
```

### Runtime Manager

```python
from seaa.cli.runtime import get_runtime

runtime = get_runtime()

# Start Genesis
runtime.start()

# Check status
if runtime.is_running():
    print("Genesis is running")

# Stop Genesis
runtime.stop()
```

---

## See Also

- [README.md](../README.md) - Project overview
- [OPERATIONS.md](OPERATIONS.md) - Operations manual
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
