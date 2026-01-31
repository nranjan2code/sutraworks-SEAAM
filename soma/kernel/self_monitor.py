from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
from seaa.dna.repository import DNARepository
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import threading

logger = get_logger("soma.kernel.self_monitor")

@dataclass
class OrganVitals:
    """Health metrics for a single organ"""
    name: str
    status: str  # "healthy", "degraded", "failed", "recovering"
    last_event_time: float
    event_count: int = 0
    error_count: int = 0
    health_score: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SystemVitals:
    """Overall system health metrics"""
    total_organs: int
    healthy_organs: int
    degraded_organs: int
    failed_organs: int
    total_events: int
    goals_satisfied: int
    total_goals: int
    uptime_seconds: float
    health_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SelfMonitor:
    """System introspection and health monitoring organ.

    Provides Robinson with self-awareness by:
    - Tracking all active organs and their health
    - Monitoring event bus activity
    - Calculating system-wide health metrics
    - Publishing health events for other organs to consume
    """

    def __init__(self):
        self.organ_vitals: Dict[str, OrganVitals] = {}
        self.event_counts: Dict[str, int] = {}
        self.start_time = time.time()
        self.lock = threading.Lock()
        self.dna_repo = DNARepository()

        # Subscribe to all events to track system activity
        bus.subscribe('*', self._on_event)

        # Start health publication loop
        threading.Thread(target=self._health_publisher_loop, daemon=True).start()

        logger.info("SelfMonitor initialized - Robinson can now perceive itself")

    def _on_event(self, event: Event) -> None:
        """Track all event activity for vitals calculation"""
        with self.lock:
            # Count events by type
            self.event_counts[event.event_type] = self.event_counts.get(event.event_type, 0) + 1

            # Track organ-level events (format: "organ.something")
            if '.' in event.event_type:
                organ_prefix = event.event_type.split('.')[0]
                if organ_prefix == 'organ':
                    # Events like "organ.soma.xyz.started", "organ.soma.xyz.failed"
                    parts = event.event_type.split('.')
                    if len(parts) >= 3:
                        organ_name = '.'.join(parts[1:-1])
                        event_action = parts[-1]

                        if event_action == 'started':
                            self._update_organ_status(organ_name, 'healthy')
                        elif event_action == 'failed':
                            self._update_organ_status(organ_name, 'failed', error=True)
                        elif event_action == 'recovered':
                            self._update_organ_status(organ_name, 'healthy')
                        elif event_action == 'degraded':
                            self._update_organ_status(organ_name, 'degraded')

    def _update_organ_status(self, organ_name: str, status: str, error: bool = False) -> None:
        """Update vitals for a specific organ"""
        if organ_name not in self.organ_vitals:
            self.organ_vitals[organ_name] = OrganVitals(
                name=organ_name,
                status=status,
                last_event_time=time.time(),
                event_count=1,
                error_count=1 if error else 0,
                health_score=100.0 if status == 'healthy' else 50.0
            )
        else:
            vitals = self.organ_vitals[organ_name]
            vitals.status = status
            vitals.last_event_time = time.time()
            vitals.event_count += 1
            if error:
                vitals.error_count += 1

            # Update health score based on error rate
            if vitals.event_count > 0:
                error_rate = vitals.error_count / vitals.event_count
                vitals.health_score = max(0, 100.0 * (1.0 - error_rate))

    def get_organ_health(self, organ_name: str) -> Optional[OrganVitals]:
        """Get health metrics for a specific organ"""
        with self.lock:
            return self.organ_vitals.get(organ_name)

    def get_all_organs(self) -> List[OrganVitals]:
        """Get health metrics for all known organs"""
        with self.lock:
            return list(self.organ_vitals.values())

    def get_system_vitals(self) -> SystemVitals:
        """Calculate and return overall system health"""
        with self.lock:
            # Get DNA to check goals
            dna = self.dna_repo.load()

            # Count organs by status
            healthy = sum(1 for v in self.organ_vitals.values() if v.status == 'healthy')
            degraded = sum(1 for v in self.organ_vitals.values() if v.status == 'degraded')
            failed = sum(1 for v in self.organ_vitals.values() if v.status == 'failed')

            # Count satisfied goals
            goals_satisfied = sum(1 for g in dna.goals if g.satisfied)
            total_goals = len(dna.goals)

            # Overall health score (weighted)
            total_events = sum(self.event_counts.values())
            avg_organ_health = sum(v.health_score for v in self.organ_vitals.values()) / len(self.organ_vitals.values()) if self.organ_vitals else 100.0
            goal_satisfaction_rate = goals_satisfied / total_goals if total_goals > 0 else 0
            overall_health = (avg_organ_health * 0.6) + (goal_satisfaction_rate * 100 * 0.4)

            uptime = time.time() - self.start_time

            return SystemVitals(
                total_organs=len(self.organ_vitals),
                healthy_organs=healthy,
                degraded_organs=degraded,
                failed_organs=failed,
                total_events=total_events,
                goals_satisfied=goals_satisfied,
                total_goals=total_goals,
                uptime_seconds=uptime,
                health_score=overall_health
            )

    def get_active_organs(self) -> List[str]:
        """Get list of all active organ names"""
        with self.lock:
            return list(self.organ_vitals.keys())

    def _health_publisher_loop(self) -> None:
        """Publish health metrics periodically so Genesis can make informed decisions"""
        interval = getattr(config, 'health_check_interval_seconds', 5)

        while True:
            try:
                time.sleep(interval)

                vitals = self.get_system_vitals()

                # Publish system health event
                bus.publish(Event(
                    event_type='system.health_check',
                    data={
                        'vitals': vitals.to_dict(),
                        'organs': [v.to_dict() for v in self.get_all_organs()],
                        'timestamp': time.time()
                    }
                ))

                # Log health status
                logger.debug(
                    "System health check",
                    health_score=vitals.health_score,
                    organs=vitals.total_organs,
                    healthy=vitals.healthy_organs,
                    goals_satisfied=f"{vitals.goals_satisfied}/{vitals.total_goals}"
                )

            except Exception as e:
                logger.error("Error in health publisher loop", error=str(e))

# REQUIRED ENTRY POINT (zero required args)
def start():
    monitor = SelfMonitor()
