"""
SEAAM Genealogy - Evolutionary Memory

Responsible for maintaining the history of the SOMA (body) using Git.
This allows the system to:
1. Recall previous states (Time Travel)
2. Revert failed mutations (Healing)
3. Analyze diffs between generations (Learning)

This module operates on a LOCAL git repository inside the soma/ directory,
completely isolated from the project's main version control.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Union

from seaam.core.logging import get_logger
from seaam.core.config import config

logger = get_logger("genealogy")


class Genealogy:
    """
    Manages the evolutionary history of the SOMA using a nested Git repository.
    """

    def __init__(self, soma_path: Optional[Union[Path, str]] = None):
        """
        Initialize the Genealogy manage.

        Args:
            soma_path: Path to the soma directory (default: from config)
        """
        self.soma_path = Path(soma_path) if soma_path else config.paths.soma
        self.enabled = config.genealogy.enabled
        
        # Ensure absolute path for safety
        self.soma_path = self.soma_path.resolve()

    def init_repo(self) -> bool:
        """
        Initialize the git repository if it doesn't exist.
        """
        if not self.enabled:
            return False

        git_dir = self.soma_path / ".git"
        if git_dir.exists():
            return True

        try:
            # Ensure directory exists
            self.soma_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("Initializing evolutionary memory (git)...")
            self._run_git(["init"])
            
            # Configure local user for this repo
            self._run_git(["config", "user.name", config.genealogy.user_name])
            self._run_git(["config", "user.email", config.genealogy.user_email])
            
            # create initial commit
            initial_file = self.soma_path / "README.md"
            if not initial_file.exists():
                initial_file.write_text("# SOMA - Evolved Organs\n\nThis directory contains the evolved body of the AI.")
            
            self._run_git(["add", "."])
            self._run_git(["commit", "-m", "Genesis: Initial Awakening"])
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize genealogy: {e}")
            return False

    def commit(self, message: str) -> bool:
        """
        Snapshot the current state of the SOMA.
        
        Args:
            message: Commit message describing the change
        """
        if not self.enabled:
            return False

        try:
            # Check if there are changes
            status = self._run_git(["status", "--porcelain"], capture_output=True)
            if not status.strip():
                # Nothing to commit
                return False

            self._run_git(["add", "."])
            self._run_git(["commit", "-m", message])
            logger.info(f"Evolution captured: {message}")
            return True
        except Exception as e:
            logger.error(f"Failed to commit evolution: {e}")
            return False

    def revert_last(self) -> bool:
        """
        Revert to the previous state (HEAD^).
        Used for immediate metabolic recovery.
        """
        if not self.enabled:
            return False
            
        try:
            logger.warning("REVERTING to previous evolutionary state...")
            self._run_git(["reset", "--hard", "HEAD^"])
            return True
        except Exception as e:
            logger.error(f"Failed to revert: {e}")
            return False

    def get_diff(self, generations: int = 1) -> str:
        """
        Get the diff between current HEAD and previous generations.
        Useful for the Architect to understand what changed.
        """
        if not self.enabled:
            return ""

        try:
            return self._run_git(["diff", f"HEAD~{generations}", "HEAD"], capture_output=True)
        except Exception:
            return ""

    def _run_git(self, args: List[str], capture_output: bool = False) -> str:
        """
        Execute a git command within the soma directory.
        """
        cmd = ["git"] + args
        
        # Run process
        result = subprocess.run(
            cmd,
            cwd=self.soma_path,
            check=True,
            capture_output=True, # Always capture to prevent leakage to stdout
            text=True
        )
        
        if capture_output:
            return result.stdout
        return ""
