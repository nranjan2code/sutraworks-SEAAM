# SEAA Management Script

Complete guide to managing the SEAA system using the `manage.sh` script.

## Quick Start

The `manage.sh` script provides a unified interface for all SEAA operations:

```bash
# Start the system
./manage.sh start

# Check status
./manage.sh status

# Stop the system
./manage.sh stop

# Restart
./manage.sh restart
```

## Commands Overview

### Core Operations

**Start System**
```bash
./manage.sh start
```
- Starts SEAA in background
- Saves PID to `.seaa.pid`
- Waits for initialization
- Reports API availability

**Stop System**
```bash
./manage.sh stop
```
- Graceful shutdown (SIGTERM)
- Timeout after 10 seconds
- Force kill (SIGKILL) if necessary
- Cleans up PID file

**Restart System**
```bash
./manage.sh restart
```
- Stops if running
- Waits for cleanup
- Starts fresh instance

**Check Status**
```bash
./manage.sh status
```
- Shows running status
- Port availability
- API health check
- Ollama connection status

### Monitoring

**View Logs**
```bash
./manage.sh logs              # Show last 50 lines
./manage.sh logs -f           # Follow in real-time
./manage.sh logs --follow     # Same as -f
```

**Stream Live Events**
```bash
./manage.sh watch
```
- Real-time event stream
- Shows all system activity
- Filter by organ if needed

**System Health**
```bash
./manage.sh health
```
- Detailed health report
- Organ count and status
- Evolution progress
- Goal satisfaction

**List Organs**
```bash
./manage.sh organs
```
- All organs with status
- Health metrics
- Integration status

**Goal Progress**
```bash
./manage.sh goals
```
- Goal satisfaction status
- Progress metrics
- Priority ranking

**View Failures**
```bash
./manage.sh failures
```
- Failure history
- Circuit breaker status
- Recovery attempts

### Utility Commands

**Check Ollama**
```bash
./manage.sh ollama-check
```
- Verifies Ollama is running
- Lists available models
- Checks connectivity

**Port Status**
```bash
./manage.sh ports
```
- Shows usage for all SEAA ports
- Identifies conflicts
- Process information

**Reset System**
```bash
./manage.sh reset
```
- Soft reset (preserves identity)
- Confirmation prompt
- Wipes DNA, keeps `.identity.json`
- **Note:** Instance will remember itself

**Interactive Mode**
```bash
./manage.sh interactive
```
- Launch REPL shell
- Rich UI with syntax highlighting
- Direct command execution

**Test API**
```bash
./manage.sh api-test
```
- Checks all API endpoints
- Reports connectivity
- Useful for debugging

### Help

**Show Help**
```bash
./manage.sh help
./manage.sh --help
./manage.sh -h
```

**Show Version**
```bash
./manage.sh version
./manage.sh --version
```

## Common Workflows

### Development Setup

```bash
# 1. Install (one time)
./install.sh --dev

# 2. Start system
./manage.sh start

# 3. Watch events
./manage.sh watch

# 4. Check health (in another terminal)
./manage.sh health

# 5. Stop when done
./manage.sh stop
```

### Troubleshooting

```bash
# Check what's using ports
./manage.sh ports

# Verify Ollama is running
./manage.sh ollama-check

# Check system logs
./manage.sh logs -f

# Get full health report
./manage.sh health

# View failures
./manage.sh failures

# Restart if needed
./manage.sh restart
```

### Production Deployment

```bash
# Start system (runs in background)
./manage.sh start

# Check it's running
./manage.sh status

# Monitor periodically
./manage.sh health

# View detailed logs
./manage.sh logs -f

# Stop gracefully
./manage.sh stop
```

### System Reset

```bash
# View current state
./manage.sh health

# Reset (keeps instance identity)
./manage.sh reset

# System restarts from scratch but remembers who it is
# Check identity: curl http://localhost:8000/api/identity
```

## Environment Variables

Control behavior via environment variables:

```bash
# Custom API port (default: 8000)
SEAA_PORT=8001 ./manage.sh start

# Custom Ollama port (default: 11434)
OLLAMA_PORT=11435 ./manage.sh ollama-check

# Custom Python command (default: python3)
PYTHON_CMD=python3.11 ./manage.sh start
```

## Exit Codes

```
0   Success
1   Error (command failed, system issue, etc.)
2   System not running when required
```

Use for scripting:

```bash
./manage.sh status
if [ $? -eq 0 ]; then
    echo "System running"
else
    echo "System not running"
fi
```

## Log Files

The script logs to `seaa.log`:

```bash
# View full log
cat seaa.log

# Follow in real-time
tail -f seaa.log

# Last 100 lines
tail -100 seaa.log

# Search for errors
grep ERROR seaa.log

# Using manage.sh
./manage.sh logs -f
```

## PID Management

System creates `.seaa.pid` file:

```bash
# See stored PID
cat .seaa.pid

# Manual cleanup (if needed)
rm .seaa.pid
```

## Port Management

Default ports:

| Port | Service | Check |
|------|---------|-------|
| 8000 | SEAA API | `./manage.sh ports` |
| 11434 | Ollama | `./manage.sh ollama-check` |
| 3000 | Frontend (optional) | `./manage.sh ports` |

### Using Different Port

Edit `config.yaml`:

```yaml
api:
  port: 8001  # Changed from 8000
```

Then:

```bash
SEAA_PORT=8001 ./manage.sh status
```

## Troubleshooting

### Script Not Executable

```bash
chmod +x manage.sh
```

### Virtual Environment Not Found

```bash
./install.sh
# Then use manage.sh
```

### Port Already in Use

```bash
# Find what's using it
./manage.sh ports

# Use different port
SEAA_PORT=8001 ./manage.sh start
```

### System Won't Stop

```bash
# Force kill (use as last resort)
pkill -9 -f "python3 main.py"

# Clean up
rm .seaa.pid
```

### API Not Responding

```bash
./manage.sh ports         # Check port is open
./manage.sh api-test      # Test endpoints
./manage.sh logs -f       # Check logs
./manage.sh restart       # Restart system
```

## Comparison: manage.sh vs Direct Commands

| Task | manage.sh | Direct |
|------|-----------|--------|
| Start | `./manage.sh start` | `python3 main.py` |
| Stop | `./manage.sh stop` | Ctrl+C or pkill |
| Status | `./manage.sh status` | curl /api/status |
| Logs | `./manage.sh logs -f` | tail -f seaa.log |
| Events | `./manage.sh watch` | python3 main.py watch |
| Health | `./manage.sh health` | python3 main.py status |
| Reset | `./manage.sh reset` | python3 main.py --reset |

**Advantages of manage.sh:**
- ✓ Unified interface
- ✓ Automatic PID management
- ✓ Graceful shutdown
- ✓ Status checking
- ✓ Better logging
- ✓ Color-coded output
- ✓ Error handling

## Getting Help

```bash
# Show help
./manage.sh help

# Check version
./manage.sh version

# For troubleshooting
./manage.sh health
./manage.sh logs -f

# See docs
docs/guides/TROUBLESHOOTING.md
```

## Advanced Usage

### Custom Ports in Script

Edit `manage.sh` to change defaults:

```bash
MAIN_PORT=${SEAA_PORT:-8000}      # Default 8000
OLLAMA_PORT=${OLLAMA_PORT:-11434} # Default 11434
```

### Integration with systemd

For system-wide management on Linux:

```bash
# Create service file
sudo vim /etc/systemd/system/seaa.service

[Unit]
Description=SEAA Self-Evolving Autonomous Agent
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/seaa
ExecStart=/path/to/seaa/manage.sh start
ExecStop=/path/to/seaa/manage.sh stop
Restart=on-failure

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable seaa
sudo systemctl start seaa
sudo systemctl status seaa
```

### Cron Job Monitoring

Check system health periodically:

```bash
# Every 5 minutes, check if running and restart if needed
*/5 * * * * cd /path/to/seaa && ./manage.sh status || ./manage.sh restart
```

---

**Last Updated:** January 31, 2026
**Status:** Production Ready ✅
