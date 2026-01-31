"""
SEAA Genesis - The Primal Will

The slim orchestrator that coordinates the system lifecycle.
All complex logic is delegated to specialized components:
- Assimilator: Module loading
- Materializer: Code writing
- Immunity: Error recovery
- Architect: Design decisions
- Gateway: LLM communication

This module focuses purely on orchestration.
"""

import os
import sys
import signal
import threading
import time
from pathlib import Path
from typing import Callable, Optional, Union

from seaa.core.logging import get_logger, setup_logging
from seaa.core.config import config
from seaa.core.exceptions import (
    SEAAError,
    ImportFailedError,
    AssimilationError,
)
from seaa.dna import DNA, DNARepository
from seaa.dna.schema import FailureType, OrganBlueprint
from seaa.kernel.bus import bus, Event
from seaa.kernel.assimilator import Assimilator
from seaa.kernel.materializer import Materializer
from seaa.kernel.immunity import Immunity
from seaa.connectors.llm_gateway import ProviderGateway
from seaa.cortex.architect import Architect
from seaa.kernel.genealogy import Genealogy

logger = get_logger("genesis")


class Genesis:
    """
    The Primal Will.
    
    Genesis orchestrates the lifecycle of the SEAA system:
    1. Awakening - Load DNA, initialize components
    2. Evolution - Architect designs, Gateway generates, Materializer writes
    3. Assimilation - Load and activate organs
    4. Life - Continuous metabolic loop
    
    All complex logic is delegated to specialized components.
    """
    
    def __init__(self, root_dir: Optional[Union[Path, str]] = None):
        """
        Initialize the Genesis system.

        Args:
            root_dir: Project root directory (default: current working directory)

        Raises:
            ValueError: If configuration is invalid
        """
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()

        # Validate configuration
        config_errors = config.validate()
        if config_errors:
            error_msg = "Invalid configuration:\n  - " + "\n  - ".join(config_errors)
            raise ValueError(error_msg)

        # Setup logging from config
        setup_logging(
            level=config.logging.level,
            format_type=config.logging.format,
            log_file=config.logging.file,
        )
        
        # Initialize DNA repository
        dna_path = config.paths.dna
        self.dna_repo = DNARepository(dna_path)
        self.dna = self.dna_repo.load_or_create()
        
        # Initialize Evolutionary Memory (Git)
        # MUST be initialized before Immunity so it can use it for rollback
        self.genealogy = Genealogy()
        self.genealogy.init_repo()
        
        # Initialize components with callbacks
        self.materializer = Materializer(self.root_dir)
        self.assimilator = Assimilator(on_failure=self._handle_assimilation_failure)
        self.immunity = Immunity(
            root_dir=self.root_dir,
            on_blueprint_needed=self._handle_blueprint_request,
            on_failure_report=self._handle_failure_report,
            genealogy=self.genealogy,
        )
        
        # Initialize LLM gateway
        self.gateway = ProviderGateway()
        
        # Initialize Architect
        self.architect = Architect(
            dna=self.dna,
            gateway=self.gateway,
            save_callback=self._save_dna,
        )
        
        # Lifecycle state
        self._running = False
        self._setup_signal_handlers()
        
        logger.info(f"Genesis initialized: {self.dna.system_name} v{self.dna.system_version}")
    
    def _setup_signal_handlers(self) -> None:
        """Setup graceful shutdown handlers.

        Note: Signal handlers can only be registered in the main thread.
        When Genesis runs in a background thread (e.g., interactive CLI),
        we skip signal registration - shutdown is handled by the runtime.
        """
        # Signal handlers can only be set from main thread
        if threading.current_thread() is not threading.main_thread():
            logger.debug("Running in background thread, skipping signal handlers")
            return

        def shutdown_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self._running = False

        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)
    
    def awaken(self) -> None:
        """
        The main awakening sequence.
        
        1. Log startup
        2. Run initial evolution loop
        3. Assimilate existing organs
        4. Enter metabolic life loop
        """
        logger.info("=" * 50)
        logger.info(f"SEAA v{self.dna.system_version} AWAKENING")
        logger.info("=" * 50)
        
        # Start event bus worker
        bus.start_worker()
        
        # Phase 1: Initial Evolution (Architect designs, Genesis builds)
        logger.info("[PHASE 1] Evolution...")
        self._evolution_cycle()
        
        # Phase 2: Assimilation (Load all built organs)
        logger.info("[PHASE 2] Assimilation...")
        self._assimilate_all()
        
        # Phase 3: Life Loop
        self._running = True
        logger.info("[PHASE 3] Entering life loop...")
        self._live()
    
    def _evolution_cycle(self, max_iterations: int = 10) -> int:
        """
        Run evolution until no more blueprints are pending.

        Args:
            max_iterations: Safety limit to prevent infinite loops

        Returns:
            Number of organs evolved
        """
        evolved_count = 0

        for iteration in range(max_iterations):
            # Ask Architect to reflect
            self.architect.reflect()

            # Check for pending blueprints
            pending = self.dna.get_pending_blueprints()
            if not pending:
                logger.info(f"Evolution complete: {evolved_count} organs grown")
                break

            # Build pending organs (filter by dependencies, limited per cycle)
            organs_this_cycle = self._get_buildable_organs(pending)
            organs_this_cycle = organs_this_cycle[:config.metabolism.max_organs_per_cycle]

            if not organs_this_cycle and pending:
                # Pending organs exist but have unsatisfied dependencies
                logger.warning(f"Waiting for dependencies: {list(pending.keys())}")
                break

            for organ_name, blueprint in organs_this_cycle:
                if self._evolve_organ(organ_name, blueprint):
                    evolved_count += 1

        return evolved_count
    
    def _get_buildable_organs(self, pending: dict) -> list:
        """
        Filter pending organs to only those with satisfied dependencies.

        Args:
            pending: Dictionary of pending blueprints

        Returns:
            List of (organ_name, blueprint) tuples that can be built now
        """
        buildable = []
        active_modules = set(self.dna.active_modules)

        for organ_name, blueprint in pending.items():
            # Check if dependencies are satisfied
            if not blueprint.dependencies:
                # No dependencies, always buildable
                buildable.append((organ_name, blueprint))
                continue

            # Check each dependency
            all_satisfied = True
            for dep in blueprint.dependencies:
                # Support wildcard patterns (e.g., "soma.perception.*")
                if "*" in dep:
                    pattern = dep.replace("*", "")
                    satisfied = any(mod.startswith(pattern) for mod in active_modules)
                else:
                    satisfied = dep in active_modules

                if not satisfied:
                    all_satisfied = False
                    logger.debug(f"Unsatisfied dependency: {organ_name} requires {dep}")
                    break

            if all_satisfied:
                buildable.append((organ_name, blueprint))

        return buildable

    def _evolve_organ(self, organ_name: str, blueprint: OrganBlueprint) -> bool:
        """
        Generate and materialize a single organ.

        Args:
            organ_name: Fully qualified module name
            blueprint: The organ blueprint

        Returns:
            True if successful
        """
        # Circuit breaker check
        if not self.dna.should_attempt(
            organ_name,
            max_attempts=config.circuit_breaker.max_attempts,
            cooldown_minutes=config.circuit_breaker.cooldown_minutes,
        ):
            logger.warning(f"Circuit breaker OPEN for {organ_name}, skipping evolution")
            return False

        # Resource limit check
        if len(self.dna.active_modules) >= config.metabolism.max_total_organs:
            logger.warning(f"Max total organs ({config.metabolism.max_total_organs}) reached, skipping {organ_name}")
            return False

        logger.info(f"Evolving: {organ_name}")
        
        try:
            # Generate code via LLM (pass active modules for context)
            code = self.gateway.generate_code(
                organ_name,
                blueprint.description,
                active_modules=self.dna.active_modules,
            )
            
            if not code:
                logger.error(f"Failed to generate code for {organ_name}")
                self.dna.add_failure(
                    organ_name,
                    FailureType.GENERATION,
                    "LLM failed to generate code"
                )
                self._save_dna()
                return False
            
            # Materialize to filesystem
            self.materializer.materialize(organ_name, code)
            
            # Mark as active in DNA
            self.dna.mark_active(organ_name)
            
            # Clear any previous failures
            self.dna.clear_failure(organ_name)
            
            self._save_dna()
            logger.info(f"✓ Evolved: {organ_name}")
            
            # Emit event
            bus.publish(Event(
                event_type="organ.evolved",
                data={"organ": organ_name},
                source="genesis",
            ))

            # Commit the evolution to memory
            self.genealogy.commit(f"Evolved: {organ_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Evolution failed for {organ_name}: {e}")
            self.dna.add_failure(
                organ_name,
                FailureType.MATERIALIZATION,
                str(e)
            )
            self._save_dna()
            return False
    
    def _assimilate_all(self) -> int:
        """
        Assimilate all active organs that aren't already running.

        Returns:
            Number successfully integrated
        """
        active = self.dna.active_modules
        already_running = self.assimilator.get_running_organs()

        to_integrate = [m for m in active if m not in already_running]

        if not to_integrate:
            logger.info("No new organs to integrate")
            return 0

        # Resource limit check
        max_concurrent = config.metabolism.max_concurrent_organs
        current_running = len(already_running)
        available_slots = max_concurrent - current_running

        if available_slots <= 0:
            logger.warning(f"Max concurrent organs ({max_concurrent}) reached, skipping integration")
            return 0

        # Limit integration to available slots
        if len(to_integrate) > available_slots:
            logger.info(f"Limiting integration to {available_slots} organs (max concurrent: {max_concurrent})")
            to_integrate = to_integrate[:available_slots]

        logger.info(f"Integrating {len(to_integrate)} organs...")
        
        success_count = 0
        for module_name in to_integrate:
            try:
                if self.assimilator.integrate(module_name):
                    success_count += 1
                    
                    # Emit event
                    bus.publish(Event(
                        event_type="organ.integrated",
                        data={"organ": module_name},
                        source="genesis",
                    ))
                    
            except ImportFailedError as e:
                # Try to heal the import issue
                self.immunity.heal(e.module_name)
                
            except AssimilationError:
                # Already logged and reported by assimilator
                pass
        
        logger.info(f"Integrated {success_count}/{len(to_integrate)} organs")
        return success_count
    
    def _live(self) -> None:
        """
        The metabolic life loop.
        
        Continuously:
        1. Sleep for configured interval
        2. Reflect on goals
        3. Evolve if needed
        4. Integrate new organs
        """
        interval = config.metabolism.cycle_interval_seconds
        logger.info(f"Entering metabolic stasis (cycle every {interval}s, Ctrl+C to stop)")
        
        try:
            while self._running:
                time.sleep(interval)
                
                if not self._running:
                    break
                
                logger.info("─" * 30)
                logger.info("METABOLIC CYCLE")
                
                # Reflect and evolve
                self.architect.reflect()
                pending = self.dna.get_pending_blueprints()
                
                if pending:
                    logger.info(f"New needs: {list(pending.keys())}")
                    for organ_name, blueprint in list(pending.items())[:config.metabolism.max_organs_per_cycle]:
                        if self._evolve_organ(organ_name, blueprint):
                            # Integrate immediately
                            try:
                                self.assimilator.integrate(organ_name)
                            except AssimilationError:
                                pass
                
                # Emit heartbeat
                bus.publish(Event(
                    event_type="system.heartbeat",
                    data={
                        "running_organs": len(self.assimilator.get_running_organs()),
                        "pending_blueprints": len(pending),
                        "failures": len(self.dna.failures),
                    },
                    source="genesis",
                ))
                
        except Exception as e:
            logger.error(f"Fatal error in life loop: {e}")
            raise
        finally:
            self._shutdown()
    
    def _shutdown(self) -> None:
        """Graceful shutdown procedure."""
        logger.info("Initiating shutdown...")
        
        # Stop event bus
        bus.stop_worker(drain=True)
        
        # Save final DNA state
        self._save_dna()
        
        logger.info("Shutdown complete")
    
    def _save_dna(self) -> None:
        """Save DNA to disk."""
        self.dna_repo.save(self.dna)
    
    # ─── Callback Handlers ───────────────────────────────────────────
    
    def _handle_assimilation_failure(
        self,
        module_name: str,
        error_type: str,
        error_message: str,
    ) -> None:
        """Handle failure reports from the Assimilator."""
        failure_type = FailureType.RUNTIME
        if error_type == "import":
            failure_type = FailureType.IMPORT
        elif error_type == "validation":
            failure_type = FailureType.VALIDATION
        
        self.dna.add_failure(module_name, failure_type, error_message)
        self.dna.mark_inactive(module_name)
        self._save_dna()
        
        # Emit event
        bus.publish(Event(
            event_type="organ.failed",
            data={"organ": module_name, "error": error_message},
            source="genesis",
        ))
        
        # Auto-Immune Response:
        # If this failure is happening to a freshly evolved organ, 
        # it might be fatal. Trigger revert if it's a validation or import error.
        if failure_type in [FailureType.VALIDATION, FailureType.IMPORT]:
             self.immunity.trigger_revert(module_name, error_message)
    
    def _handle_blueprint_request(self, module_name: str, description: str) -> None:
        """Handle blueprint requests from Immunity (for missing dependencies)."""
        self.dna.add_blueprint(module_name, description)
        self._save_dna()
        logger.info(f"Blueprint added: {module_name}")
    
    def _handle_failure_report(
        self,
        module_name: str,
        error_type: FailureType,
        message: str,
    ) -> None:
        """Handle failure reports from Immunity."""
        self.dna.add_failure(module_name, error_type, message)
        self._save_dna()
