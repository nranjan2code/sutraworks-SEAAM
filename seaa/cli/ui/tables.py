"""
SEAA CLI Table Components

Rich Table implementations for displaying organs, goals, failures, and timeline.
"""

from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from seaa.kernel.observer import get_observer
from seaa.kernel.protocols import OrganInfo, GoalInfo, FailureInfo, OrganHealth
from seaa.cli.ui.formatters import (
    health_indicator,
    active_indicator,
    format_timestamp,
    format_error_preview,
    truncate,
)


def create_organ_table(organs: List[OrganInfo], show_all: bool = False) -> Table:
    """
    Create a Rich Table for organs.

    Args:
        organs: List of organ info objects
        show_all: If False, filter out stopped organs without errors
    """
    table = Table(
        title="Organs",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        expand=True,
    )

    table.add_column("", width=3, justify="center")  # Status indicator
    table.add_column("Name", style="white", no_wrap=True)
    table.add_column("Health", width=10)
    table.add_column("Failures", width=8, justify="right")
    table.add_column("Error", style="dim")

    # Filter if needed
    if not show_all:
        organs = [o for o in organs if o.active or o.circuit_open or o.failure_count > 0]

    if not organs:
        table.add_row("", "[dim]No organs found[/dim]", "", "", "")
        return table

    for organ in sorted(organs, key=lambda o: (not o.active, o.name)):
        status = active_indicator(organ.active)
        health = health_indicator(organ.health)

        failures = str(organ.failure_count) if organ.failure_count > 0 else "-"

        error = ""
        if organ.last_error:
            error = format_error_preview(organ.last_error, 40)
        if organ.circuit_open:
            error = f"[red]CIRCUIT OPEN[/red] {error}"

        table.add_row(status, organ.name, health, failures, error)

    return table


def render_organs(console: Console, show_all: bool = False) -> None:
    """Render organs table to console."""
    observer = get_observer()
    organs = observer.get_organs()
    table = create_organ_table(organs, show_all=show_all)
    console.print(table)

    if not show_all:
        stopped_count = sum(1 for o in organs if not o.active and not o.circuit_open)
        if stopped_count > 0:
            console.print(f"[dim]({stopped_count} stopped organs hidden. Use --all to show.)[/dim]")


def create_goal_table(goals: List[GoalInfo]) -> Table:
    """
    Create a Rich Table for goals.

    Args:
        goals: List of goal info objects
    """
    table = Table(
        title="Goals",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        expand=True,
    )

    table.add_column("", width=3, justify="center")  # Status indicator
    table.add_column("P", width=3, justify="center")  # Priority
    table.add_column("Description", style="white")
    table.add_column("Required", style="dim")
    table.add_column("Matched", width=8, justify="right")

    if not goals:
        table.add_row("", "", "[dim]No goals defined[/dim]", "", "")
        return table

    for goal in sorted(goals, key=lambda g: (g.satisfied, g.priority)):
        status = "[green]✓[/green]" if goal.satisfied else "[dim]○[/dim]"
        priority = f"[cyan]{goal.priority}[/cyan]"

        required = ", ".join(goal.required_organs) if goal.required_organs else "-"
        required = truncate(required, 30)

        matched = str(len(goal.matching_organs)) if goal.matching_organs else "-"
        if goal.matching_organs:
            matched = f"[green]{matched}[/green]"

        table.add_row(status, priority, goal.description, required, matched)

    return table


def render_goals(console: Console) -> None:
    """Render goals table to console."""
    observer = get_observer()
    goals = observer.get_goals()
    table = create_goal_table(goals)
    console.print(table)

    # Summary
    satisfied = sum(1 for g in goals if g.satisfied)
    console.print(f"\n[dim]Progress: {satisfied}/{len(goals)} goals satisfied[/dim]")


def create_failure_table(failures: List[FailureInfo]) -> Table:
    """
    Create a Rich Table for failures.

    Args:
        failures: List of failure info objects
    """
    table = Table(
        title="Failures",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        expand=True,
    )

    table.add_column("", width=3, justify="center")  # Status indicator
    table.add_column("Module", style="white", no_wrap=True)
    table.add_column("Type", width=12)
    table.add_column("Attempts", width=8, justify="right")
    table.add_column("Message", style="dim")

    if not failures:
        table.add_row("", "[green]No failures recorded[/green]", "", "", "")
        return table

    for failure in failures:
        if failure.circuit_open:
            status = "[red]⊘[/red]"
        else:
            status = "[yellow]![/yellow]"

        error_type = failure.error_type
        attempts = str(failure.attempts)
        message = format_error_preview(failure.message, 40)

        table.add_row(status, failure.module, error_type, attempts, message)

    return table


def render_failures(console: Console) -> None:
    """Render failures table to console."""
    observer = get_observer()
    failures = observer.get_failures()
    table = create_failure_table(failures)
    console.print(table)

    # Summary
    circuit_open = sum(1 for f in failures if f.circuit_open)
    if circuit_open > 0:
        console.print(f"\n[red]{circuit_open} circuit breaker(s) open[/red]")


def create_timeline_table(events: List[dict], limit: int = 20) -> Table:
    """
    Create a Rich Table for evolution timeline.

    Args:
        events: List of timeline event dicts
        limit: Maximum events to show
    """
    table = Table(
        title="Evolution Timeline",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        expand=True,
    )

    table.add_column("", width=3, justify="center")  # Type indicator
    table.add_column("Time", width=19)
    table.add_column("Type", width=12)
    table.add_column("Organ", style="white")
    table.add_column("Details", style="dim")

    if not events:
        table.add_row("", "[dim]No evolution events yet[/dim]", "", "", "")
        return table

    # Type icons
    icons = {
        "integrated": "[green]↑[/green]",
        "designed": "[blue]◆[/blue]",
        "failure": "[red]✗[/red]",
    }

    for event in events[:limit]:
        event_type = event.get("type", "unknown")
        icon = icons.get(event_type, "•")

        timestamp = format_timestamp(event.get("timestamp"), include_date=True)
        organ = event.get("organ", "-")

        # Build details from available fields
        details = ""
        if event_type == "designed":
            details = truncate(event.get("description", ""), 40)
        elif event_type == "failure":
            details = truncate(event.get("error", ""), 40)
        elif event_type == "integrated":
            details = "[green]started[/green]"

        table.add_row(icon, timestamp, event_type, organ, details)

    return table


def render_timeline(console: Console, limit: int = 20) -> None:
    """Render timeline table to console."""
    observer = get_observer()
    events = observer.get_timeline(limit=limit)
    table = create_timeline_table(events, limit=limit)
    console.print(table)


class OrganTable:
    """Stateful organ table that can be refreshed."""

    def __init__(self, show_all: bool = False):
        self.show_all = show_all

    def render(self, console: Console) -> None:
        """Render to console."""
        render_organs(console, show_all=self.show_all)


class GoalTable:
    """Stateful goal table that can be refreshed."""

    def render(self, console: Console) -> None:
        """Render to console."""
        render_goals(console)


class FailureTable:
    """Stateful failure table that can be refreshed."""

    def render(self, console: Console) -> None:
        """Render to console."""
        render_failures(console)
