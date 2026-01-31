from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
from seaa.dna.repository import DNARepository
import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = get_logger("soma.kernel.error_recovery")

@dataclass
class RecoveryAction:
    """Describes an action taken during error recovery"""
    organ_name: str
    error_message: str
    action_taken: str  # "retry", "circuit_break", "restart", "notify"
    success: bool
    timestamp: float

class ErrorRecovery:
    """Self-healing mechanism for Robinson.

    Handles organ failures by:
    - Catching exceptions from failing organs
    - Executing recovery procedures (retry, restart, circuit break)
    - Logging failures for learning
    - Publishing recovery events
    """

    def __init__(self):
        self.recovery_history: List[RecoveryAction] = []
        self.organ_retry_counts: Dict[str, int] = {}
        self.lock = threading.Lock()
        self.dna_repo = DNARepository()

        # Subscribe to organ failure events
        bus.subscribe('organ.*.failed', self._on_organ_failure)
        bus.subscribe('organ.*.error', self._on_organ_error)

        logger.info("ErrorRecovery initialized - Robinson can now heal itself")

    def _on_organ_failure(self, event: Event) -> None:
        """Handle organ failure events"""
        organ_name = event.data.get('organ_name') or event.data.get('name', 'unknown')
        error = event.data.get('error', str(event.data))

        logger.warn(
            f"Organ failure detected: {organ_name}",
            error=error
        )

        # Execute recovery procedure
        success = self.execute_recovery_procedure(organ_name, error)

    def _on_organ_error(self, event: Event) -> None:
        """Handle non-fatal organ errors (degraded state)"""
        organ_name = event.data.get('organ_name') or event.data.get('name', 'unknown')
        error = event.data.get('error', str(event.data))

        logger.warn(
            f"Organ error (non-fatal): {organ_name}",
            error=error
        )

    def execute_recovery_procedure(self, organ_name: str, error_message: str) -> bool:
        """Execute recovery strategy for a failing organ"""
        with self.lock:
            # Get retry count
            retry_count = self.organ_retry_counts.get(organ_name, 0)
            max_retries = getattr(config, 'max_organ_retries', 3)

            # Get DNA to check circuit breaker status
            dna = self.dna_repo.load()

            action_taken = "unknown"
            success = False

            # Strategy 1: Check if organ should be attempted (circuit breaker)
            if dna.should_attempt(organ_name, max_attempts=max_retries, cooldown_minutes=30):
                if retry_count < max_retries:
                    # Strategy 2: Retry
                    action_taken = "retry"
                    self.organ_retry_counts[organ_name] = retry_count + 1
                    success = True

                    # Publish retry event
                    bus.publish(Event(
                        event_type=f'organ.{organ_name}.retry',
                        data={
                            'organ_name': organ_name,
                            'retry_attempt': retry_count + 1,
                            'max_retries': max_retries,
                            'timestamp': time.time()
                        }
                    ))

                    logger.info(
                        f"Retrying organ: {organ_name}",
                        attempt=f"{retry_count + 1}/{max_retries}"
                    )
                else:
                    # Strategy 3: Circuit break - disable this organ temporarily
                    action_taken = "circuit_break"
                    success = True

                    # Mark in DNA as failed (circuit breaker will prevent re-attempts)
                    dna.mark_failure(organ_name, error_message)
                    self.dna_repo.save(dna)

                    # Publish circuit break event
                    bus.publish(Event(
                        event_type=f'organ.{organ_name}.circuit_broken',
                        data={
                            'organ_name': organ_name,
                            'reason': 'exceeded_max_retries',
                            'error': error_message,
                            'timestamp': time.time()
                        }
                    ))

                    logger.warn(
                        f"Circuit breaker activated for organ: {organ_name}",
                        retries_exhausted=retry_count
                    )
            else:
                # Organ is in cooldown period
                action_taken = "circuit_break_cooldown"
                success = False

                logger.info(
                    f"Organ {organ_name} in cooldown period - will retry later"
                )

            # Log recovery action
            recovery_action = RecoveryAction(
                organ_name=organ_name,
                error_message=error_message[:200],  # Truncate long errors
                action_taken=action_taken,
                success=success,
                timestamp=time.time()
            )
            self.recovery_history.append(recovery_action)

            # Publish recovery event for system awareness
            bus.publish(Event(
                event_type='recovery.action_executed',
                data=asdict(recovery_action)
            ))

            return success

    def reset_organ_retry(self, organ_name: str) -> None:
        """Reset retry counter for a successfully recovered organ"""
        with self.lock:
            if organ_name in self.organ_retry_counts:
                self.organ_retry_counts[organ_name] = 0

    def get_recovery_history(self) -> List[RecoveryAction]:
        """Get history of recovery actions"""
        with self.lock:
            return list(self.recovery_history)

    def get_organ_status(self, organ_name: str) -> Dict:
        """Get recovery status of a specific organ"""
        with self.lock:
            retry_count = self.organ_retry_counts.get(organ_name, 0)
            max_retries = getattr(config, 'max_organ_retries', 3)

            # Get recent recovery history for this organ
            recent = [
                r for r in self.recovery_history
                if r.organ_name == organ_name
            ][-5:]

            return {
                'organ_name': organ_name,
                'retry_count': retry_count,
                'max_retries': max_retries,
                'recent_actions': [asdict(r) for r in recent]
            }

# REQUIRED ENTRY POINT (zero required args)
def start():
    recovery = ErrorRecovery()
