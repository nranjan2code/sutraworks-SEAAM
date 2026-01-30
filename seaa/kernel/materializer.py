"""
SEAA Materializer

Responsible for writing generated code to the filesystem.

Single Responsibility:
- Convert module names to file paths
- Create directory structure with proper __init__.py files
- Atomic file writes
- Kernel protection enforcement
"""

import os
import re
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Optional, Union, List

from seaa.core.logging import get_logger
from seaa.core.config import config
from seaa.core.exceptions import (
    MaterializationError,
    KernelProtectionError,
)

# Security: Strict module name pattern - only valid Python identifiers under soma.*
MODULE_NAME_PATTERN = re.compile(r'^soma(\.[a-z_][a-z0-9_]*)+$', re.IGNORECASE)

logger = get_logger("materializer")


class Materializer:
    """
    The Materializer writes generated organ code to the filesystem.
    
    It enforces:
    - Kernel protection (cannot overwrite seaa.* modules)
    - Proper package structure (creates __init__.py files)
    - Atomic writes (prevents partial file corruption)
    """
    
    def __init__(self, root_dir: Optional[Union[Path, str]] = None):
        """
        Args:
            root_dir: Root directory for soma organs (default: from config)
        """
        self.root_dir = Path(root_dir) if root_dir else config.paths.root
        self.protected_prefixes = list(config.security.protected_prefixes)
    
    def materialize(self, module_name: str, code: str) -> Path:
        """
        Write code to the filesystem.

        Args:
            module_name: Fully qualified module name (e.g., 'soma.perception.observer')
            code: Python source code to write

        Returns:
            Path to the created file

        Raises:
            KernelProtectionError: If attempting to modify protected kernel
            MaterializationError: If write fails or module name is invalid

        SECURITY: Validates module name format and prevents path traversal.
        """
        # Step 1: Validate module name format (prevents path traversal)
        self._validate_module_name(module_name)

        # Step 2: Validate not protected
        self._check_protection(module_name)

        # Step 3: Ensure soma prefix (redundant with validation, but explicit)
        if not module_name.startswith("soma."):
            raise MaterializationError(
                f"Organ '{module_name}' must have 'soma.' prefix",
                context={"module": module_name}
            )

        # Step 4: Convert to path (includes path traversal check)
        file_path = self._module_to_path(module_name)

        # Step 5: Create directory structure
        self._ensure_package_structure(file_path.parent)

        # Step 6: Atomic write
        self._atomic_write(file_path, code)
        
        logger.info(f"✓ Materialized: {module_name} -> {file_path}")
        return file_path
    
    def _check_protection(self, module_name: str) -> None:
        """
        Ensure module name doesn't conflict with protected kernel.
        """
        for prefix in self.protected_prefixes:
            if module_name.startswith(prefix):
                raise KernelProtectionError(module_name)

    def _validate_module_name(self, module_name: str) -> None:
        """
        SECURITY: Validate module name format to prevent path traversal.

        Raises:
            MaterializationError: If module name is invalid or malicious
        """
        if not module_name or not isinstance(module_name, str):
            raise MaterializationError(
                "Invalid module name: must be non-empty string",
                context={"module": str(module_name)}
            )

        # Check against strict pattern: soma.valid_identifier.valid_identifier...
        if not MODULE_NAME_PATTERN.match(module_name):
            raise MaterializationError(
                f"Invalid module name format: '{module_name}'. "
                "Must match pattern 'soma.<identifier>.<identifier>...' "
                "where identifiers contain only letters, digits, and underscores.",
                context={"module": module_name, "pattern": MODULE_NAME_PATTERN.pattern}
            )

        # Additional check: no consecutive dots (path traversal attempt)
        if ".." in module_name:
            raise MaterializationError(
                f"Path traversal detected in module name: '{module_name}'",
                context={"module": module_name}
            )

        # Check each part is a valid Python identifier
        parts = module_name.split(".")
        for part in parts:
            if not part or not part.replace("_", "").replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").isalpha():
                # More thorough check using Python's own validation
                if not part.isidentifier():
                    raise MaterializationError(
                        f"Invalid identifier '{part}' in module name: '{module_name}'",
                        context={"module": module_name, "invalid_part": part}
                    )

    def _module_to_path(self, module_name: str) -> Path:
        """
        Convert module name to file path.

        SECURITY: Validates module name and ensures path stays within root_dir.

        Example: 'soma.perception.observer' -> './soma/perception/observer.py'

        Raises:
            MaterializationError: If path escapes root directory
        """
        # Step 1: Validate module name format
        self._validate_module_name(module_name)

        parts = module_name.split(".")
        # parts = ['soma', 'perception', 'observer']

        # Build path: root / soma / perception / observer.py
        path = self.root_dir
        for part in parts[:-1]:  # All but last
            path = path / part

        file_name = parts[-1] + ".py"
        final_path = path / file_name

        # SECURITY: Resolve to absolute path and verify it's under root_dir
        resolved_path = final_path.resolve()
        resolved_root = self.root_dir.resolve()

        # Ensure the resolved path starts with the root directory
        try:
            resolved_path.relative_to(resolved_root)
        except ValueError:
            raise MaterializationError(
                f"Path traversal detected: '{module_name}' resolves outside root directory",
                context={
                    "module": module_name,
                    "resolved_path": str(resolved_path),
                    "root_dir": str(resolved_root)
                }
            )

        return final_path
    
    def _ensure_package_structure(self, directory: Path) -> None:
        """
        Create directory and all parent __init__.py files.
        """
        # Create directory
        directory.mkdir(parents=True, exist_ok=True)
        
        # Walk up from the directory, creating __init__.py in each
        # Stop at root_dir or when we hit an existing __init__.py chain
        current = directory
        while current != self.root_dir.parent:
            init_file = current / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f"# SEAA auto-generated package: {current.name}\n")
                logger.debug(f"Created package: {init_file}")
            current = current.parent
            if current == self.root_dir.parent:
                break
    
    def _atomic_write(self, path: Path, content: str) -> None:
        """
        Write file atomically (write to temp, then rename).
        
        This prevents partial writes from corrupting files.
        """
        # Write to temp file in same directory (for same-filesystem atomic rename)
        temp_path = path.with_suffix(".tmp")
        try:
            with open(temp_path, "w") as f:
                f.write(content)
            
            # Atomic rename
            temp_path.rename(path)
            
        except Exception as e:
            # Clean up temp file on failure
            if temp_path.exists():
                temp_path.unlink()
            raise MaterializationError(
                f"Failed to write {path}: {e}",
                context={"path": str(path), "error": str(e)}
            )
    
    def exists(self, module_name: str) -> bool:
        """Check if an organ file exists on disk."""
        try:
            # _module_to_path includes security validation
            path = self._module_to_path(module_name)
            return path.exists()
        except (MaterializationError, KernelProtectionError):
            # Invalid or protected module names return False
            return False
        except Exception:
            return False

    def delete(self, module_name: str) -> bool:
        """
        Delete an organ file.

        Note: Does NOT remove empty parent directories.
        SECURITY: Validates module name before deletion.
        """
        self._check_protection(module_name)

        # _module_to_path includes path traversal protection
        path = self._module_to_path(module_name)
        if path.exists():
            path.unlink()
            logger.info(f"Deleted organ: {module_name}")
            return True
        return False

    def read(self, module_name: str) -> Optional[str]:
        """
        Read the source code of an organ.

        Useful for self-reflection and debugging.
        SECURITY: Validates module name before reading.
        """
        try:
            # _module_to_path includes security validation
            path = self._module_to_path(module_name)
            if path.exists():
                return path.read_text()
        except (MaterializationError, KernelProtectionError):
            # Invalid or protected module names return None
            logger.warning(f"Attempted to read invalid/protected module: {module_name}")
        return None
    
    def list_organs(self) -> List[str]:
        """
        List all materialized organs.
        
        Walks the soma directory and returns module names.
        """
        soma_dir = self.root_dir / "soma"
        if not soma_dir.exists():
            return []
        
        organs = []
        for py_file in soma_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            # Convert path back to module name
            relative = py_file.relative_to(self.root_dir)
            # PosixPath('soma/perception/observer.py') -> 'soma.perception.observer'
            module_name = str(relative.with_suffix("")).replace(os.sep, ".")
            organs.append(module_name)
        
        return organs
