# SEAA Troubleshooting Guide

## System Stuck on Shutdown

### Symptoms
- System doesn't respond to Ctrl+C
- "Received signal 2, initiating graceful shutdown..." message repeating
- Ollama timeout error in logs (e.g., "Ollama timeout (120s)")
- Process is hung and won't exit cleanly

### Root Cause
The system is waiting for an LLM response during evolution. If Ollama is slow or unresponsive, the LLM timeout (previously 120 seconds) will block shutdown.

### Immediate Fix
If the system is stuck right now, force kill it:

```bash
# Kill the process
pkill -f "python3 main.py"

# Verify it's gone
ps aux | grep "python3 main.py" | grep -v grep
```

### Permanent Solution
The LLM timeout has been reduced from **120 seconds to 30 seconds** in `config.yaml`. This allows failed requests to fail fast and enables graceful shutdown without hanging.

**What changed:**
```yaml
# Before
llm:
  timeout_seconds: 120

# After
llm:
  timeout_seconds: 30
```

**Why this works:**
- Organs retry up to 3 times before circuit opening
- Total worst-case timeout: 30s × 3 attempts = 90s (down from 360s)
- Failed organs won't block shutdown
- Circuit breaker activates faster

### Prevention
Ensure Ollama is responsive:

```bash
# Check Ollama is running
lsof -i :11434

# Verify Ollama responds
curl -s http://localhost:11434/api/tags | jq .
```

### Optional: Further Reduce Timeout
If you experience timeouts even at 30 seconds, reduce further:

```yaml
llm:
  timeout_seconds: 15  # Faster failure, quicker shutdown
```

**Tradeoff:** Lower timeout = faster shutdown but code generation may fail more often for complex organs.

---

## Ollama Not Running

### Symptoms
- Error: "Connection refused" or "Cannot reach localhost:11434"
- LLM requests timing out

### Fix
Start Ollama:

```bash
ollama serve
```

Verify it's running:

```bash
lsof -i :11434
# Should show: ollama with LISTEN status
```

### Pull Model
If you get "model not found" error:

```bash
ollama pull qwen2.5-coder:14b
```

---

## High CPU/Memory Usage

### Symptoms
- System running but CPU or memory very high
- Organs not evolving
- Slow response times

### Diagnosis
Check what organs are running:

```bash
python3 main.py organs
```

Check system resources:

```bash
# macOS
top -l 1 | grep -E "^CPU|^Mem"

# Linux
top -bn1 | head -20
```

### Fix
Reduce concurrent organs in `config.yaml`:

```yaml
metabolism:
  max_concurrent_organs: 5    # Was 20
  cycle_interval_seconds: 60   # Was 30
```

This slows evolution but reduces resource usage.

---

## DNA Corruption

### Symptoms
- "DNA integrity check failed" error
- System won't start
- SHA-256 hash mismatch

### Fix - Soft Reset (Preserves Identity)
Resets to initial state but keeps instance identity:

```bash
python3 main.py --reset
```

This:
- ✓ Preserves `.identity.json` (instance remembers itself)
- ✗ Wipes `dna.json` (system state reset)
- ✓ Keeps all core organs intact

### Fix - Hard Reset (Full Clean State)
Delete DNA files manually:

```bash
rm dna.json dna.sha256 .dna_backups/*
python3 main.py  # Starts from scratch
```

This fully resets the system. **Identity is preserved** (in `.identity.json`).

---

## Organ Failures

### Symptoms
- Organ marked as "FAILED" in status
- Repeated errors in logs for same organ
- Circuit breaker activated (organ disabled for 30 min)

### Check Failure Details

```bash
# See failure history
python3 main.py failures

# Or check via API
curl http://localhost:8000/api/failures | jq .
```

### Common Causes

**1. Import Error (Missing Dependency)**
```
Error: Cannot import X
Fix: pip install X
```

**2. Validation Error (Bad Code Generation)**
```
Error: SyntaxError in generated code
Fix: Check LLM output quality, may need to:
  - Lower temperature in config.yaml (was 0.1, good)
  - Reduce max_tokens if set
  - Restart Ollama
```

**3. Runtime Error (Logic Bug)**
```
Error: AttributeError: module 'X' has no attribute 'Y'
Fix: Check organ implementation, may be incompatible
```

**4. Circuit Breaker (3 Failures in a Row)**
```
Status: CIRCUIT_OPEN
Duration: 30 minutes (configurable)
Fix: Wait 30 minutes or restart system
```

### View Organ Logs

```bash
# Real-time event stream
python3 main.py watch

# Filter for specific organ
python3 main.py watch | grep "soma.learning"

# Via API websocket
# ws://localhost:8000/ws/events
```

---

## LLM Connection Issues

### Symptoms
- "Cannot reach Ollama" or timeout errors
- Code generation fails
- "Connection refused" errors

### Verify Ollama
```bash
# Check Ollama process
lsof -i :11434

# Test direct call
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2.5-coder:14b",
    "prompt": "def hello(): return",
    "stream": false
  }' | jq .
```

### Switch LLM Provider
If Ollama is problematic, use Google Gemini:

```bash
# 1. Get API key from https://ai.google.dev
export GOOGLE_API_KEY=your_key_here

# 2. Update config.yaml
# llm:
#   provider: gemini
#   model: gemini-1.5-flash
```

### Increase Timeout Temporarily
For slower systems:

```yaml
llm:
  timeout_seconds: 60  # Increased from 30
```

---

## Port Already in Use

### Symptoms
- Error: "Address already in use" on port 8000
- API won't start

### Find What's Using the Port
```bash
lsof -i :8000
```

### Kill It
```bash
# Safe: Kill SEAA if multiple instances
pkill -f "python3 main.py"

# Or specify PID
kill -9 <PID>
```

### Use Different Port
Edit `config.yaml`:

```yaml
api:
  port: 8001  # Changed from 8000
```

---

## Installation Issues

### Python Version Error
```
Error: Python 3.9+ required
Fix:
  python3 --version
  brew install python@3.11  # macOS
  apt-get install python3.11  # Linux
```

### Virtual Environment Issues
```bash
# Fresh install
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Dependencies Missing
```bash
# Reinstall all
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## Getting Help

1. **Check this guide first** - Most issues covered above
2. **Check logs** - `python3 main.py watch` shows real-time events
3. **Check API status** - `curl http://localhost:8000/api/status`
4. **View failures** - `python3 main.py failures`
5. **Report issue** - [GitHub Issues](https://github.com/nranjan2code/sutraworks-SEAAM/issues)

---

## Key Commands Reference

```bash
# System status
python3 main.py status           # Health overview
python3 main.py organs           # Organ list
python3 main.py identity         # Instance info
python3 main.py goals            # Goal progress
python3 main.py failures         # Failure history
python3 main.py watch            # Live event stream

# System control
python3 main.py --reset          # Soft reset (keeps identity)
pkill -f "python3 main.py"       # Force shutdown

# API endpoints
curl http://localhost:8000/api/status      # System status
curl http://localhost:8000/api/organs      # Organs list
curl http://localhost:8000/api/identity    # Instance identity
curl http://localhost:8000/api/goals       # Goals progress
curl http://localhost:8000/api/failures    # Failures
curl http://localhost:8000/api/timeline    # Evolution timeline

# Debugging
python3 main.py -i               # Interactive REPL mode
python3 main.py watch            # Stream events
tail -f events.log               # View event journal
```

---

**Last Updated:** January 31, 2026
**Status:** Production Ready ✅
