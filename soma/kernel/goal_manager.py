from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
from seaa.dna.repository import DNARepository
from seaa.dna.schema import Goal
import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import asdict

logger = get_logger("soma.kernel.goal_manager")

class GoalManager:
    """Purpose-driven evolution engine for Robinson.

    Manages goals by:
    - Tracking satisfaction of system goals
    - Auto-detecting newly satisfied goals
    - Publishing goal events for Genesis to act on
    - Recommending next evolution targets based on unsatisfied goals
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.dna_repo = DNARepository()
        self.last_check_time = time.time()

        # Subscribe to all events to detect goal satisfaction
        bus.subscribe('*', self._on_event)

        # Start goal checker loop
        threading.Thread(target=self._goal_checker_loop, daemon=True).start()

        logger.info("GoalManager initialized - Robinson now has purpose")

    def _on_event(self, event: Event) -> None:
        """Monitor events to detect newly satisfied goals"""
        # Goal satisfaction can be detected from organ creation events
        if event.event_type.startswith('organ.') and event.event_type.endswith('.started'):
            self._check_goal_satisfaction()

    def _check_goal_satisfaction(self) -> None:
        """Check if any new goals are satisfied"""
        with self.lock:
            dna = self.dna_repo.load()
            newly_satisfied = []

            for goal in dna.goals:
                if not goal.satisfied:
                    # Check if required organs are active
                    if self._are_organs_active(goal.required_organs, dna):
                        goal.satisfied = True
                        newly_satisfied.append(goal)

                        logger.info(
                            f"Goal satisfied: {goal.description[:50]}...",
                            priority=goal.priority
                        )

            # Save updated DNA if any goals were satisfied
            if newly_satisfied:
                self.dna_repo.save(dna)

                # Publish goal satisfaction event
                bus.publish(Event(
                    event_type='goals.satisfied',
                    data={
                        'count': len(newly_satisfied),
                        'goals': [
                            {
                                'description': g.description,
                                'priority': g.priority,
                                'required_organs': g.required_organs
                            }
                            for g in newly_satisfied
                        ],
                        'timestamp': time.time()
                    }
                ))

    def _are_organs_active(self, required_patterns: List[str], dna) -> bool:
        """Check if organs matching required patterns are active"""
        if not required_patterns:
            return True

        active_organs = dna.active_modules
        for pattern in required_patterns:
            # Pattern matching: "soma.perception.*" matches "soma.perception.observer"
            if pattern.endswith('*'):
                prefix = pattern[:-1]
                if any(organ.startswith(prefix) for organ in active_organs):
                    continue
                else:
                    return False
            else:
                # Exact match
                if pattern in active_organs:
                    continue
                else:
                    return False

        return True

    def get_goal_status(self) -> Dict:
        """Get overall goal progress"""
        with self.lock:
            dna = self.dna_repo.load()

            total = len(dna.goals)
            satisfied = sum(1 for g in dna.goals if g.satisfied)

            return {
                'total_goals': total,
                'satisfied_goals': satisfied,
                'progress_percent': (satisfied / total * 100) if total > 0 else 0,
                'satisfaction_rate': satisfied / total if total > 0 else 0
            }

    def get_unsatisfied_goals(self) -> List[Goal]:
        """Get list of unsatisfied goals"""
        with self.lock:
            dna = self.dna_repo.load()
            return [g for g in dna.goals if not g.satisfied]

    def get_satisfied_goals(self) -> List[Goal]:
        """Get list of satisfied goals"""
        with self.lock:
            dna = self.dna_repo.load()
            return [g for g in dna.goals if g.satisfied]

    def recommend_next_evolution(self) -> Optional[Dict]:
        """Recommend the next evolution target based on unsatisfied goals"""
        with self.lock:
            dna = self.dna_repo.load()

            # Get high-priority unsatisfied goals
            unsatisfied = [g for g in dna.goals if not g.satisfied]
            high_priority = [g for g in unsatisfied if g.priority <= 2]

            if not high_priority:
                high_priority = unsatisfied

            if not high_priority:
                # All goals satisfied!
                logger.info("All system goals satisfied!")
                return None

            # Get the highest priority unsatisfied goal
            next_goal = min(high_priority, key=lambda g: (g.priority, g.created_at))

            return {
                'goal_description': next_goal.description,
                'required_organs': next_goal.required_organs,
                'priority': next_goal.priority,
                'why': f"This is a priority {next_goal.priority} goal and is currently unsatisfied"
            }

    def add_goal(self, description: str, priority: int = 3, required_organs: Optional[List[str]] = None) -> Goal:
        """Add a new goal to the system"""
        with self.lock:
            dna = self.dna_repo.load()

            new_goal = Goal(
                description=description,
                priority=priority,
                satisfied=False,
                created_at=time.time(),
                required_organs=required_organs or []
            )

            dna.goals.append(new_goal)
            self.dna_repo.save(dna)

            logger.info(
                f"New goal added: {description[:50]}...",
                priority=priority
            )

            # Publish goal added event
            bus.publish(Event(
                event_type='goal.added',
                data={
                    'description': description,
                    'priority': priority,
                    'required_organs': required_organs,
                    'timestamp': time.time()
                }
            ))

            return new_goal

    def _goal_checker_loop(self) -> None:
        """Periodically check for newly satisfied goals"""
        check_interval = getattr(config, 'goal_check_interval_seconds', 10)

        while True:
            try:
                time.sleep(check_interval)
                self._check_goal_satisfaction()

                # Log current progress
                status = self.get_goal_status()
                logger.debug(
                    "Goal satisfaction check",
                    satisfied=f"{status['satisfied_goals']}/{status['total_goals']}",
                    progress=f"{status['progress_percent']:.1f}%"
                )

            except Exception as e:
                logger.error("Error in goal checker loop", error=str(e))

# REQUIRED ENTRY POINT (zero required args)
def start():
    manager = GoalManager()
