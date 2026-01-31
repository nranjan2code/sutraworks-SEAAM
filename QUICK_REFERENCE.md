# SEAA Quick Reference Card

## 🚀 Quick Start (One-Liner)

```bash
./manage.sh start
```

That's it! Everything launches:
- ✅ SEAA Core System
- ✅ Event Bus & Evolution
- ✅ REST API (port 8000)
- ✅ WebSocket (real-time events)
- ✅ Frontend (if built)

---

## 📋 Essential Commands

### System Control
```bash
./manage.sh start          # Start system
./manage.sh stop           # Stop gracefully
./manage.sh restart        # Restart
./manage.sh status         # Check status & ports
```

### Monitoring
```bash
./manage.sh health         # Detailed health report
./manage.sh watch          # Live event stream
./manage.sh logs -f        # Follow logs
./manage.sh organs         # List all organs
```

### API Testing
```bash
curl http://localhost:8000/api/status     # Check API
curl http://localhost:8000/api/organs     # Organs list
curl http://localhost:8000/api/identity   # Instance info
curl http://localhost:8000/api/goals      # Goals progress
```

---

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
api:
  port: 8000              # API port

llm:
  timeout_seconds: 30     # LLM timeout (prevents hanging)
```

Custom port:
```bash
SEAA_PORT=8001 ./manage.sh start
```

---

## 🔧 Common Tasks

### Check Everything is Working
```bash
./manage.sh status && ./manage.sh health
```

### Reset System (Keeps Identity)
```bash
./manage.sh reset
```

### View Failures & Recovery
```bash
./manage.sh failures
```

### Interactive REPL Mode
```bash
./manage.sh interactive
```

### Test All API Endpoints
```bash
./manage.sh api-test
```

### Check Ollama
```bash
./manage.sh ollama-check
```

---

## 📊 System Health

**Healthy System Shows:**
```
Status:   HEALTHY ✓
Organs:   13/13 healthy
Evolution: 40+ cycles
Failures:  All recovered
```

**Check with:**
```bash
./manage.sh health
```

---

## 🐛 Troubleshooting

### System Won't Stop
```bash
pkill -f "python3 main.py"
rm .seaa.pid
./manage.sh start
```

### API Not Responding
```bash
./manage.sh status              # Check port
./manage.sh logs -f             # View logs
./manage.sh restart             # Restart system
```

### Port Already in Use
```bash
./manage.sh ports               # See what's using it
SEAA_PORT=8001 ./manage.sh start  # Use different port
```

### More Help
```bash
See docs/guides/TROUBLESHOOTING.md
```

---

## 📚 Documentation

| Need | Read |
|------|------|
| **Installation** | `./install.sh` + `docs/guides/INSTALL.md` |
| **System Management** | `MANAGEMENT.md` |
| **Web API & Launch** | `WEB_API_LAUNCH.md` |
| **Troubleshooting** | `docs/guides/TROUBLESHOOTING.md` |
| **Architecture** | `docs/architecture/` |
| **Quick Start** | `docs/guides/QUICK_START.md` |

---

## 🎯 Common Workflows

### Development
```bash
# Terminal 1: Start system
./manage.sh start

# Terminal 2: Watch events
./manage.sh watch

# Terminal 3: Follow logs
./manage.sh logs -f

# Check API in Terminal 4
curl http://localhost:8000/api/status | jq .
```

### Production
```bash
# Start once
./manage.sh start

# Monitor occasionally
./manage.sh health

# Stop when needed
./manage.sh stop
```

### Debugging
```bash
./manage.sh logs -f         # See everything
./manage.sh health          # System status
./manage.sh failures        # What went wrong
./manage.sh ports           # Port conflicts
./manage.sh ollama-check    # Ollama status
```

---

## 📞 Getting Help

1. **Quick Question?**
   ```bash
   ./manage.sh help
   ```

2. **API Issues?**
   ```bash
   ./manage.sh api-test
   ```

3. **System Down?**
   ```bash
   ./manage.sh status && ./manage.sh health
   ```

4. **Stuck?**
   ```bash
   See TROUBLESHOOTING.md
   ```

---

## 🔑 Key Facts

- ✅ One command starts everything
- ✅ API runs on port 8000
- ✅ WebSocket for real-time events
- ✅ Web interface (if frontend built)
- ✅ Graceful shutdown support
- ✅ Instance identity persists
- ✅ Circuit breaker prevents cascades
- ✅ All documented and production-ready

---

## 📦 File Locations

| File | Purpose |
|------|---------|
| `manage.sh` | System management |
| `MANAGEMENT.md` | Management guide |
| `WEB_API_LAUNCH.md` | API documentation |
| `config.yaml` | System configuration |
| `dna.json` | System state |
| `.identity.json` | Instance identity |
| `seaa.log` | System logs |

---

**Everything you need to start and manage SEAA!**

For details, see `MANAGEMENT.md` and `WEB_API_LAUNCH.md`

Last Updated: January 31, 2026
