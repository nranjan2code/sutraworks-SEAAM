"""
SEAA CLI Tab Completion

Provides intelligent tab completion for the interactive REPL.
"""

from typing import Iterable, List, Optional

from prompt_toolkit.completion import (
    Completer,
    Completion,
    WordCompleter,
)
from prompt_toolkit.document import Document

from seaa.core.logging import get_logger

logger = get_logger("cli.completers")


class SEAACompleter(Completer):
    """
    Smart completer for SEAA CLI.

    Features:
    - Command name completion
    - Alias completion
    - Argument completion (e.g., --json, --all)
    - Organ name completion for relevant commands
    """

    def __init__(self):
        self._command_names: List[str] = []
        self._command_aliases: List[str] = []
        self._all_commands: List[str] = []

        # Common arguments per command
        self._command_args = {
            "status": ["--json"],
            "organs": ["--json", "--all"],
            "goals": ["--json"],
            "failures": ["--json"],
            "timeline": ["--json", "--limit"],
            "identity": ["--json", "--name"],
            "watch": ["--poll", "--interval"],
        }

        # Global arguments (available for all commands)
        self._global_args = ["--help"]

        self._load_commands()

    def _load_commands(self) -> None:
        """Load command names from registry."""
        try:
            from seaa.cli.commands import get_registry

            registry = get_registry()

            self._command_names = registry.get_command_names()
            self._all_commands = registry.get_all_names_and_aliases()

            # Build alias list
            self._command_aliases = [
                name for name in self._all_commands if name not in self._command_names
            ]

            logger.debug(f"Loaded {len(self._all_commands)} completions")
        except Exception as e:
            logger.warning(f"Failed to load commands: {e}")
            # Fallback
            self._command_names = [
                "status",
                "organs",
                "goals",
                "failures",
                "dashboard",
                "watch",
                "timeline",
                "identity",
                "evolve",
                "start",
                "stop",
                "help",
                "clear",
                "exit",
            ]
            self._all_commands = self._command_names.copy()

    def get_completions(
        self, document: Document, complete_event
    ) -> Iterable[Completion]:
        """
        Generate completions for current input.

        Args:
            document: Current document
            complete_event: Completion event

        Yields:
            Completion objects
        """
        text = document.text_before_cursor.lstrip()
        word = document.get_word_before_cursor()

        # Empty or single word - complete commands
        if " " not in text:
            yield from self._complete_command(word)
            return

        # Multiple words - complete arguments
        parts = text.split()
        command = parts[0].lower()

        # Check if completing an argument
        if word.startswith("-"):
            yield from self._complete_argument(command, word)
        else:
            # Context-specific completion (organ names, etc.)
            yield from self._complete_context(command, word, parts)

    def _complete_command(self, prefix: str) -> Iterable[Completion]:
        """Complete command names."""
        prefix_lower = prefix.lower()

        for cmd in self._command_names:
            if cmd.startswith(prefix_lower):
                yield Completion(
                    cmd,
                    start_position=-len(prefix),
                    display_meta="command",
                )

        # Also suggest aliases (with lower priority)
        for alias in self._command_aliases:
            if alias.startswith(prefix_lower):
                yield Completion(
                    alias,
                    start_position=-len(prefix),
                    display_meta="alias",
                )

    def _complete_argument(self, command: str, prefix: str) -> Iterable[Completion]:
        """Complete command arguments."""
        # Get command-specific args
        args = self._command_args.get(command, [])
        args = args + self._global_args

        prefix_lower = prefix.lower()

        for arg in args:
            if arg.startswith(prefix_lower):
                yield Completion(
                    arg,
                    start_position=-len(prefix),
                    display_meta="option",
                )

    def _complete_context(
        self, command: str, word: str, parts: List[str]
    ) -> Iterable[Completion]:
        """Complete based on command context."""
        # Organ name completion for relevant commands
        if command in ["watch", "timeline"]:
            yield from self._complete_organ_pattern(word)

        # Value completion after specific args
        if len(parts) >= 2:
            last_arg = parts[-2] if parts[-1] == word else parts[-1]

            if last_arg == "--limit":
                # Suggest common limits
                for limit in ["10", "20", "50", "100"]:
                    if limit.startswith(word):
                        yield Completion(
                            limit,
                            start_position=-len(word),
                            display_meta="limit",
                        )

            elif last_arg == "--interval":
                # Suggest common intervals
                for interval in ["1.0", "2.0", "5.0", "10.0"]:
                    if interval.startswith(word):
                        yield Completion(
                            interval,
                            start_position=-len(word),
                            display_meta="seconds",
                        )

    def _complete_organ_pattern(self, prefix: str) -> Iterable[Completion]:
        """Complete organ name patterns."""
        try:
            from seaa.kernel.observer import get_observer

            observer = get_observer()
            organs = observer.get_organs()

            prefix_lower = prefix.lower()

            for organ in organs:
                if organ.name.lower().startswith(prefix_lower):
                    yield Completion(
                        organ.name,
                        start_position=-len(prefix),
                        display_meta="organ",
                    )

            # Also suggest common patterns
            patterns = ["soma.*", "soma.perception.*", "soma.memory.*", "soma.interface.*"]
            for pattern in patterns:
                if pattern.startswith(prefix_lower):
                    yield Completion(
                        pattern,
                        start_position=-len(prefix),
                        display_meta="pattern",
                    )

        except Exception:
            pass


def create_completer() -> SEAACompleter:
    """Create a new SEAA completer instance."""
    return SEAACompleter()
