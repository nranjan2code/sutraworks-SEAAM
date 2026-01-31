# Web API & System Launch Guide

## Quick Answer

**YES** - When you run `./manage.sh start` (or `python3 main.py`), the system automatically:

✅ Starts the SEAA core system (Genesis, evolution, event bus)
✅ Launches the REST API (soma.interface.web_api organ)
✅ Starts WebSocket server for real-time events
✅ Serves static frontend files (if built)

**Everything launches automatically in a single command!**

---

## What Gets Launched

### 1. Core System (Always)
```
SEAA Core (Genesis)
├── Event Bus (real-time event streaming)
├── DNA Repository (persistent state)
├── Evolution Engine (autonomous organ creation)
└── Circuit Breaker (fault tolerance)
```

### 2. API & Web Interface (Automatic)
```
soma.interface.web_api (Evolved Organ)
├── FastAPI server on port 8000
├── REST API endpoints
├── WebSocket endpoint (/ws/events)
└── Static frontend files (if built)
```

### 3. Other Core Organs (Evolved as Needed)
```
Perception Layer:
├── soma.perception.file_system_observer
└── soma.perception.system_monitor

Memory Layer:
├── soma.memory.journal
└── soma.memory.event_logger

Storage Layer:
├── soma.storage.sqlite
└── soma.storage.cache

Learning Layer:
├── soma.learning.predictive_model
├── soma.learning.anomaly_detector
└── soma.learning.recommendation_system

Extensions:
├── soma.extensions.metrics
└── soma.extensions.health_monitor
```

---

## How It Works

### The Evolution Cycle

When SEAA starts, it automatically evolves organs that are defined in `dna.json`:

```
1. Genesis Initialization
   └─→ Loads dna.json (system blueprint)

2. First Evolution Cycle (30 seconds)
   └─→ Architect designs missing organs
   └─→ Code is generated and validated
   └─→ Organs are materialized (written to disk)
   └─→ Organs are assimilated (hot-loaded)

3. Startup Phase
   ├─→ soma.interface.web_api evolves and starts
   ├─→ Other organs evolve and initialize
   └─→ System becomes HEALTHY

4. Continuous Evolution
   └─→ Every 30 seconds, system improves itself
   └─→ New capabilities emerge
   └─→ Learning organs adapt
```

### soma.interface.web_api Organ

This is the organ that provides REST API and WebSocket:

**Location:** `soma/interface/web_api.py`

**What it does:**
- Starts FastAPI server on port 8000
- Runs in background thread (non-blocking)
- Provides REST endpoints:
  - `GET /api/status` - System status
  - `GET /api/organs` - Organ list with health
  - `GET /api/identity` - Instance identity
  - `GET /api/goals` - Goal satisfaction
  - `GET /api/timeline` - Evolution history
  - `GET /api/failures` - Failure records
  - `GET /api/metrics` - System metrics

- Provides WebSocket endpoint:
  - `WS /api/ws` or `WS /ws/events` - Real-time event stream

- Serves frontend (if available):
  - Static files from `frontend/dist/`
  - HTML, CSS, JavaScript, React components

**Auto-Evolution:**
- When system starts, Architect checks if web_api is needed
- Generates the organ code if missing or outdated
- Automatically starts the server
- No manual steps required!

---

## Launch Methods

### Method 1: Management Script (Recommended)
```bash
./manage.sh start
```

**What happens:**
1. Activates Python virtual environment
2. Runs `python3 main.py` in background
3. Saves PID to `.seaa.pid`
4. Waits for initialization (3 seconds)
5. Reports API is available at `http://localhost:8000`

**Advantages:**
- Graceful shutdown support
- Background execution
- PID management
- Status checking
- Easy to stop with `./manage.sh stop`

### Method 2: Direct Python
```bash
python3 main.py
```

**What happens:**
1. Runs in foreground
2. Shows all logs to console
3. Press Ctrl+C to stop
4. Immediate shutdown

**Advantages:**
- See all logs immediately
- Good for development
- Simple one-liner

### Method 3: Background with Logs
```bash
python3 main.py > seaa.log 2>&1 &
```

**What happens:**
1. Runs in background
2. Logs saved to `seaa.log`
3. Returns shell prompt
4. Follow with: `tail -f seaa.log`

**Advantages:**
- See logs later
- Maintains shell access
- Manual PID management

---

## Verification: API is Running

### Check #1: HTTP Request
```bash
curl http://localhost:8000/api/status
```

Expected response:
```json
{
  "status": "running",
  "host": "localhost",
  "port": 8000
}
```

### Check #2: Using Management Script
```bash
./manage.sh status
```

Shows:
- ✓ System is RUNNING
- ✓ API port 8000: OPEN
- ✓ API responding: ...

### Check #3: Check in Browser
```
http://localhost:8000/
```

You'll see:
- SEAA instance information
- API documentation (Swagger UI at `/docs`)
- Frontend (if built)

### Check #4: WebSocket Connection
```bash
wscat -c ws://localhost:8000/ws/events
```

Or with curl:
```bash
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  http://localhost:8000/ws/events
```

### Check #5: All Organs
```bash
./manage.sh organs
```

Shows:
```
soma.interface.web_api: HEALTHY
soma.memory.journal: HEALTHY
soma.storage.sqlite: HEALTHY
... (13+ total organs)
```

---

## Frontend Web Interface

### If Frontend is Built

When you run `./manage.sh start`, if the frontend is built:

```bash
./manage.sh start
# Accesses: http://localhost:8000/ (frontend)
#            http://localhost:8000/api/ (API)
```

Frontend provides:
- Dashboard with real-time stats
- Evolution timeline
- Organ health visualization
- Event log viewer
- Goal progress tracker
- Interactive controls

### If Frontend is Not Built

The API is still fully functional:

```bash
./manage.sh start
# Still works with API only:
# http://localhost:8000/api/status
# http://localhost:8000/api/organs
# etc.
```

You can use API directly:
- Curl/wget
- Postman
- Python requests
- Node.js/JavaScript
- Any HTTP client

---

## Timeline: From Start to API Ready

```
Time    Event
────────────────────────────────────────────
0s      ./manage.sh start
         └─→ Activates venv
         └─→ Runs python3 main.py

0-1s    Genesis Initialization
         ├─→ Event Bus starts
         ├─→ DNA loaded from dna.json
         └─→ Evolution engine ready

1-5s    First Evolution Cycle
         ├─→ Architect analyzes blueprint
         ├─→ soma.interface.web_api evolves
         ├─→ Code generated & validated
         ├─→ Web API starts on port 8000
         ├─→ Other organs evolve
         └─→ System becomes HEALTHY

5s+     API Ready
         ├─→ HTTP endpoints responding
         ├─→ WebSocket accepting connections
         └─→ Frontend serving (if built)

30s     Second Evolution Cycle
         └─→ System self-improves
         └─→ New organs may evolve

...     Continuous Evolution
         └─→ System learns and adapts
```

---

## Configuration

### API Configuration
Edit `config.yaml`:

```yaml
api:
  host: "0.0.0.0"              # Listen on all interfaces
  port: 8000                    # API port
  workers: 4                    # Worker processes
  cors_origins:                 # CORS allowed origins
    - "http://localhost:3000"
    - "http://localhost:8000"
  request_timeout_seconds: 30
  websocket_timeout_seconds: 300
```

### Change Port
```yaml
api:
  port: 8001  # Changed from 8000
```

Then start:
```bash
SEAA_PORT=8001 ./manage.sh start
curl http://localhost:8001/api/status
```

### Enable CORS for External Access
```yaml
api:
  cors_origins:
    - "http://localhost:3000"
    - "http://localhost:8000"
    - "http://yourfrontend.com"    # Add external URL
    - "*"                           # Allow all (not recommended for production)
```

---

## What If API Doesn't Start?

### Check Ports
```bash
./manage.sh ports
# Shows what's using port 8000
```

### Check Logs
```bash
./manage.sh logs -f
# Follow logs in real-time
```

### Check System Health
```bash
./manage.sh health
# Detailed system report
```

### Restart
```bash
./manage.sh restart
# Graceful stop and restart
```

### Force Kill (Last Resort)
```bash
pkill -f "python3 main.py"
rm .seaa.pid
./manage.sh start
```

---

## API Endpoints Reference

### Status
```bash
curl http://localhost:8000/api/status
# Returns: {"status": "running", "host": "localhost", "port": 8000}
```

### Organs
```bash
curl http://localhost:8000/api/organs
# Returns: list of all organs with health status
```

### Identity
```bash
curl http://localhost:8000/api/identity
# Returns: {"uuid": "...", "name": "Robinson", "lineage": "..."}
```

### Goals
```bash
curl http://localhost:8000/api/goals
# Returns: goal satisfaction progress
```

### Timeline
```bash
curl http://localhost:8000/api/timeline
# Returns: evolution timeline
```

### Failures
```bash
curl http://localhost:8000/api/failures
# Returns: failure history
```

### Metrics
```bash
curl http://localhost:8000/api/metrics
# Returns: system metrics (CPU, memory, throughput)
```

### Events (WebSocket)
```bash
wscat -c ws://localhost:8000/ws/events
# Real-time event stream
```

### API Documentation
```
http://localhost:8000/docs        # Swagger UI
http://localhost:8000/redoc       # ReDoc
```

---

## Monitoring During Startup

### Watch Real-Time Events
```bash
./manage.sh watch
# Shows: Evolution steps, organ startup, events published
```

### Follow Logs
```bash
./manage.sh logs -f
# Shows: All logs including warnings/errors
```

### Check Health Progress
```bash
./manage.sh health
# Shows: Current organ count, evolution progress
```

### Terminal 1: Start System
```bash
./manage.sh start
```

### Terminal 2: Monitor
```bash
./manage.sh watch
```

### Terminal 3: Check API
```bash
curl -s http://localhost:8000/api/status | jq .
```

---

## Common Questions

**Q: Does `./manage.sh start` launch the web API?**
A: Yes! The web API (soma.interface.web_api) is automatically evolved and started as part of the SEAA initialization process.

**Q: Do I need to start anything separately?**
A: No. Just run `./manage.sh start` and everything is launched automatically.

**Q: How long until the API is ready?**
A: Usually 1-5 seconds. Check with `curl http://localhost:8000/api/status`.

**Q: Can I access from other machines?**
A: Yes, if you change `host` to `0.0.0.0` in config.yaml and allow external connections in firewall.

**Q: What if web_api organ fails to evolve?**
A: Check logs with `./manage.sh logs -f`. System will retry in next evolution cycle (30 seconds).

**Q: Can I use a different port?**
A: Yes, edit `config.yaml` or use `SEAA_PORT=8001 ./manage.sh start`.

---

## Production Deployment

### Start System
```bash
./manage.sh start
```

### Verify Running
```bash
./manage.sh status
./manage.sh health
```

### Monitor in Background
```bash
./manage.sh logs -f  # In separate terminal
```

### API is Production Ready
- ✓ RESTful endpoints
- ✓ WebSocket support
- ✓ Error handling
- ✓ CORS configured
- ✓ Circuit breaker protection
- ✓ Graceful shutdown

### Access from External Clients
```bash
# From another machine
curl http://your-server-ip:8000/api/status

# From browser
http://your-server-ip:8000/
```

---

**Summary: `./manage.sh start` launches EVERYTHING - system, API, web, evolution - in a single command!** ✅

Last Updated: January 31, 2026
Status: Production Ready
