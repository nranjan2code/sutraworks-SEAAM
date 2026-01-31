# SEAA Implementation Roadmap

**Goal**: Move from minimal viable system to fully autonomous, self-evolving platform

**Timeline**: 4 weeks to MVP+ (all initial goals satisfied + learning enabled)

---

## Week 1: Core Infrastructure 🔧

### Goal: Get 3 organs running + Frontend online

#### Day 1-2: soma.memory.journal
**What**: Event persistence
**Why**: Goal #2 requires memory
**How**:
- LLM generates journal organ
- Listens to all events on bus
- Appends to JSON file (or SQLite later)
- Provides query interface

**Success**:
```bash
python3 main.py goals
# Output should show: ✓ I must have a memory (satisfied)
```

**Metrics**:
- Events logged per cycle: 50+
- Journal size after 24h: 10KB+
- Query latency: <100ms

---

#### Day 3-4: soma.interface.web_api
**What**: REST API + WebSocket endpoint
**Why**: Frontend depends on it, enables remote monitoring
**How**:
- FastAPI application
- GET /api/* endpoints
- WS /ws/events stream
- Serve frontend/dist/

**Success**:
```bash
curl http://localhost:8000/api/status | jq .identity.name
# Output: "Robinson"
```

**Endpoints**:
- `GET /api/status` ← Returns full status
- `GET /api/identity` ← Instance info
- `GET /api/organs` ← Active organs
- `GET /api/goals` ← Goal progress
- `WS /ws/events` ← Event stream

---

#### Day 5-7: Frontend Integration
**What**: Connect React dashboard to API
**Why**: Visual monitoring + control
**How**:
- Build frontend: `npm run build`
- Copy dist/ to API static folder
- Test all dashboard features

**Success**:
```bash
open http://localhost:8000
# See Robinson dashboard with live updates
```

**Dashboard Shows**:
- System status (healthy/degraded)
- Organ list with health
- Goal satisfaction progress
- Real-time event stream
- Identity info

---

### Week 1 Deliverables

```
seaa/                          (unchanged - kernel stable)
soma/
├── perception/
│   └── file_system_observer/  (✓ active)
├── memory/
│   └── journal/               (✓ NEW - WEEK 1)
└── interface/
    └── web_api/               (✓ NEW - WEEK 1)

frontend/                      (✓ NEW - deployed)
├── dist/                      (served by web_api)
└── package.json

config.yaml
├── new: api section
└── new: database section
```

**Goals Satisfied After Week 1**: 2/3 ✓
- ✓ Perceive filesystem (perception.observer)
- ✓ Have memory (memory.journal)
- ⏳ Be observable (interface.web_api partially, needs more monitoring)

---

## Week 2: Observability & Monitoring 📊

### Goal: Collect metrics, add health monitoring, improve visualization

#### Day 1-2: soma.storage.sqlite
**What**: Durable event + metric storage
**Why**: Journal needs backing store, enables analytics
**How**:
- SQLite database
- Tables: events, metrics, audit
- Subscribe to all events
- Store metrics when organs stop

**Success**:
```bash
sqlite3 data/seaa.db "SELECT COUNT(*) FROM events WHERE type='file.created';"
# Output: 42
```

---

#### Day 3-4: soma.extensions.metrics
**What**: Performance collector
**Why**: Identify bottlenecks, predict failures
**How**:
- Track per-organ metrics
- Execution time, memory, error rate
- Publish metric.updated events
- Store to SQLite

**Metrics Tracked**:
- Duration (min/max/avg)
- Memory (peak/average)
- Execution count
- Error count
- Success rate

---

#### Day 5-7: Enhanced Dashboard
**What**: Add metrics visualization
**Why**: Observability is key to autonomy
**How**:
- Add charts to React dashboard
- Show organ performance trends
- Add alerts for degradation

**Dashboard New Features**:
- Organ performance graphs
- Event rate graph
- Memory usage over time
- Error rate trend

---

### Week 2 Deliverables

```
soma/
├── perception/file_system_observer/  (✓ active)
├── memory/journal/                    (✓ active)
├── interface/web_api/                 (✓ active)
├── storage/
│   └── sqlite/                        (✓ NEW - WEEK 2)
└── extensions/
    └── metrics/                       (✓ NEW - WEEK 2)
```

**Goals Satisfied After Week 2**: 2.5/3 ✓
- ✓ Perceive filesystem
- ✓ Have memory (enhanced with metrics)
- ⏳ Be observable (now fully implemented)

---

## Week 3: Learning & Optimization 🧠

### Goal: Enable system to learn and improve itself

#### Day 1-2: Enhanced DNA Schema
**What**: Add learnings to DNA
**Why**: System needs to remember what works
**How**:
- Add `metrics` section to DNA
- Add `learnings` section to DNA
- Track successful patterns

**New DNA Fields**:
```json
{
  "metrics": {
    "soma.perception.observer": {
      "success_count": 150,
      "avg_duration_ms": 45,
      "error_count": 0
    }
  },
  "learnings": {
    "successful_patterns": [
      "event_bus_subscription",
      "graceful_error_handling"
    ],
    "preferred_libraries": {
      "watchdog": 0.95,
      "fastapi": 0.92
    }
  }
}
```

---

#### Day 3-4: soma.extensions.health_monitor
**What**: Proactive health checking
**Why**: Catch problems before they fail
**How**:
- Monitor each organ's metrics
- Detect degradation trends
- Alert before failure
- Suggest restarts

**Checks**:
- Is organ still responding?
- Has memory usage spiked?
- Has error rate increased?
- Is performance degrading?

---

#### Day 5-7: soma.cortex.goal_optimizer
**What**: Dynamically adjust goals
**Why**: Enable goal evolution
**How**:
- Analyze goal progress
- Suggest new subgoals
- Update DNA with learned insights
- Propose goal refinements

**Examples**:
- Goal: "Be observable" → Add subgoal: "Report metrics"
- Goal: "Perceive filesystem" → Add subgoal: "Detect patterns"

---

### Week 3 Deliverables

```
soma/
├── perception/file_system_observer/  (✓ active)
├── memory/journal/                    (✓ active)
├── interface/web_api/                 (✓ active)
├── storage/sqlite/                    (✓ active)
├── extensions/
│   ├── metrics/                       (✓ active)
│   └── health_monitor/                (✓ NEW - WEEK 3)
└── cortex/
    └── goal_optimizer/                (✓ NEW - WEEK 3)
```

**Goals Satisfied After Week 3**: 2.5/3 ✓
- ✓ Perceive filesystem
- ✓ Have memory (with analytics)
- ✓ Be observable (comprehensive)

**BUT**: System now has 7 organs + can optimize its own goals!

---

## Week 4: Autonomy & Scaling 🚀

### Goal: Enable fleet operations and self-repair

#### Day 1-2: soma.cortex.learning
**What**: Extract and apply learnings
**Why**: System improves over time
**How**:
- Analyze successful organ designs
- Identify patterns that work
- Refine architect prompts
- Predict success likelihood

**Learned Patterns**:
- Which libraries lead to success
- Which architectures scale
- Which event patterns work
- Common pitfalls to avoid

---

#### Day 3-4: Enhanced Auto-Recovery
**What**: Intelligent error handling
**Why**: Reduce manual intervention
**How**:
- Analyze failure root causes
- Attempt smart fixes
- Reset with fresh code if needed
- Learn from each fix

**Recovery Strategies**:
- Restart with same code
- Restart with code adjustments
- Request redesign from architect
- Disable if unrecoverable

---

#### Day 5-7: soma.mesh.discovery (Optional)
**What**: Multi-instance coordination
**Why**: Enable fleet operations
**How**:
- Broadcast instance status
- Discover other instances
- Share organ designs
- Coordinate goal achievement

**Mesh Features**:
- Registry of instances
- Design sharing (gist/git)
- Fleet-wide metrics
- Distributed goal tracking

---

### Week 4 Deliverables

```
soma/
├── perception/file_system_observer/  (✓ active)
├── memory/journal/                    (✓ active)
├── interface/web_api/                 (✓ active)
├── storage/sqlite/                    (✓ active)
├── extensions/
│   ├── metrics/                       (✓ active)
│   └── health_monitor/                (✓ active)
├── cortex/
│   ├── goal_optimizer/                (✓ active)
│   └── learning/                      (✓ NEW - WEEK 4)
└── mesh/
    └── discovery/                     (✓ NEW - WEEK 4 if time)
```

**Final State**:
- ✓ All initial goals satisfied
- ✓ System learning and improving
- ✓ Multiple organs collaborating
- ✓ Ready for autonomous operation
- ⏳ Fleet coordination (optional)

---

## Parallel Track: Kernel Enhancements

### Throughout All Weeks

#### Add Config Sections (Day 1)
```yaml
# seaa/core/config.py
api:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["http://localhost:3000"]

database:
  engine: "sqlite"
  url: "data/seaa.db"

metrics:
  enabled: true
  retention_days: 30
```

#### Enhanced Prompts (Day 2-3)
```
seaa/cortex/prompts/
├── agent_factory.yaml        (memory organs)
├── storage_factory.yaml       (database organs)
├── interface_factory.yaml     (API organs)
└── health_factory.yaml        (monitoring organs)
```

#### New CLI Commands (Throughout)
- `python3 main.py config` - View config
- `python3 main.py metrics` - Show metrics
- `python3 main.py health` - Health check
- `python3 main.py organ restart <name>` - Force restart
- `python3 main.py gene edit` - Edit goals

---

## Success Criteria

### By End of Week 1
- [ ] Frontend dashboard live on http://localhost:8000
- [ ] 3 organs active (perception, journal, web_api)
- [ ] Goals #1 & #2 satisfied
- [ ] Real-time event streaming works

### By End of Week 2
- [ ] SQLite persistent storage active
- [ ] Metrics collected for all organs
- [ ] Dashboard shows performance graphs
- [ ] 5 organs total

### By End of Week 3
- [ ] Health monitoring catching issues
- [ ] Goal optimizer proposing improvements
- [ ] Learning system analyzing patterns
- [ ] System learning from experience

### By End of Week 4
- [ ] Learning improves architect prompts
- [ ] Auto-recovery fixes most failures
- [ ] Fleet coordination operational (optional)
- [ ] All 3 goals satisfied
- [ ] 7-10 organs running harmoniously

---

## Testing Strategy

### Unit Tests (Existing)
- Continue running existing 13 tests
- Add tests for new organs

### Integration Tests
- Test API endpoints
- Test WebSocket streaming
- Test organ lifecycle

### System Tests
- Run 24-hour autonomous loop
- Verify no memory leaks
- Verify error recovery
- Check goal satisfaction

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] No security warnings
- [ ] Documentation updated
- [ ] Frontend builds successfully
- [ ] API endpoints responding

### Deployment
- [ ] Config file created
- [ ] Database initialized
- [ ] Frontend deployed to dist/
- [ ] API running on port 8000
- [ ] Genesis running in background

### Post-Deployment
- [ ] Dashboard accessible
- [ ] Events streaming live
- [ ] Journal recording events
- [ ] Metrics being collected

---

## Risk Mitigation

### Risk: New organs failing
**Mitigation**:
- Circuit breaker limits to 3 attempts
- Immunity system auto-disables
- Manual override via CLI

### Risk: API timeout
**Mitigation**:
- Set timeouts in FastAPI
- Implement request queuing
- Add retry logic in frontend

### Risk: Database corruption
**Mitigation**:
- SQLite is atomic
- Regular backups
- Schema migrations

### Risk: Learning makes bad recommendations
**Mitigation**:
- Keep comprehensive logs
- Allow prompt override
- Manual gene editing

---

## Next Immediate Action

**START: Create soma.memory.journal**

This organ will:
1. Satisfy Goal #2
2. Demonstrate self-evolution at scale
3. Provide data for all future analytics
4. Be the foundation for SQLite integration

```bash
# DNA will auto-evolve this on next cycle
# But we can seed it by updating DNA first:

python3 -c "
from seaa.dna.repository import DNARepository
from pathlib import Path
repo = DNARepository(Path('dna.json'))
dna = repo.load()
# Journal is already in blueprint - just let it evolve naturally
"

# Or manually trigger evolution:
python3 main.py  # Run system for 2 minutes
# Watch it evolve soma.memory.journal
```

---

## Summary

**Week 1**: Infrastructure (perception → journal → API → frontend)
**Week 2**: Observability (storage → metrics → monitoring)
**Week 3**: Learning (health monitor → goal optimizer)
**Week 4**: Autonomy (learning → auto-recovery → (mesh))

**Outcome**: Fully observable, self-learning, autonomous system

**Confidence**: HIGH - The kernel is solid, soma organs follow clear patterns
