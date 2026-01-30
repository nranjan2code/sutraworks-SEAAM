# ⚙️ Operations Manual

Complete guide to operating, configuring, and maintaining the SEAA system.

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.9+ | Runtime |
| Ollama | Latest | Local LLM (default) |
| pip | Latest | Dependency management |

### Installation

```bash
# Clone the repository
git clone https://github.com/sutraworks/seaa.git
cd seaa

# Install in development mode
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

### Running

```bash
# Start Ollama (in a separate terminal)
ollama run qwen2.5-coder:14b

# Start SEAA
python3 main.py
```

---

## Command Line Interface

```bash
python3 main.py [COMMAND] [OPTIONS]
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| *(none)* | Start the agent (default) | `python3 main.py` |
| `status` | Show system health and vitals | `python3 main.py status` |
| `organs` | List organs with health status | `python3 main.py organs` |
| `goals` | Show goal satisfaction progress | `python3 main.py goals` |
| `failures` | Show failure records | `python3 main.py failures` |
| `identity` | Show/set instance identity | `python3 main.py identity` |
| `timeline` | Show evolution timeline | `python3 main.py timeline` |
| `watch` | Stream events in real-time | `python3 main.py watch` |

### Global Options

| Option | Description | Example |
|--------|-------------|---------|
| `--help` | Show help message | `python3 main.py --help` |
| `--reset` | Reset to tabula rasa state | `python3 main.py --reset` |
| `--config CONFIG` | Use custom config file | `python3 main.py --config prod.yaml` |
| `--log-level LEVEL` | Override log level | `python3 main.py --log-level DEBUG` |

### Command-Specific Options

```bash
# status - Show system health
python3 main.py status              # Human-readable output
python3 main.py status --json       # JSON output

# organs - List organs
python3 main.py organs              # Active organs only
python3 main.py organs --all        # Include stopped organs
python3 main.py organs --json       # JSON output

# goals - Show goals
python3 main.py goals               # Human-readable
python3 main.py goals --json        # JSON output

# failures - Show failures
python3 main.py failures            # Human-readable
python3 main.py failures --json     # JSON output

# identity - Show/set identity
python3 main.py identity            # Show current identity
python3 main.py identity --name X   # Set instance name
python3 main.py identity --json     # JSON output

# timeline - Show evolution history
python3 main.py timeline            # Last 20 events
python3 main.py timeline --limit 50 # Last 50 events
python3 main.py timeline --json     # JSON output

# watch - Stream events
python3 main.py watch               # All events
python3 main.py watch --pattern organ.evolved  # Specific events
```

### Example Output

```bash
$ python3 main.py status

Robinson (713d8815)
========================================
Status:      HEALTHY
Uptime:      3600s
DNA:         56271deda1e156e0

Organs:      3/3 healthy
Goals:       2/4 satisfied
Evolutions:  3
Pending:     0

$ python3 main.py organs

Organs:
------------------------------------------------------------
  ● ✓  soma.perception.observer
  ● ✓  soma.memory.journal
  ● !  soma.interface.dashboard
        └─ Connection refused on port 5000...

$ python3 main.py identity

Instance Identity:
----------------------------------------
ID:       713d8815-6867-409c-87a1-a2ae27aa3276
Name:     Robinson
Genesis:  2026-01-30T08:28:34.921116Z
Lineage:  56271deda1e156e0
```

### Reset Behavior

The `--reset` flag performs a **Robinson Crusoe reset**:

1. Deletes all evolved organs (`soma/` directory)
2. Resets DNA to original goals only
3. Clears all failure history
4. System re-evolves from scratch

```bash
# Watch the system rebuild from nothing
python3 main.py --reset
```

---

## 📁 Configuration

SEAA uses a layered configuration system:

```
Priority (highest wins):
1. Environment variables
2. config.yaml
3. Built-in defaults
```

### `config.yaml` Reference

```yaml
# SEAA Configuration File
# All values shown are defaults

# LLM Provider Settings
llm:
  provider: ollama              # 'ollama' or 'gemini'
  model: qwen2.5-coder:14b      # Model to use
  temperature: 0.1              # Lower = more deterministic
  max_retries: 3                # Retry attempts for code generation
  timeout_seconds: 120          # Request timeout
  
  # Ollama-specific
  ollama_url: http://localhost:11434/api/generate
  
  # Gemini-specific
  gemini_model: gemini-1.5-flash

# File Paths
paths:
  root: .                       # Project root
  dna: ./dna.json               # DNA file location
  soma: ./soma                  # Evolved organs directory
  prompts: ./seaa/cortex/prompts  # Prompt templates

# Evolution Settings
metabolism:
  cycle_interval_seconds: 30    # Time between evolution cycles
  max_organs_per_cycle: 3       # Max organs to evolve per cycle
  reflection_timeout_seconds: 60
  max_concurrent_organs: 20     # Max running at once (resource limit)
  max_total_organs: 50          # Max ever created (resource limit)

# Circuit Breaker (prevents infinite retry loops)
circuit_breaker:
  max_attempts: 3               # Failures before circuit opens
  cooldown_minutes: 30          # Wait time before retry allowed

# Evolutionary Memory
genealogy:
  enabled: true                 # Enable local git for soma
  user_name: "SEAA Genesis"    # Git user.name for soma repo
  user_email: "genesis@seaa.internal"

# Security Settings
security:
  allow_pip_install: false      # DISABLED by default
  allowed_pip_packages:         # Packages that CAN be installed
    - watchdog
    - streamlit
    - flask
    - fastapi
    - requests
  protected_prefixes:           # Paths that cannot be modified
    - seaa.
    - seaa/

# Logging Settings
logging:
  level: INFO                   # DEBUG, INFO, WARNING, ERROR
  format: colored               # 'colored' or 'json'
  file: null                    # Optional log file path

# Metadata
version: "1.0.0"
environment: development        # 'development' or 'production'
```

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `SEAA_LOG_LEVEL` | Override log level | `DEBUG` |
| `SEAA_LOG_FORMAT` | Log format | `json` |
| `SEAA_ALLOW_PIP` | Enable pip installs | `true` |
| `SEAA_ENV` | Environment name | `production` |
| `SEAA_WATCH_PATH` | Override observer watch path | `/data/watched` |
| `OLLAMA_URL` | Custom Ollama endpoint | `http://gpu-server:11434/api/generate` |
| `OLLAMA_MODEL` | Override Ollama model | `codellama:34b` |
| `GEMINI_API_KEY` | Enable Gemini fallback | `your-api-key` |

---

## 🧬 Evolutionary Memory (Git)

The system maintains a full history of its evolution in `soma/.git`.

### Viewing History

```bash
cd soma
git log --oneline --graph
```

### Auto-Immune Response (Self-Healing)

SEAA is capable of **autonomous rollback**.

If a newly evolved organ causes a critical failure (e.g., `ImportError`, `SyntaxError`) that prevents assimilation:
1. `Immunity` detects the crash.
2. It triggers a `genealogy.revert_last()`.
3. The system returns to the previous healthy state.
4. The mistake is logged in DNA to avoid repeating it.

### Manual Rollback

You can also manually revert if needed:

```bash
cd soma
git reset --hard HEAD^
```

---

## 🔌 Circuit Breaker

The circuit breaker prevents infinite retry loops when organs repeatedly fail.

### How It Works

1. **Closed State** (normal): Evolution attempts proceed
2. **After max_attempts failures**: Circuit **opens**
3. **Open State**: Evolution skipped with log warning
4. **After cooldown_minutes**: Circuit auto-closes, retry allowed

### Configuration

```yaml
circuit_breaker:
  max_attempts: 3        # Default: 3 failures opens circuit
  cooldown_minutes: 30   # Default: 30 min before retry
```

### Manual Circuit Reset

```python
# Via Python
from seaa.dna import DNA
from seaa.dna.repository import DNARepository

repo = DNARepository("dna.json")
dna = repo.load_or_create()
dna.reset_circuit("soma.failing.module")
repo.save(dna)
```

Or edit `dna.json` directly:
```json
{
  "failures": [
    {
      "module_name": "soma.failing.module",
      "circuit_open": false,        // Set to false
      "circuit_opened_at": null,    // Set to null
      "attempt_count": 0            // Reset to 0
    }
  ]
}
```

---

## 🛑 System Reset (Robinson Crusoe Protocol)

For a complete system reset to watch the system rebuild from scratch:

### Option 1: CLI Flag (Recommended)

```bash
python3 main.py --reset
```

### Option 2: Manual Reset

```bash
# 1. Stop the running process (Ctrl+C)

# 2. Delete the body (evolved organs)
rm -rf soma/

# 3. Reset DNA to tabula rasa
cat > dna.json << 'EOF'
{
  "goals": [
    {"text": "I must be able to perceive the file system.", "created_at": "2026-01-01T00:00:00Z", "achieved": false},
    {"text": "I must have persistent memory.", "created_at": "2026-01-01T00:00:00Z", "achieved": false},
    {"text": "I must have a visual dashboard.", "created_at": "2026-01-01T00:00:00Z", "achieved": false}
  ],
  "blueprint": {},
  "failures": [],
  "active_modules": [],
  "metadata": {
    "system_version": "1.0.0",
    "system_name": "SEAA",
    "created_at": "2026-01-01T00:00:00Z",
    "evolution_count": 0
  }
}
EOF

# 4. Optionally uninstall evolved dependencies (for full test)
pip uninstall watchdog streamlit -y

# 5. Restart
python3 main.py
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=seaa --cov-report=term-missing

# Run specific test file
python3 -m pytest tests/unit/test_bus.py -v

# Run specific test
python3 -m pytest tests/unit/test_bus.py::TestEventBus::test_subscribe_and_publish -v
```

### Test Coverage

| Module | Tests | Description |
|--------|-------|-------------|
| EventBus | 12 | Subscribe, publish, async, unsubscribe, drain |
| DNA Schema | 17 | Serialization, legacy migration, operations |
| Materializer | 16 | Atomic writes, kernel protection, **security (path traversal)** |
| Assimilator | 6 | Module loading, validation, batch |
| Genealogy | 4 | Git init, commit, revert |
| Auto-Immune | 3 | Revert triggers, failure handling |
| **Integration** | **28** | Code validation, circuit breaker, goals, config |
| Observability | 20 | Identity, Beacon, Observer, thread-safety |
| **Total** | **109** | All passing |

### Code Quality

```bash
# Format code
black seaa/ tests/

# Lint code
ruff check seaa/ tests/

# Type checking (if mypy installed)
mypy seaa/
```

---

## 🔒 Security

<div align="center">
  <img src="images/seaa_security_layers.png" alt="Security Layers" width="50%">
</div>

### Default Security Posture

SEAA follows **security-first** principles with defense in depth:

| Protection | Default | Description |
|------------|---------|-------------|
| Path Traversal | **Blocked** | Module names validated with regex pattern |
| Module Validation | **Enabled** | Only `soma.*` with valid identifiers imported |
| Star Imports | **Blocked** | `from X import *` rejected for non-seaa modules |
| Forbidden Imports | **Extended** | Blocks pip, subprocess, ctypes, socket, pickle, etc. |
| Prompt Injection | **Protected** | Error messages sanitized before LLM prompts |
| DNA Integrity | **Verified** | SHA-256 hash detects file tampering |
| Pip Install | **Disabled** | External packages cannot be installed |
| Package Allowlist | Limited | Only approved packages can be installed |
| Kernel Protection | **Enabled** | Cannot write to `seaa/*` |
| Atomic Writes | **Enabled** | Prevents file corruption |

### Enabling Pip Install

> ⚠️ **WARNING**: Only enable if you trust the LLM and understand the risks.

```yaml
# config.yaml
security:
  allow_pip_install: true
  allowed_pip_packages:
    - watchdog
    - streamlit
    - requests
    # Add more as needed
```

Or via environment:

```bash
SEAA_ALLOW_PIP=true python3 main.py
```

### Kernel Protection

The system **cannot** modify files with these prefixes:
- `seaa.` (module names)
- `seaa/` (file paths)

This protection is enforced in the Materializer and cannot be disabled.

---

## 🕵️ Troubleshooting

### Common Issues

#### `[ARCHITECT] Failed to structure thought`

**Symptoms:**
```
ERROR    [ARCHITECT   ] Failed to parse JSON response: ...
```

**Causes:**
- LLM outputting conversational text instead of JSON
- Invalid JSON syntax in response

**Solutions:**
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Try a more capable model: `qwen2.5-coder:14b` or `codellama:34b`
3. Check prompt templates in `seaa/cortex/prompts/`

---

#### `[GATEWAY] Validation FAILED: Missing start() function`

**Symptoms:**
```
WARNING  [GATEWAY     ] Validation FAILED: Missing start() function (attempt 1/3)
```

**Causes:**
- LLM not following the organ contract
- Poor prompt engineering

**Solutions:**
1. Check `seaa/cortex/prompts/agent_factory.yaml` for clear instructions
2. Try a different model
3. Increase `max_retries` in config

---

#### `[ASSIMILATOR] ImportError: No module named 'xyz'`

**Symptoms:**
```
ERROR    [ASSIMILATOR ] Failed to import soma.perception.observer: No module named 'watchdog'
```

**Causes:**
- Missing external dependency
- Pip install disabled (default)

**Solutions:**
1. Enable pip install and add package to allowlist:
   ```yaml
   security:
     allow_pip_install: true
     allowed_pip_packages:
       - watchdog
   ```
2. Or install manually: `pip install watchdog`

---

#### `[ASSIMILATOR] Rejected: Missing global start() function`

**Symptoms:**
```
ERROR    [ASSIMILATOR ] Validation failed for soma.xyz: Missing global start() function
```

**Causes:**
- Generated code doesn't have `start()` function
- Gateway validation somehow passed invalid code

**Solutions:**
1. Check the generated file in `soma/`
2. The Architect will attempt to redesign in the next cycle
3. Check `dna.json` for logged failures

---

#### `[GATEWAY] Forbidden imports/calls detected`

**Symptoms:**
```
WARNING  [GATEWAY     ] Validation FAILED: Forbidden imports/calls detected: pip, subprocess
```

**Causes:**
- LLM generated code using prohibited imports
- Security validation working correctly

**Solutions:**
1. This is expected behavior - the system will retry with feedback
2. If persistent, check prompt templates for clear security instructions
3. The code is being correctly rejected for security

---

#### `Circuit breaker OPEN for module`

**Symptoms:**
```
WARNING  [GENESIS     ] Circuit breaker OPEN for soma.xyz, skipping evolution
```

**Causes:**
- Module failed `max_attempts` times (default: 3)
- Circuit breaker protecting against infinite loops

**Solutions:**
1. Wait for `cooldown_minutes` (default: 30) for auto-reset
2. Manually reset circuit (see Circuit Breaker section)
3. Check `dna.json` failures for root cause
4. Fix the underlying issue before resetting

---

#### `Security: Path traversal detected` or `Invalid module name format`

**Symptoms:**
```
ERROR    [MATERIALIZER] Invalid module name format: 'soma..evil'
ERROR    [MATERIALIZER] Path traversal detected in module name
```

**Causes:**
- LLM generated a malicious or malformed module name
- Attempt to escape the soma/ directory
- Module name contains invalid Python identifiers

**Solutions:**
1. This is security protection working correctly
2. The system will retry with valid module names
3. Check prompt templates for clear module naming instructions
4. Valid format: `soma.<category>.<name>` (e.g., `soma.perception.observer`)

---

#### `DNA file integrity check failed`

**Symptoms:**
```
ERROR    [REPOSITORY  ] SECURITY: DNA integrity check FAILED!
DNACorruptedError: DNA file integrity check failed - possible tampering detected
```

**Causes:**
- `dna.json` was modified outside the system
- File corruption
- Possible tampering

**Solutions:**
1. If you legitimately edited the file, recalculate the hash:
   ```python
   from seaa.dna.repository import DNARepository
   repo = DNARepository("dna.json")
   repo.recalculate_integrity_hash()
   ```
2. Or restore from backup: `cp .dna_backups/dna_YYYYMMDD_HHMMSS.json dna.json`
3. To skip verification (debugging only):
   ```python
   repo = DNARepository("dna.json", verify_integrity=False)
   ```

---

#### `Invalid configuration` at startup

**Symptoms:**
```
ValueError: Invalid configuration:
  - LLM temperature must be 0-2, got 3.0
  - max_total_organs must be >= max_concurrent_organs
```

**Causes:**
- Configuration validation failed
- Invalid values in `config.yaml`

**Solutions:**
1. Check the specific error messages
2. Fix values in `config.yaml`:
   - Temperature: 0.0 to 2.0
   - max_total_organs >= max_concurrent_organs
   - Timeouts >= 10 seconds
3. See Configuration section for valid ranges

---

#### EventBus Not Responding

**Symptoms:**
- Events published but handlers not called
- System appears frozen

**Solutions:**
1. Check if EventBus worker is running:
   ```python
   from seaa.kernel.bus import bus
   print(bus._worker_running)
   ```
2. Restart the system

---

### Debug Mode

For detailed diagnostics:

```bash
# Maximum verbosity
python3 main.py --log-level DEBUG

# JSON logging for parsing
SEAA_LOG_FORMAT=json python3 main.py > seaa.log 2>&1
```

### Log Locations

| Log Type | Location |
|----------|----------|
| Console | stdout/stderr |
| File | Configure in `logging.file` |
| DNA State | `dna.json` |
| Evolved Code | `soma/` directory |

---

## 📊 Monitoring

### Health Indicators

| Indicator | Healthy | Unhealthy |
|-----------|---------|-----------|
| Evolution cycles | Regularly occurring | Stalled |
| Active organs | Growing or stable | Decreasing |
| Failure count | Low, decreasing | High, increasing |
| LLM responses | Valid JSON | Timeouts, errors |

### Checking System State

```bash
# View DNA state
cat dna.json | python3 -m json.tool

# List evolved organs
find soma/ -name "*.py" ! -name "__init__.py"

# Check running processes
ps aux | grep python
```

### DNA Analytics

```python
# Python script to analyze DNA
import json

with open("dna.json") as f:
    dna = json.load(f)

print(f"Goals: {len(dna['goals'])}")
print(f"Blueprints: {len(dna['blueprint'])}")
print(f"Active Modules: {len(dna['active_modules'])}")
print(f"Failures: {len(dna['failures'])}")
print(f"Evolution Count: {dna['metadata'].get('evolution_count', 0)}")
```

---

## 🔄 Backup & Recovery

### Backup DNA

```bash
# Create dated backup
cp dna.json "dna.backup.$(date +%Y%m%d-%H%M%S).json"

# Automatic backups are stored in dna.json.bak
ls -la dna.json*
```

### Backup Evolved Organs

```bash
# Archive soma directory
tar -czf "soma.backup.$(date +%Y%m%d).tar.gz" soma/
```

### Recovery

```bash
# Restore DNA
cp dna.backup.20260130-120000.json dna.json

# Restore soma
tar -xzf soma.backup.20260130.tar.gz
```

---

## 🚦 Production Deployment

### Configuration for Production

```yaml
# config.yaml (production)
llm:
  provider: ollama
  model: codellama:34b
  max_retries: 5

security:
  allow_pip_install: false  # Keep disabled in production

logging:
  level: INFO
  format: json              # Machine-parseable
  file: /var/log/seaa/seaa.log

environment: production
```

### Running as a Service

```bash
# systemd service file (/etc/systemd/system/seaa.service)
[Unit]
Description=SEAA Self-Evolving Agent
After=network.target

[Service]
Type=simple
User=seaa
WorkingDirectory=/opt/seaa
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable seaa
sudo systemctl start seaa
sudo systemctl status seaa
```

---

## 📚 Additional Resources

- [Architecture Deep Dive](ARCHITECTURE.md)
- [Design Specifications](DESIGN.md)
- [GitHub Repository](https://github.com/sutraworks/seaa)
