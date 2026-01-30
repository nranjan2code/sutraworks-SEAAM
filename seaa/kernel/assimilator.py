"""
SEAA Assimilator

Responsible for dynamically loading and activating evolved organs.

Single Responsibility:
- Import modules dynamically
- Validate module structure (start() function)
- Spawn threads for organ activation
- Track running organs
"""

import importlib
import importlib.util
import inspect
import sys
import threading
from typing import Callable, Any, Optional, Dict, List

from seaa.core.logging import get_logger
from seaa.core.exceptions import (
    ImportFailedError,
    ValidationFailedError,
    ActivationFailedError,
)

logger = get_logger("assimilator")


class OrganThread(threading.Thread):
    """
    A supervised thread for running an organ.
    
    Captures exceptions and reports them back.
    """
    
    def __init__(
        self,
        module_name: str,
        start_func: Callable[[], None],
        on_error: Optional[Callable[[str, Exception], None]] = None,
    ):
        super().__init__(name=f"organ-{module_name}", daemon=True)
        self.module_name = module_name
        self.start_func = start_func
        self.on_error = on_error
        self.exception: Optional[Exception] = None
    
    def run(self):
        try:
            logger.debug(f"Starting organ: {self.module_name}")
            self.start_func()
        except Exception as e:
            self.exception = e
            logger.error(f"Organ {self.module_name} crashed: {e}")
            if self.on_error:
                self.on_error(self.module_name, e)


class Assimilator:
    """
    The Assimilator integrates evolved organs into the running system.
    
    It handles:
    - Dynamic module import
    - Signature validation
    - Thread-based activation
    - Running organ tracking
    """
    
    def __init__(self, on_failure: Optional[Callable[[str, str, str], None]] = None):
        """
        Args:
            on_failure: Callback(module_name, error_type, error_message) when organ fails
        """
        self.running_organs: Dict[str, OrganThread] = {}
        self.on_failure = on_failure
        self._lock = threading.Lock()
    
    def is_running(self, module_name: str) -> bool:
        """Check if an organ is already running."""
        return module_name in self.running_organs
    
    def get_running_organs(self) -> List[str]:
        """Get list of all running organ names."""
        return list(self.running_organs.keys())
    
    def integrate(self, module_name: str) -> bool:
        """
        Integrate an organ into the running system.
        
        Steps:
        1. Import the module
        2. Validate it has a start() function
        3. Validate start() signature (zero args)
        4. Spawn a thread to run it
        
        Args:
            module_name: Fully qualified module name (e.g., 'soma.perception.observer')
        
        Returns:
            True if successfully integrated, False otherwise
        """
        with self._lock:
            # Check if already running
            if module_name in self.running_organs:
                logger.debug(f"Organ {module_name} already running, skipping")
                return True
            
            try:
                # Step 1: Import
                module = self._import_module(module_name)
                
                # Step 2: Validate start() exists
                if not hasattr(module, "start"):
                    raise ValidationFailedError(
                        module_name,
                        "Missing global start() function"
                    )
                
                start_func = getattr(module, "start")
                
                # Step 3: Validate signature
                if not callable(start_func):
                    raise ValidationFailedError(
                        module_name,
                        "start is not a callable function"
                    )
                
                sig = inspect.signature(start_func)
                required_params = [
                    p for p in sig.parameters.values()
                    if p.default == inspect.Parameter.empty
                ]
                
                if len(required_params) > 0:
                    raise ValidationFailedError(
                        module_name,
                        f"start() requires arguments: {[p.name for p in required_params]}. Must be zero-args."
                    )
                
                # Step 4: Spawn thread
                thread = OrganThread(
                    module_name=module_name,
                    start_func=start_func,
                    on_error=self._handle_organ_error,
                )
                thread.start()
                
                self.running_organs[module_name] = thread
                logger.info(f"✓ Integrated organ: {module_name}")
                return True
                
            except ImportError as e:
                logger.error(f"Failed to import {module_name}: {e}")
                self._report_failure(module_name, "import", str(e))
                raise ImportFailedError(module_name, e)
                
            except ValidationFailedError as e:
                logger.error(f"Validation failed for {module_name}: {e.reason}")
                self._report_failure(module_name, "validation", e.reason)
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error integrating {module_name}: {e}")
                self._report_failure(module_name, "runtime", str(e))
                raise ActivationFailedError(module_name, e)
    
    def _import_module(self, module_name: str) -> Any:
        """
        Import a module by name, with proper cache invalidation.
        """
        # Invalidate cache for hot-reload support
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # Also clear parent packages to ensure fresh import
        parts = module_name.split(".")
        for i in range(len(parts)):
            parent = ".".join(parts[:i+1])
            if parent in sys.modules:
                del sys.modules[parent]
        
        return importlib.import_module(module_name)
    
    def _handle_organ_error(self, module_name: str, error: Exception) -> None:
        """Handle runtime errors from running organs."""
        with self._lock:
            if module_name in self.running_organs:
                del self.running_organs[module_name]
        
        self._report_failure(module_name, "runtime", str(error))
    
    def _report_failure(self, module_name: str, error_type: str, message: str) -> None:
        """Report failure through callback if registered."""
        if self.on_failure:
            self.on_failure(module_name, error_type, message)
    
    def stop_organ(self, module_name: str) -> bool:
        """
        Request an organ to stop.
        
        Note: Since organs run in daemon threads, this just removes
        them from tracking. The thread will die with the main process.
        """
        with self._lock:
            if module_name in self.running_organs:
                del self.running_organs[module_name]
                logger.info(f"Stopped tracking organ: {module_name}")
                return True
        return False
    
    def get_organ_status(self, module_name: str) -> Dict[str, Any]:
        """Get status information for an organ."""
        with self._lock:
            if module_name not in self.running_organs:
                return {"status": "not_running", "module": module_name}
            
            thread = self.running_organs[module_name]
            return {
                "status": "running" if thread.is_alive() else "stopped",
                "module": module_name,
                "thread_name": thread.name,
                "exception": str(thread.exception) if thread.exception else None,
            }
    
    def integrate_batch(self, module_names: List[str]) -> Dict[str, bool]:
        """
        Integrate multiple organs, returning success status for each.
        """
        results = {}
        for module_name in module_names:
            try:
                results[module_name] = self.integrate(module_name)
            except Exception:
                results[module_name] = False
        return results
