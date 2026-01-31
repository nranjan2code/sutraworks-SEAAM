# Robinson's Core Birth Organs - Essential Systems

**Purpose**: Define the minimal set of organs Robinson is **born with** - required for autonomous evolution to work.

**Principle**: These are NOT evolved. They are **part of Robinson's DNA at genesis** - the immune system, nervous system, and evolutionary machinery itself.

---

## Core Organ Architecture

```
ROBINSON AT BIRTH (soma/kernel/)
├── soma.kernel.self_monitor        [Core] ← System introspection
├── soma.kernel.error_recovery       [Core] ← Resilience & healing
├── soma.kernel.goal_manager         [Core] ← Purpose & direction
├── soma.kernel.code_validator       [Core] ← Safety gatekeeper
├── soma.kernel.memory_keeper        [Core] ← Persistence & state
└── soma.kernel.event_logger         [Core] ← Audit trail

EVOLVED ORGANS (soma/)
├── soma.perception.*                [Evolved] ← Sensors
├── soma.memory.*                    [Evolved] ← Application storage
├── soma.extensions.*                [Evolved] ← Monitoring/metrics
├── soma.interface.*                 [Evolved] ← External APIs
├── soma.learning.*                  [Evolved] ← Intelligence
└── soma.cortex.*                    [Evolved] ← Decision making
```

---

## 1. soma.kernel.self_monitor

**Purpose**: Robinson knows itself - introspection, awareness, monitoring.

**Responsibility**:
- Track all active organs and their health
- Monitor system vitals (CPU, memory, uptime)
- Detect degradation patterns
- Publish self-awareness events

**Critical for**:
- Genesis knowing what organs are running
- Architect deciding what to evolve next
- Goal satisfaction checking
- Health-based circuit breaker decisions

**Core Functions**:
```python
class SelfMonitor:
    def get_organ_health(organ_name: str) -> Vitals
    def get_system_vitals() -> SystemHealth
    def get_active_organs() -> List[OrganInfo]
    def detect_degradation() -> List[DegradationAlert]
    def publish_health_event(health_data) -> None
```

**Born at**: Genesis initialization
**Always active**: Yes
**Restartable**: No (would break the system)

---

## 2. soma.kernel.error_recovery

**Purpose**: Robinson heals itself - error handling, recovery, resilience.

**Responsibility**:
- Catch organ failures
- Execute recovery procedures
- Update circuit breaker status
- Suggest fixes via immunity system
- Prevent cascade failures

**Critical for**:
- Keeping failed organs from crashing system
- Preventing repeated failures
- Learning from mistakes
- Self-healing without manual intervention

**Core Functions**:
```python
class ErrorRecovery:
    def handle_organ_failure(organ_name: str, error: Exception) -> None
    def execute_recovery_procedure(organ_name: str) -> bool
    def update_circuit_breaker(organ_name: str, state: str) -> None
    def suggest_fix(organ_name: str, error: Exception) -> Suggestion
    def prevent_cascade_failure() -> None
```

**Born at**: Genesis initialization
**Always active**: Yes
**Restartable**: No (would lose failure tracking)

---

## 3. soma.kernel.goal_manager

**Purpose**: Robinson has purpose - maintains goals, checks satisfaction, directs evolution.

**Responsibility**:
- Store and manage system goals
- Check goal satisfaction (pattern matching against active organs)
- Auto-satisfy goals when organs appear
- Publish goal satisfaction events
- Direct Genesis toward unsatisfied goals

**Critical for**:
- Genesis knowing what to evolve
- Architect designing appropriate organs
- Measuring system progress
- Defining autonomy direction

**Core Functions**:
```python
class GoalManager:
    def get_goals() -> List[Goal]
    def check_goal_satisfaction() -> List[GoalStatus]
    def add_goal(description: str, required_organs: List[str]) -> Goal
    def satisfy_goal(goal_id: str) -> bool
    def get_unsatisfied_goals() -> List[Goal]
    def recommend_next_organ() -> Optional[Organ]
```

**Born at**: Genesis initialization (with 3 core goals)
**Always active**: Yes
**Restartable**: No (would reset goals)

---

## 4. soma.kernel.code_validator

**Purpose**: Robinson enforces safety - validates all generated code before execution.

**Responsibility**:
- Validate syntax (AST parsing)
- Check for forbidden imports/operations
- Verify required interfaces
- Ensure thread safety patterns
- Reject unsafe code before materialization

**Critical for**:
- Preventing malicious code execution
- Catching LLM generation errors early
- Maintaining system stability
- Security boundary enforcement

**Core Functions**:
```python
class CodeValidator:
    def validate_syntax(code: str) -> Tuple[bool, str]
    def check_security(code: str) -> List[SecurityIssue]
    def verify_interfaces(code: str, module_name: str) -> bool
    def validate_async_patterns(code: str) -> Tuple[bool, str]
    def pre_materialization_check(code: str) -> ValidationResult
```

**Born at**: Genesis initialization
**Always active**: Yes (blocks unsafe code)
**Restartable**: No (would allow unsafe code)

---

## 5. soma.kernel.memory_keeper

**Purpose**: Robinson remembers - persists state, survives restarts, maintains DNA.

**Responsibility**:
- Load/save DNA at startup and regularly
- Maintain DNA integrity (SHA-256 verification)
- Create versioned backups
- Survive system crashes
- Ensure state consistency

**Critical for**:
- Preserving organ configurations across restarts
- Goal tracking across sessions
- Evolution history (genealogy)
- System identity persistence

**Core Functions**:
```python
class MemoryKeeper:
    def load_dna() -> DNA
    def save_dna(dna: DNA) -> bool
    def verify_integrity(dna: DNA) -> bool
    def create_backup(dna: DNA) -> str
    def restore_from_backup(version: str) -> DNA
    def update_genealogy(event: EvolutionEvent) -> None
```

**Born at**: Before Genesis initialization
**Always active**: Yes (blocks until DNA loads)
**Restartable**: No (would lose state)

---

## 6. soma.kernel.event_logger

**Purpose**: Robinson learns from history - complete audit trail of all evolution.

**Responsibility**:
- Log all significant events
- Create immutable audit trail
- Enable historical analysis
- Support genealogy queries
- Preserve learning records

**Critical for**:
- Understanding evolution history
- Analyzing patterns over time
- Debugging what went wrong
- Teaching new organs about past

**Core Functions**:
```python
class EventLogger:
    def log_event(event_type: str, data: Dict) -> None
    def get_timeline(limit: int = 100) -> List[TimelineEntry]
    def query_events(filters: Dict) -> List[LogEntry]
    def get_genealogy(organ_name: str) -> EvolutionPath
    def export_audit_trail() -> str
```

**Born at**: Genesis initialization
**Always active**: Yes
**Restartable**: Yes (logs append, no state)

---

## Core Organs Status Matrix

| Organ | Purpose | Restartable | Replaceable | Run At Birth |
|-------|---------|-------------|-------------|--------------|
| self_monitor | Know yourself | No | No | Yes |
| error_recovery | Heal yourself | No | No | Yes |
| goal_manager | Know your purpose | No | No | Yes |
| code_validator | Enforce safety | No | No | Yes |
| memory_keeper | Remember | No | No | Yes |
| event_logger | Learn from history | Yes | No | Yes |

---

## Startup Sequence

```
1. MemoryKeeper.load_dna()           ← Restore state first
2. self_monitor.initialize()         ← Know what exists
3. code_validator.initialize()       ← Safety gatekeeper
4. goal_manager.initialize()         ← Load goals
5. error_recovery.initialize()       ← Setup healing
6. event_logger.initialize()         ← Audit trail
7. Genesis.initialize()              ← Now evolution can begin
```

**Critical**: Cores organs must load before Genesis, or the evolution system breaks.

---

## Birth Package Location

These organs are **part of Robinson's birth package**, not evolved:

```
soma/kernel/
├── self_monitor.py          (~150 lines, built-in)
├── error_recovery.py        (~200 lines, built-in)
├── goal_manager.py          (~ 120 lines, built-in)
├── code_validator.py        (~ 180 lines, built-in)
├── memory_keeper.py         (~ 100 lines, built-in)
└── event_logger.py          (~100 lines, built-in)
```

**Not in soma/** (because they're core system, not evolved organs)

---

## Why These 6?

### 1. **self_monitor** - No introspection = blind evolution
   - Genesis can't know what organs are running
   - Architect can't assess current state
   - Circuit breaker can't make health decisions

### 2. **error_recovery** - No recovery = system fragile
   - One bad organ crashes the whole system
   - No learning from failures
   - No resilience or self-healing

### 3. **goal_manager** - No goals = no direction
   - Genesis doesn't know what to evolve
   - No measure of progress
   - System becomes random

### 4. **code_validator** - No validation = unsafe
   - LLM can generate malicious code
   - No safety boundary
   - System becomes vulnerable

### 5. **memory_keeper** - No memory = resets constantly
   - State lost on restart
   - No evolution history
   - Goals forgotten

### 6. **event_logger** - No audit trail = can't learn
   - No way to analyze evolution patterns
   - Can't debug what went wrong
   - Learning impossible

---

## Relationship to Existing Systems

These **core organs complement the kernel**, not replace it:

| Component | Location | Purpose |
|-----------|----------|---------|
| Genesis | seaa/kernel/genesis.py | Orchestrator (stays in kernel) |
| Bus | seaa/kernel/bus.py | Event system (stays in kernel) |
| Assimilator | seaa/kernel/assimilator.py | Module loader (stays in kernel) |
| Materializer | seaa/kernel/materializer.py | Code writer (stays in kernel) |
| **self_monitor** | **soma/kernel/** | System awareness (NEW CORE ORGAN) |
| **error_recovery** | **soma/kernel/** | Resilience (NEW CORE ORGAN) |
| **goal_manager** | **soma/kernel/** | Purpose (NEW CORE ORGAN) |
| **code_validator** | **soma/kernel/** | Safety (NEW CORE ORGAN) |
| **memory_keeper** | **soma/kernel/** | Persistence (NEW CORE ORGAN) |
| **event_logger** | **soma/kernel/** | History (NEW CORE ORGAN) |

---

## Implementation Strategy

### Phase 1: Self-Monitor
```python
class SelfMonitor:
    """Robinson knows itself"""

    def __init__(self):
        self.last_organs_state = {}
        self.vitals_history = []
        bus.subscribe('organ.started', self.on_organ_started)
        bus.subscribe('organ.stopped', self.on_organ_stopped)
        bus.subscribe('organ.error', self.on_organ_error)

    def get_organ_health(self, organ_name: str) -> dict:
        # Query observer for organ info
        from seaa.kernel.observer import get_observer
        observer = get_observer()
        organs = [o for o in observer.get_organs() if o.name == organ_name]
        return organs[0] if organs else None

    def publish_health_event(self):
        # Every 30 seconds
        observer = get_observer()
        health = {
            "organs": len([o for o in observer.get_organs() if o.active]),
            "healthy": len([o for o in observer.get_organs() if o.health == "healthy"]),
            "vitals": observer.get_vitals()
        }
        bus.publish(Event(event_type="system.health", data=health))
```

### Phase 2: Error Recovery
```python
class ErrorRecovery:
    """Robinson heals itself"""

    def __init__(self):
        bus.subscribe('organ.error', self.handle_organ_failure)

    def handle_organ_failure(self, event: Event):
        organ_name = event.data.get('organ')
        error = event.data.get('error')

        # Update circuit breaker
        from seaa.dna.repository import DNARepository
        repo = DNARepository(Path('dna.json'))
        dna = repo.load()

        # Find failure record
        failure = next((f for f in dna.failures if f.module_name == organ_name), None)
        if failure:
            failure.attempt_count += 1
            if failure.attempt_count >= 3:
                failure.circuit_open = True

        repo.save(dna)

        # Suggest fix
        suggestion = self.suggest_fix(organ_name, error)
        bus.publish(Event(event_type="recovery.suggestion", data=suggestion))
```

### Phase 3: Goal Manager
```python
class GoalManager:
    """Robinson has purpose"""

    def __init__(self):
        from seaa.dna.repository import DNARepository
        self.repo = DNARepository(Path('dna.json'))
        self.dna = self.repo.load()

    def check_goal_satisfaction(self):
        """Auto-satisfy goals when organs appear"""
        from seaa.kernel.observer import get_observer
        observer = get_observer()
        active_organs = [o.name for o in observer.get_organs() if o.active]

        for goal in self.dna.goals:
            if not goal.satisfied:
                # Check if required organs are active
                for required_pattern in goal.required_organs:
                    if any(organ.startswith(required_pattern.replace('*', '')) for organ in active_organs):
                        goal.satisfied = True
                        bus.publish(Event(event_type="goal.satisfied", data={"goal": goal.description}))
                        break

        self.repo.save(self.dna)
```

### Phase 4: Code Validator
```python
class CodeValidator:
    """Robinson enforces safety"""

    def validate_syntax(self, code: str) -> tuple:
        import ast
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)

    def check_security(self, code: str) -> list:
        """Check for forbidden imports"""
        forbidden = ['subprocess', 'os.system', 'eval', 'exec', 'pip', '__import__']
        issues = []

        for item in forbidden:
            if item in code:
                issues.append(f"Forbidden: {item}")

        return issues

    def pre_materialization_check(self, code: str) -> dict:
        syntax_ok, syntax_err = self.validate_syntax(code)
        security_issues = self.check_security(code)

        return {
            "valid": syntax_ok and len(security_issues) == 0,
            "syntax_error": syntax_err,
            "security_issues": security_issues
        }
```

### Phase 5: Memory Keeper
```python
class MemoryKeeper:
    """Robinson remembers"""

    def __init__(self):
        self.repo = DNARepository(Path('dna.json'))

    def load_dna(self) -> DNA:
        return self.repo.load()

    def save_dna(self, dna: DNA) -> bool:
        try:
            self.repo.save(dna)
            return True
        except Exception as e:
            logger.error(f"Failed to save DNA: {e}")
            return False

    def verify_integrity(self, dna: DNA) -> bool:
        # SHA-256 verification already in repository
        return self.repo.verify_hash(dna)
```

### Phase 6: Event Logger
```python
class EventLogger:
    """Robinson learns from history"""

    def __init__(self):
        self.log_file = Path('logs/evolution.log')
        self.log_file.parent.mkdir(exist_ok=True)
        bus.subscribe('*', self.log_event)

    def log_event(self, event: Event):
        """Log all events to audit trail"""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event.event_type,
            "data": event.data
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_timeline(self, limit: int = 100) -> list:
        """Query evolution history"""
        entries = []
        with open(self.log_file, 'r') as f:
            for line in f:
                entries.append(json.loads(line))
        return entries[-limit:]
```

---

## Benefits of Core Organs

### 1. **Clarity**: Robinson's essential systems are visible
   - Not hidden in kernel code
   - Clear interfaces and contracts
   - Can be audited and understood

### 2. **Maintainability**: Core logic is separated
   - Kernel stays small and stable
   - Core organs are focused
   - Easier to test and debug

### 3. **Scalability**: Foundation is solid
   - Evolution can build on core
   - No circular dependencies
   - Clear layer separation

### 4. **Teaching**: Future systems can learn from example
   - New organs see working patterns
   - Can replicate core organ structure
   - Understand system boundaries

### 5. **Autonomy**: System is truly self-contained
   - All necessary systems present at birth
   - No external dependencies
   - Can run in any environment

---

## Summary

Robinson should be **born with 6 core organs** that enable everything else:

1. **self_monitor** - "I know myself"
2. **error_recovery** - "I heal myself"
3. **goal_manager** - "I know my purpose"
4. **code_validator** - "I enforce safety"
5. **memory_keeper** - "I remember"
6. **event_logger** - "I learn from history"

These are **not optional**. They are **Robinson's immune system, nervous system, and evolutionary machinery**. Without them, Robinson can't be autonomous.

---

**Status**: Ready to implement
**Priority**: CRITICAL (before any evolution begins)
**Effort**: ~1000 lines of Python
**Benefit**: Complete autonomous system

