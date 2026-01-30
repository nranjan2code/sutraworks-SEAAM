"""
SEAA Interactive REPL

The main interactive command loop with history, completion, and rich output.
"""

import os
import sys
from pathlib import Path
from typing import Optional, List

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style
from rich.console import Console

from seaa.core.logging import get_logger
from seaa.cli.commands import get_registry, Command
from seaa.cli.completers import create_completer
from seaa.cli.handlers import CommandContext, ExitREPL, set_context
from seaa.cli.runtime import GenesisRuntime, get_runtime
from seaa.cli.parsers.fuzzy import get_best_match, suggest_correction
from seaa.cli.parsers.natural import detect_intent, is_natural_query

logger = get_logger("cli.repl")

# Default history file location
DEFAULT_HISTORY_PATH = Path.home() / ".seaa_history"

# Prompt style
PROMPT_STYLE = Style.from_dict(
    {
        "prompt": "ansicyan bold",
        "indicator": "ansigreen",
        "indicator-stopped": "ansired",
    }
)


class REPL:
    """
    Interactive REPL for SEAA.

    Features:
    - Command history (persisted to file)
    - Tab completion
    - Fuzzy matching for typos
    - Natural language recognition
    - Rich output formatting
    """

    def __init__(
        self,
        history_path: Optional[Path] = None,
        runtime: Optional[GenesisRuntime] = None,
    ):
        """
        Initialize the REPL.

        Args:
            history_path: Path to history file (default: ~/.seaa_history)
            runtime: Genesis runtime manager (created if not provided)
        """
        self.console = Console()
        self.runtime = runtime or get_runtime()
        self.history_path = history_path or DEFAULT_HISTORY_PATH

        # Create command context
        self.context = CommandContext(
            console=self.console,
            runtime=self.runtime,
            args=[],
        )
        set_context(self.context)

        # Setup prompt session
        self.session = PromptSession(
            history=FileHistory(str(self.history_path)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=create_completer(),
            style=PROMPT_STYLE,
            enable_history_search=True,
        )

        self._running = False

    def _get_prompt(self) -> str:
        """Generate the prompt string."""
        from seaa.kernel.identity import get_identity

        try:
            identity = get_identity()
            name = identity.name
        except Exception:
            name = "SEAA"

        # Status indicator
        if self.runtime.is_running():
            indicator = "\033[92m●\033[0m"  # Green
        else:
            indicator = "\033[91m●\033[0m"  # Red

        return f"{indicator} {name} > "

    def _parse_input(self, text: str) -> tuple:
        """
        Parse user input into command and arguments.

        Returns:
            (command_name, args_list) or (None, []) if no valid command
        """
        text = text.strip()
        if not text:
            return (None, [])

        # Check for natural language first
        if is_natural_query(text):
            intent = detect_intent(text)
            if intent:
                return (intent, [])

        # Split into command and args
        parts = text.split()
        cmd_input = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        # Try exact match (including aliases)
        registry = get_registry()
        cmd = registry.get(cmd_input)
        if cmd:
            return (cmd.name, args)

        # Try natural language on just the first word
        intent = detect_intent(cmd_input)
        if intent:
            return (intent, args)

        # Try fuzzy match
        all_names = registry.get_all_names_and_aliases()
        match = get_best_match(cmd_input, all_names, threshold=0.6)
        if match:
            suggested_name, score = match

            # If very close match, auto-correct
            if score >= 0.8:
                # Resolve alias to command name
                cmd = registry.get(suggested_name)
                if cmd:
                    self.console.print(
                        f"[dim]Auto-corrected: {cmd_input} -> {cmd.name}[/dim]"
                    )
                    return (cmd.name, args)

            # Lower confidence - ask for confirmation
            elif score >= 0.6:
                cmd = registry.get(suggested_name)
                if cmd:
                    self.console.print(
                        f"[yellow]Did you mean '{cmd.name}'? (y/n)[/yellow]",
                        end=" ",
                    )
                    try:
                        response = input().strip().lower()
                        if response in ("y", "yes", ""):
                            return (cmd.name, args)
                    except (EOFError, KeyboardInterrupt):
                        pass

        # No match found
        suggestion = suggest_correction(cmd_input, all_names, threshold=0.5)
        if suggestion:
            self.console.print(
                f"[red]Unknown command: {cmd_input}[/red] "
                f"[dim](Did you mean '{suggestion}'?)[/dim]"
            )
        else:
            self.console.print(f"[red]Unknown command: {cmd_input}[/red]")

        return (None, [])

    def _execute_command(self, cmd_name: str, args: List[str]) -> None:
        """Execute a command by name."""
        registry = get_registry()
        cmd = registry.get(cmd_name)

        if not cmd:
            self.console.print(f"[red]Command not found: {cmd_name}[/red]")
            return

        # Check if Genesis is required
        if cmd.requires_genesis and not self.runtime.is_running():
            self.console.print(
                f"[yellow]'{cmd_name}' requires Genesis to be running. "
                "Use 'start' first.[/yellow]"
            )
            return

        # Update context with args
        self.context.args = args

        try:
            cmd.handler(self.context)
        except ExitREPL:
            raise
        except KeyboardInterrupt:
            self.console.print("[dim]Interrupted[/dim]")
        except Exception as e:
            logger.exception(f"Command error: {e}")
            self.console.print(f"[red]Error: {e}[/red]")

    def _print_welcome(self) -> None:
        """Print welcome message."""
        from seaa.kernel.identity import get_identity

        try:
            identity = get_identity()
            name = identity.name
            short_id = identity.short_id()
        except Exception:
            name = "SEAA"
            short_id = "unknown"

        self.console.print()
        self.console.print(f"[bold cyan]SEAA Interactive Shell[/bold cyan]")
        self.console.print(f"[dim]Instance: {name} ({short_id})[/dim]")
        self.console.print()
        self.console.print("[dim]Type 'help' for commands, 'exit' to quit.[/dim]")
        self.console.print(
            "[dim]Natural language works too: try 'how are you?'[/dim]"
        )
        self.console.print()

    def run(self) -> None:
        """Run the REPL loop."""
        self._running = True
        self._print_welcome()

        while self._running:
            try:
                # Get input
                text = self.session.prompt(self._get_prompt())

                # Parse and execute
                cmd_name, args = self._parse_input(text)
                if cmd_name:
                    self._execute_command(cmd_name, args)

            except KeyboardInterrupt:
                self.console.print()  # New line after ^C
                continue

            except EOFError:
                # Ctrl+D
                break

            except ExitREPL:
                break

            except Exception as e:
                logger.exception(f"REPL error: {e}")
                self.console.print(f"[red]Error: {e}[/red]")

        # Cleanup
        self._shutdown()

    def _shutdown(self) -> None:
        """Shutdown the REPL."""
        self._running = False

        # Stop Genesis if running
        if self.runtime.is_running():
            self.console.print("[dim]Stopping Genesis...[/dim]")
            self.runtime.stop()

        self.console.print("[dim]Goodbye![/dim]")


def run_interactive(
    history_path: Optional[Path] = None,
    auto_start_genesis: bool = False,
) -> None:
    """
    Run the interactive REPL.

    Args:
        history_path: Path to history file
        auto_start_genesis: If True, start Genesis automatically
    """
    # Suppress logging for clean REPL output
    from seaa.core.logging import setup_logging

    setup_logging(level="WARNING", format_type="colored")

    runtime = get_runtime()

    if auto_start_genesis:
        runtime.start()

    repl = REPL(history_path=history_path, runtime=runtime)
    repl.run()
