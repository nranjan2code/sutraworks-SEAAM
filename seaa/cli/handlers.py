"""
SEAA CLI Command Handlers

Implementation of all CLI command handlers.
These are invoked by the command registry when commands are executed.
"""

from typing import Optional, List, TYPE_CHECKING

from rich.console import Console

from seaa.core.logging import get_logger
from seaa.kernel.observer import get_observer
from seaa.kernel.identity import get_identity

if TYPE_CHECKING:
    from seaa.cli.runtime import GenesisRuntime

logger = get_logger("cli.handlers")

# Rich console for output
console = Console()


class ExitREPL(Exception):
    """Raised to exit the REPL loop."""

    pass


class CommandContext:
    """
    Context passed to command handlers.

    Provides access to:
    - console: Rich console for output
    - runtime: Genesis runtime manager
    - args: Command arguments
    """

    def __init__(
        self,
        console: Console,
        runtime: Optional["GenesisRuntime"] = None,
        args: Optional[List[str]] = None,
    ):
        self.console = console
        self.runtime = runtime
        self.args = args or []

    def is_genesis_running(self) -> bool:
        """Check if Genesis is currently running."""
        return self.runtime is not None and self.runtime.is_running()


# Default context for standalone usage
_default_context: Optional[CommandContext] = None


def get_context() -> CommandContext:
    """Get current command context."""
    global _default_context
    if _default_context is None:
        _default_context = CommandContext(console=console)
    return _default_context


def set_context(ctx: CommandContext) -> None:
    """Set the current command context."""
    global _default_context
    _default_context = ctx


# =========================================
# Observation Commands
# =========================================


def cmd_status(ctx: Optional[CommandContext] = None) -> None:
    """Show system health and vitals."""
    ctx = ctx or get_context()

    from seaa.cli.ui.panels import render_status

    render_status(ctx.console, show_genesis_status=True, runtime=ctx.runtime)


def cmd_organs(ctx: Optional[CommandContext] = None) -> None:
    """List all organs with health status."""
    ctx = ctx or get_context()

    from seaa.cli.ui.tables import render_organs

    render_organs(ctx.console, show_all="--all" in ctx.args)


def cmd_goals(ctx: Optional[CommandContext] = None) -> None:
    """Show goals and satisfaction progress."""
    ctx = ctx or get_context()

    from seaa.cli.ui.tables import render_goals

    render_goals(ctx.console)


def cmd_failures(ctx: Optional[CommandContext] = None) -> None:
    """Show failure records and circuit breakers."""
    ctx = ctx or get_context()

    from seaa.cli.ui.tables import render_failures

    render_failures(ctx.console)


def cmd_dashboard(ctx: Optional[CommandContext] = None) -> None:
    """Launch live full-screen dashboard."""
    ctx = ctx or get_context()

    from seaa.cli.ui.dashboard import run_dashboard

    run_dashboard(ctx.console, runtime=ctx.runtime)


def cmd_watch(ctx: Optional[CommandContext] = None) -> None:
    """Stream events in real-time."""
    ctx = ctx or get_context()

    from seaa.cli.ui.dashboard import run_event_stream

    # Parse patterns from args
    patterns = None
    if ctx.args:
        patterns = [arg for arg in ctx.args if not arg.startswith("-")]

    run_event_stream(ctx.console, patterns=patterns)


def cmd_timeline(ctx: Optional[CommandContext] = None) -> None:
    """Show evolution timeline."""
    ctx = ctx or get_context()

    from seaa.cli.ui.tables import render_timeline

    # Parse limit from args
    limit = 20
    for i, arg in enumerate(ctx.args):
        if arg == "--limit" and i + 1 < len(ctx.args):
            try:
                limit = int(ctx.args[i + 1])
            except ValueError:
                pass

    render_timeline(ctx.console, limit=limit)


# =========================================
# Identity Commands
# =========================================


def cmd_identity(ctx: Optional[CommandContext] = None) -> None:
    """Show or set instance identity."""
    ctx = ctx or get_context()

    from seaa.kernel.identity import set_name
    from seaa.cli.ui.panels import render_identity

    # Check if setting name
    for i, arg in enumerate(ctx.args):
        if arg == "--name" and i + 1 < len(ctx.args):
            new_name = ctx.args[i + 1]
            identity = set_name(new_name)
            ctx.console.print(f"[green]Renamed to:[/green] {identity.name}")
            return

    # Just show identity
    render_identity(ctx.console)


# =========================================
# Control Commands
# =========================================


def cmd_evolve(ctx: Optional[CommandContext] = None) -> None:
    """Trigger an evolution cycle."""
    ctx = ctx or get_context()

    if not ctx.is_genesis_running():
        ctx.console.print("[yellow]Genesis is not running. Use 'start' first.[/yellow]")
        return

    ctx.console.print("[cyan]Triggering evolution cycle...[/cyan]")
    ctx.runtime.trigger_evolution()
    ctx.console.print("[green]Evolution cycle triggered.[/green]")


def cmd_start(ctx: Optional[CommandContext] = None) -> None:
    """Start Genesis in background."""
    ctx = ctx or get_context()

    if ctx.runtime is None:
        ctx.console.print("[red]Runtime not available.[/red]")
        return

    if ctx.is_genesis_running():
        ctx.console.print("[yellow]Genesis is already running.[/yellow]")
        return

    ctx.console.print("[cyan]Starting Genesis...[/cyan]")
    try:
        ctx.runtime.start()
        ctx.console.print("[green]Genesis awakened.[/green]")
    except Exception as e:
        ctx.console.print(f"[red]Failed to start: {e}[/red]")


def cmd_stop(ctx: Optional[CommandContext] = None) -> None:
    """Stop Genesis gracefully."""
    ctx = ctx or get_context()

    if ctx.runtime is None:
        ctx.console.print("[red]Runtime not available.[/red]")
        return

    if not ctx.is_genesis_running():
        ctx.console.print("[yellow]Genesis is not running.[/yellow]")
        return

    ctx.console.print("[cyan]Stopping Genesis...[/cyan]")
    try:
        ctx.runtime.stop()
        ctx.console.print("[green]Genesis asleep.[/green]")
    except Exception as e:
        ctx.console.print(f"[red]Failed to stop: {e}[/red]")


# =========================================
# General Commands
# =========================================


def cmd_help(ctx: Optional[CommandContext] = None) -> None:
    """Show available commands."""
    ctx = ctx or get_context()

    from rich.table import Table
    from seaa.cli.commands import get_registry

    registry = get_registry()
    by_category = registry.get_by_category()

    # Category order and display names
    categories = [
        ("observation", "Observation"),
        ("control", "Control"),
        ("identity", "Identity"),
        ("general", "General"),
    ]

    table = Table(
        title="SEAA Commands",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )
    table.add_column("Command", style="green")
    table.add_column("Aliases", style="dim")
    table.add_column("Description")

    for cat_key, cat_name in categories:
        if cat_key not in by_category:
            continue

        # Add category header
        table.add_row(f"[bold]{cat_name}[/bold]", "", "")

        for cmd in sorted(by_category[cat_key], key=lambda c: c.name):
            aliases = ", ".join(cmd.aliases) if cmd.aliases else "-"
            table.add_row(f"  {cmd.name}", aliases, cmd.description)

    ctx.console.print(table)
    ctx.console.print()
    ctx.console.print("[dim]Tip: Commands also respond to natural language.[/dim]")
    ctx.console.print('[dim]Try: "how are you?", "show organs", "wake up"[/dim]')


def cmd_clear(ctx: Optional[CommandContext] = None) -> None:
    """Clear the screen."""
    ctx = ctx or get_context()
    ctx.console.clear()


def cmd_exit(ctx: Optional[CommandContext] = None) -> None:
    """Exit the REPL."""
    raise ExitREPL()
