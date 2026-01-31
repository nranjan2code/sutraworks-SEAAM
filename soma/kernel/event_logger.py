from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import json
import threading
import time
from typing import List, Dict, Optional
from collections import deque
from dataclasses import dataclass, asdict

logger = get_logger("soma.kernel.event_logger")

@dataclass
class TimelineEntry:
    """A single entry in the evolution timeline"""
    event_type: str
    timestamp: float
    organ_name: Optional[str]
    data: Dict

    def to_dict(self) -> Dict:
        return asdict(self)

class EventLogger:
    """Evolution audit trail and learning engine.

    Maintains complete history of Robinson's evolution by:
    - Recording all important system events
    - Detecting evolution patterns
    - Enabling post-mortem analysis
    - Supporting continuous learning
    - Preserving institutional knowledge
    """

    def __init__(self):
        self.lock = threading.Lock()

        # Keep last N events in memory for fast access
        self.max_memory_events = getattr(config, 'event_logger_memory_events', 1000)
        self.recent_events: deque = deque(maxlen=self.max_memory_events)

        # Subscribe to evolution-critical events
        bus.subscribe('organ.*.started', self._on_event)
        bus.subscribe('organ.*.failed', self._on_event)
        bus.subscribe('organ.*.recovered', self._on_event)
        bus.subscribe('goal.satisfied', self._on_event)
        bus.subscribe('goal.added', self._on_event)
        bus.subscribe('code.validated', self._on_event)
        bus.subscribe('system.health_check', self._on_event)
        bus.subscribe('recovery.action_executed', self._on_event)

        # Start periodic analysis loop
        threading.Thread(target=self._analysis_loop, daemon=True).start()

        logger.info("EventLogger initialized - Robinson can learn from history")

    def _on_event(self, event: Event) -> None:
        """Log all important events"""
        with self.lock:
            # Parse organ name from event type if applicable
            organ_name = None
            if event.event_type.startswith('organ.'):
                # Format: organ.soma.xyz.started
                parts = event.event_type.split('.')
                if len(parts) >= 3:
                    organ_name = '.'.join(parts[1:-1])

            entry = TimelineEntry(
                event_type=event.event_type,
                timestamp=time.time(),
                organ_name=organ_name,
                data=event.data
            )

            self.recent_events.append(entry)

    def get_timeline(self, limit: int = 100, organ_name: Optional[str] = None) -> List[TimelineEntry]:
        """Get timeline of events, optionally filtered by organ"""
        with self.lock:
            events = list(self.recent_events)

            # Filter if organ specified
            if organ_name:
                events = [e for e in events if e.organ_name == organ_name]

            # Return most recent N events
            return events[-limit:]

    def get_evolution_history(self) -> Dict:
        """Get summary of evolution progress"""
        with self.lock:
            events = list(self.recent_events)

            # Count organ events
            organ_started = len([e for e in events if e.event_type.endswith('.started')])
            organ_failed = len([e for e in events if e.event_type.endswith('.failed')])
            organ_recovered = len([e for e in events if e.event_type.endswith('.recovered')])

            # Count goals
            goals_satisfied = len([e for e in events if e.event_type == 'goal.satisfied'])
            goals_added = len([e for e in events if e.event_type == 'goal.added'])

            # Get first and last event times
            first_event_time = events[0].timestamp if events else time.time()
            last_event_time = events[-1].timestamp if events else time.time()
            runtime = last_event_time - first_event_time

            return {
                'total_events': len(events),
                'organs_started': organ_started,
                'organs_failed': organ_failed,
                'organs_recovered': organ_recovered,
                'goals_satisfied': goals_satisfied,
                'goals_added': goals_added,
                'runtime_seconds': runtime,
                'average_events_per_minute': (len(events) / runtime * 60) if runtime > 0 else 0
            }

    def get_organ_evolution(self, organ_name: str) -> List[Dict]:
        """Get complete evolution history of a specific organ"""
        with self.lock:
            events = list(self.recent_events)
            organ_events = [
                e.to_dict() for e in events
                if e.organ_name == organ_name
            ]
            return organ_events

    def analyze_patterns(self) -> Dict:
        """Analyze evolution patterns to detect trends"""
        with self.lock:
            events = list(self.recent_events)

            if len(events) < 10:
                return {'error': 'Insufficient event history for pattern analysis'}

            # Detect failure patterns
            failure_windows = {}
            for i, event in enumerate(events):
                if event.event_type.endswith('.failed'):
                    organ = event.organ_name or 'unknown'
                    if organ not in failure_windows:
                        failure_windows[organ] = []
                    failure_windows[organ].append(event.timestamp)

            # Calculate failure frequency
            failure_frequency = {}
            for organ, times in failure_windows.items():
                if len(times) > 1:
                    intervals = [times[i + 1] - times[i] for i in range(len(times) - 1)]
                    avg_interval = sum(intervals) / len(intervals)
                    failure_frequency[organ] = {
                        'total_failures': len(times),
                        'average_interval_seconds': avg_interval,
                        'recurrence_rate': 'high' if avg_interval < 300 else 'low'
                    }

            # Detect successful evolution sequences
            success_chains = []
            current_chain = []
            for event in events:
                if event.event_type.endswith('.started'):
                    current_chain.append(event.organ_name)
                elif event.event_type.endswith('.failed'):
                    if current_chain:
                        success_chains.append(current_chain)
                    current_chain = []

            return {
                'failure_patterns': failure_frequency,
                'successful_evolution_chains': len(success_chains),
                'longest_chain': max(len(c) for c in success_chains) if success_chains else 0,
                'total_events_analyzed': len(events),
                'pattern_confidence': 'high' if len(events) > 100 else 'low'
            }

    def get_insights(self) -> List[str]:
        """Generate learning insights from event history"""
        with self.lock:
            insights = []

            history = self.get_evolution_history()
            if history.get('organs_failed', 0) > 0:
                fail_rate = history['organs_failed'] / max(history['organs_started'], 1)
                if fail_rate > 0.3:
                    insights.append(f"High failure rate detected ({fail_rate:.1%}) - investigate stability")

            patterns = self.analyze_patterns()
            if patterns.get('failure_patterns'):
                for organ, stats in patterns['failure_patterns'].items():
                    if stats.get('recurrence_rate') == 'high':
                        insights.append(f"Organ {organ} failing repeatedly - may need redesign")

            if history.get('goals_satisfied', 0) == 0:
                insights.append("No goals satisfied yet - focus on foundational requirements")
            else:
                insights.append(f"Progress: {history['goals_satisfied']} goals satisfied")

            return insights

    def _analysis_loop(self) -> None:
        """Periodically analyze patterns and publish insights"""
        analysis_interval = getattr(config, 'event_logger_analysis_interval_seconds', 300)

        while True:
            try:
                time.sleep(analysis_interval)

                patterns = self.analyze_patterns()
                insights = self.get_insights()

                # Publish analysis event
                bus.publish(Event(
                    event_type='evolution.analysis',
                    data={
                        'patterns': patterns,
                        'insights': insights,
                        'timestamp': time.time()
                    }
                ))

                logger.debug(
                    "Evolution analysis completed",
                    insights_count=len(insights),
                    pattern_confidence=patterns.get('pattern_confidence', 'unknown')
                )

            except Exception as e:
                logger.error("Error in analysis loop", error=str(e))

# REQUIRED ENTRY POINT (zero required args)
def start():
    logger_instance = EventLogger()
