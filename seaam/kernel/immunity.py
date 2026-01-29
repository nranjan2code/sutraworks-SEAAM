"""
SEAAM Immunity System

Responsible for healing and error recovery.

Single Responsibility:
- Classify errors (internal vs external)
- Resolve missing dependencies
- Smart retry logic
- No hardcoded lists - uses pattern matching
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional, Union

from seaam.core.logging import get_logger
from seaam.core.config import config
from seaam.core.exceptions import (
    DependencyResolutionError,
    ImmunityError,
)
from seaam.dna.schema import FailureType

# Avoid circular import with type checking only if needed, 
# but here we pass the instance.
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from seaam.kernel.genealogy import Genealogy

logger = get_logger("immunity")


class DependencyClassification:
    """Result of classifying a missing dependency."""
    
    def __init__(
        self,
        package_name: str,
        is_internal: bool,
        is_seed: bool,
        suggested_soma_path: Optional[str] = None,
    ):
        self.package_name = package_name
        self.is_internal = is_internal  # Part of soma/ (evolved)
        self.is_seed = is_seed  # Part of seaam/ (immutable kernel)
        self.suggested_soma_path = suggested_soma_path


class Immunity:
    """
    The Immunity System handles error recovery and dependency resolution.
    
    Unlike the old implementation, this version:
    - Uses pattern matching instead of hardcoded lists
    - Has configurable pip install (disabled by default)
    - Cleanly separates classification from action
    - Can trigger metabolic revert (auto-rollback)
    """
    
    def __init__(
        self,
        root_dir: Optional[Union[Path, str]] = None,
        on_blueprint_needed: Optional[Callable[[str, str], None]] = None,
        on_failure_report: Optional[Callable[[str, FailureType, str], None]] = None,
        genealogy: Optional["Genealogy"] = None,
    ):
        """
        Args:
            root_dir: Project root directory
            on_blueprint_needed: Callback(module_name, description) when new blueprint is needed
            on_failure_report: Callback(module_name, error_type, message) to report failures
            genealogy: Optional Genealogy instance for rollback
        """
        self.root_dir = Path(root_dir) if root_dir else config.paths.root
        self.soma_dir = self.root_dir / "soma"
        self.seaam_dir = self.root_dir / "seaam"
        self.on_blueprint_needed = on_blueprint_needed
        self.on_failure_report = on_failure_report
        self.genealogy = genealogy
        
        # Security settings
        self.allow_pip_install = config.security.allow_pip_install
        self.allowed_packages = set(config.security.allowed_pip_packages)
    
    def trigger_revert(self, organ_name: str, reason: str) -> bool:
        """
        Trigger an auto-immune response to revert the last evolution.
        
        This is called when a critical failure occurs immediately after evolution,
        suggesting the new mutation is fatal (cancerous).
        """
        if not self.genealogy:
            logger.warning("Auto-immune response requested but no genealogy system attached.")
            return False
            
        logger.warning(f"🛡️ AUTO-IMMUNE RESPONSE TRIGGERED: {organ_name}")
        logger.warning(f"Reason: {reason}")
        
        # Report the failure first so DNA records it
        self._report_failure(
            organ_name,
            FailureType.RUNTIME,
            f"Auto-Reverted due to critical failure: {reason}"
        )
        
        # Execute rollback
        if self.genealogy.revert_last():
            logger.info("✓ System successfully reverted to previous healthy state.")
            return True
        else:
            logger.error("Failed to execute auto-revert.")
            return False

    def classify_dependency(self, package_name: str) -> DependencyClassification:
        """
        Classify a missing dependency.
        
        Determines if it's:
        - An internal soma organ (should be evolved)
        - A seed component (kernel error)
        - An external package (maybe pip installable)
        """
        # Check if it's explicitly a soma or seaam import
        if package_name.startswith("soma."):
            return DependencyClassification(
                package_name=package_name,
                is_internal=True,
                is_seed=False,
                suggested_soma_path=package_name,
            )
        
        if package_name.startswith("seaam."):
            # Check if this seed file actually exists
            parts = package_name.split(".")
            seed_path = self.seaam_dir.parent
            for part in parts:
                seed_path = seed_path / part
            
            # Check as directory or .py file
            if seed_path.exists() or (seed_path.with_suffix(".py")).exists():
                return DependencyClassification(
                    package_name=package_name,
                    is_internal=False,
                    is_seed=True,
                )
            else:
                # seaam.* that doesn't exist - likely a typo or hallucination
                return DependencyClassification(
                    package_name=package_name,
                    is_internal=False,
                    is_seed=True,  # Treat as seed error
                )
        
        # Check if it might be a soma subpackage without prefix
        # e.g., "perception.observer" when they meant "soma.perception.observer"
        root_pkg = package_name.split(".")[0]
        potential_soma_path = self.soma_dir / root_pkg
        if potential_soma_path.exists():
            return DependencyClassification(
                package_name=package_name,
                is_internal=True,
                is_seed=False,
                suggested_soma_path=f"soma.{package_name}",
            )
        
        # Check if it looks like an internal name (common organ-like names)
        # Instead of hardcoded list, use heuristics
        if self._looks_internal(package_name):
            return DependencyClassification(
                package_name=package_name,
                is_internal=True,
                is_seed=False,
                suggested_soma_path=f"soma.{package_name}",
            )
        
        # External package
        return DependencyClassification(
            package_name=package_name,
            is_internal=False,
            is_seed=False,
        )
    
    def _looks_internal(self, package_name: str) -> bool:
        """
        Heuristic to determine if a package name looks like an internal module.
        
        This replaces hardcoded hallucination lists with pattern matching.
        """
        # Short names without dots are likely internal hallucinations
        if "." not in package_name and len(package_name) < 20:
            # Check if it's a known stdlib or common package
            known_external = {
                "os", "sys", "json", "time", "datetime", "threading",
                "typing", "pathlib", "logging", "dataclasses", "enum",
                "requests", "flask", "streamlit", "watchdog", "sqlite3",
                "asyncio", "yaml", "re", "subprocess", "importlib",
            }
            if package_name.lower() in known_external:
                return False
            
            # Looks internal - probably a hallucination
            return True
        
        return False
    
    def heal(self, package_name: str) -> bool:
        """
        Attempt to heal a missing dependency.
        
        Args:
            package_name: The missing package/module name
        
        Returns:
            True if healing was attempted (may need reboot)
            False if cannot heal
        """
        classification = self.classify_dependency(package_name)
        
        if classification.is_seed:
            # Seed component error - cannot self-heal kernel issues
            logger.error(f"Seed component error: {package_name}")
            self._report_failure(
                package_name,
                FailureType.IMPORT,
                f"Import error in seed component. Check class/function names in {package_name}."
            )
            return False
        
        if classification.is_internal:
            # Internal soma organ - request blueprint
            return self._heal_internal(classification)
        
        # External package
        return self._heal_external(package_name)
    
    def _heal_internal(self, classification: DependencyClassification) -> bool:
        """Heal a missing internal organ by requesting its evolution."""
        target = classification.suggested_soma_path or classification.package_name
        
        logger.info(f"Requesting evolution of internal organ: {target}")
        
        # Ensure soma. prefix
        if not target.startswith("soma."):
            target = f"soma.{target}"
        
        description = (
            f"Critical system component required by other organs. "
            f"This organ was discovered as a missing dependency (original: {classification.package_name}). "
            f"Implement it with a global start() function."
        )
        
        if self.on_blueprint_needed:
            self.on_blueprint_needed(target, description)
            return True
        else:
            logger.warning("No blueprint callback registered, cannot request evolution")
            return False
    
    def _heal_external(self, package_name: str) -> bool:
        """Attempt to install an external package via pip."""
        
        # Security check
        if not self.allow_pip_install:
            logger.warning(
                f"Pip install disabled (security). "
                f"To enable, set security.allow_pip_install=true in config.yaml"
            )
            self._report_failure(
                package_name,
                FailureType.IMPORT,
                f"Missing external package '{package_name}'. Pip install is disabled for security."
            )
            return False
        
        # Allowlist check
        if package_name not in self.allowed_packages:
            logger.warning(
                f"Package '{package_name}' not in allowed list. "
                f"Add to security.allowed_pip_packages in config.yaml if safe."
            )
            self._report_failure(
                package_name,
                FailureType.IMPORT,
                f"Package '{package_name}' is not in the allowed pip packages list."
            )
            return False
        
        # Actually install
        logger.info(f"Installing allowed package: {package_name}")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            logger.info(f"✓ Installed: {package_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package_name}: {e}")
            self._report_failure(
                package_name,
                FailureType.IMPORT,
                f"Pip install failed: {e}"
            )
            return False
    
    def _report_failure(self, module_name: str, error_type: FailureType, message: str) -> None:
        """Report failure through callback if registered."""
        if self.on_failure_report:
            self.on_failure_report(module_name, error_type, message)
    
    def needs_reboot(self) -> bool:
        """
        Check if a system reboot is recommended.
        
        This is a cleaner alternative to os.execv() - the caller decides.
        """
        # Currently, we never require reboots - the assimilator handles hot-reload
        return False
    
    def request_reboot(self) -> None:
        """
        Request a system reboot.
        
        This replaces the old os.execv() approach with a cleaner signal.
        """
        logger.warning("System reboot requested. Please restart the process.")
        # In production, this could set a flag or send a signal
        # instead of the dangerous os.execv()
