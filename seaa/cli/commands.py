"""
SEAA CLI Command Registry

Defines all available commands with their handlers, aliases, and natural language triggers.
"""

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any
import threading

from seaa.core.logging import get_logger

logger = get_logger("cli.commands")


@dataclass
class Command:
    """
    A CLI command definition.

    Attributes:
        name: Primary command name
        handler: Function to execute
        description: Help text
        aliases: Short names (e.g., 's' for 'status')
        natural_triggers: Phrases that map to this command
        category: Command grouping for help display
        requires_genesis: Whether Genesis must be running
    """

    name: str
    handler: Callable[..., Any]
    description: str
    aliases: List[str] = field(default_factory=list)
    natural_triggers: List[str] = field(default_factory=list)
    category: str = "general"
    requires_genesis: bool = False

    def matches(self, input_text: str) -> bool:
        """Check if input exactly matches this command or its aliases."""
        input_lower = input_text.lower().strip()
        if input_lower == self.name:
            return True
        return input_lower in self.aliases


class CommandRegistry:
    """
    Central registry for all CLI commands.

    Thread-safe singleton that manages command lookup,
    alias resolution, and natural language matching.
    """

    _instance: Optional["CommandRegistry"] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._commands: Dict[str, Command] = {}
        self._alias_map: Dict[str, str] = {}  # alias -> command name
        self._natural_map: Dict[str, str] = {}  # trigger -> command name
        self._initialized = True

    def register(self, command: Command) -> None:
        """Register a command."""
        self._commands[command.name] = command

        # Build alias map
        for alias in command.aliases:
            self._alias_map[alias.lower()] = command.name

        # Build natural language map
        for trigger in command.natural_triggers:
            self._natural_map[trigger.lower()] = command.name

        logger.debug(f"Registered command: {command.name}")

    def get(self, name: str) -> Optional[Command]:
        """Get command by name or alias."""
        name_lower = name.lower().strip()

        # Direct match
        if name_lower in self._commands:
            return self._commands[name_lower]

        # Alias match
        if name_lower in self._alias_map:
            return self._commands[self._alias_map[name_lower]]

        return None

    def get_all(self) -> List[Command]:
        """Get all registered commands."""
        return list(self._commands.values())

    def get_command_names(self) -> List[str]:
        """Get all command names (for completion)."""
        return list(self._commands.keys())

    def get_all_names_and_aliases(self) -> List[str]:
        """Get all command names and aliases (for completion)."""
        result = list(self._commands.keys())
        result.extend(self._alias_map.keys())
        return result

    def match_natural(self, text: str) -> Optional[Command]:
        """
        Match natural language input to a command.

        Checks if the input contains any registered natural triggers.
        """
        text_lower = text.lower().strip()

        # Direct trigger match
        if text_lower in self._natural_map:
            return self._commands[self._natural_map[text_lower]]

        # Partial match - check if any trigger is contained in text
        for trigger, cmd_name in self._natural_map.items():
            if trigger in text_lower:
                return self._commands[cmd_name]

        return None

    def get_by_category(self) -> Dict[str, List[Command]]:
        """Get commands grouped by category."""
        result: Dict[str, List[Command]] = {}
        for cmd in self._commands.values():
            if cmd.category not in result:
                result[cmd.category] = []
            result[cmd.category].append(cmd)
        return result

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton (for testing)."""
        with cls._lock:
            if cls._instance:
                cls._instance._commands.clear()
                cls._instance._alias_map.clear()
                cls._instance._natural_map.clear()
                cls._instance._initialized = False
            cls._instance = None


# Module-level singleton access
_registry: Optional[CommandRegistry] = None
_registry_lock = threading.Lock()


def get_registry() -> CommandRegistry:
    """Get the command registry singleton."""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = CommandRegistry()
                _register_default_commands(_registry)
    return _registry


def _register_default_commands(registry: CommandRegistry) -> None:
    """Register all default SEAA commands."""
    from seaa.cli import handlers

    # Status command
    registry.register(
        Command(
            name="status",
            handler=handlers.cmd_status,
            description="Show system health and vitals",
            aliases=["s"],
            natural_triggers=["how are you", "how's it going", "what's up", "health"],
            category="observation",
        )
    )

    # Organs command
    registry.register(
        Command(
            name="organs",
            handler=handlers.cmd_organs,
            description="List all organs with health status",
            aliases=["o", "list"],
            natural_triggers=["show organs", "list organs", "what organs"],
            category="observation",
        )
    )

    # Goals command
    registry.register(
        Command(
            name="goals",
            handler=handlers.cmd_goals,
            description="Show goals and satisfaction progress",
            aliases=["g"],
            natural_triggers=["progress", "show goals", "what goals", "objectives"],
            category="observation",
        )
    )

    # Failures command
    registry.register(
        Command(
            name="failures",
            handler=handlers.cmd_failures,
            description="Show failure records and circuit breakers",
            aliases=["f", "errors"],
            natural_triggers=["show failures", "what failed", "errors"],
            category="observation",
        )
    )

    # Dashboard command
    registry.register(
        Command(
            name="dashboard",
            handler=handlers.cmd_dashboard,
            description="Live full-screen dashboard",
            aliases=["d", "dash"],
            natural_triggers=["dashboard", "live view", "show dashboard"],
            category="observation",
        )
    )

    # Watch command
    registry.register(
        Command(
            name="watch",
            handler=handlers.cmd_watch,
            description="Stream events in real-time",
            aliases=["w"],
            natural_triggers=["stream", "watch events", "show events"],
            category="observation",
        )
    )

    # Timeline command
    registry.register(
        Command(
            name="timeline",
            handler=handlers.cmd_timeline,
            description="Show evolution timeline",
            aliases=["t", "history"],
            natural_triggers=["timeline", "history", "evolution history"],
            category="observation",
        )
    )

    # Identity command
    registry.register(
        Command(
            name="identity",
            handler=handlers.cmd_identity,
            description="Show or set instance identity",
            aliases=["id", "who"],
            natural_triggers=["who are you", "what's your name", "identity"],
            category="identity",
        )
    )

    # Evolve command
    registry.register(
        Command(
            name="evolve",
            handler=handlers.cmd_evolve,
            description="Trigger evolution cycle",
            aliases=["e", "grow"],
            natural_triggers=["evolve", "grow", "adapt"],
            category="control",
            requires_genesis=True,
        )
    )

    # Start command
    registry.register(
        Command(
            name="start",
            handler=handlers.cmd_start,
            description="Start Genesis in background",
            aliases=["run", "awaken"],
            natural_triggers=["awaken", "wake up", "start up"],
            category="control",
        )
    )

    # Stop command
    registry.register(
        Command(
            name="stop",
            handler=handlers.cmd_stop,
            description="Stop Genesis gracefully",
            aliases=["kill", "sleep"],
            natural_triggers=["sleep", "shut down", "stop running"],
            category="control",
        )
    )

    # Help command
    registry.register(
        Command(
            name="help",
            handler=handlers.cmd_help,
            description="Show available commands",
            aliases=["?", "commands"],
            natural_triggers=["help", "what can you do"],
            category="general",
        )
    )

    # Clear command
    registry.register(
        Command(
            name="clear",
            handler=handlers.cmd_clear,
            description="Clear the screen",
            aliases=["cls"],
            natural_triggers=[],
            category="general",
        )
    )

    # Exit command
    registry.register(
        Command(
            name="exit",
            handler=handlers.cmd_exit,
            description="Exit the REPL",
            aliases=["q", "quit", "bye"],
            natural_triggers=["bye", "goodbye", "see you"],
            category="general",
        )
    )
