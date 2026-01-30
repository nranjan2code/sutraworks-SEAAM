"""
SEAA CLI Live Dashboard

Full-screen live dashboard with auto-updating status, organs, and events.
"""

import time
from typing import Optional, List, TYPE_CHECKING

from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from seaa.core.logging import get_logger
from seaa.kernel.observer import get_observer
from seaa.kernel.identity import get_identity
from seaa.kernel.protocols import OrganHealth
from seaa.cli.ui.formatters import (
    health_indicator,
    active_indicator,
    format_uptime,
    format_timestamp,
    format_error_preview,
)

if TYPE_CHECKING:
    from seaa.cli.runtime import GenesisRuntime

logger = get_logger("cli.dashboard")


def create_header(genesis_running: bool = False) -> Panel:
    """Create the header panel."""
    identity = get_identity()

    # Status indicator
    if genesis_running:
        status = Text("RUNNING", style="green bold")
    else:
        status = Text("STOPPED", style="red bold")

    title = Text()
    title.append(identity.name, style="bold cyan")
    title.append(" (")
    title.append(identity.short_id(), style="dim")
    title.append(") - Genesis: ")
    title.append_text(status)

    return Panel(
        title,
        box=box.SIMPLE,
        padding=(0, 1),
    )


def create_vitals_panel() -> Panel:
    """Create the vitals panel."""
    observer = get_observer()
    vitals = observer.get_vitals()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Key", style="cyan", width=12)
    table.add_column("Value", style="white")

    # Health status
    if vitals.sick_organs > 0:
        health = Text("DEGRADED", style="yellow bold")
    else:
        health = Text("HEALTHY", style="green bold")

    table.add_row("Health", health)
    table.add_row("Uptime", format_uptime(vitals.uptime_seconds))
    table.add_row("DNA", vitals.dna_hash)
    table.add_row(
        "Organs", f"{vitals.healthy_organs}/{vitals.organ_count} healthy"
    )
    table.add_row(
        "Goals", f"{vitals.goals_satisfied}/{vitals.goals_total} satisfied"
    )
    table.add_row("Evolutions", str(vitals.total_evolutions))

    if vitals.pending_blueprints > 0:
        table.add_row("Pending", f"{vitals.pending_blueprints} blueprints")

    return Panel(table, title="Vitals", border_style="blue")


def create_organs_panel() -> Panel:
    """Create the organs panel."""
    observer = get_observer()
    organs = observer.get_organs()

    # Filter to active or problematic organs
    organs = [o for o in organs if o.active or o.circuit_open]

    table = Table(show_header=True, header_style="bold", box=box.SIMPLE)
    table.add_column("", width=2)
    table.add_column("Organ", style="white", no_wrap=True)
    table.add_column("Health", width=8)

    if not organs:
        table.add_row("", "[dim]No active organs[/dim]", "")
    else:
        for organ in sorted(organs, key=lambda o: o.name)[:10]:  # Limit to 10
            status = active_indicator(organ.active)
            health = health_indicator(organ.health)
            table.add_row(status, organ.name, health)

    return Panel(table, title="Organs", border_style="green")


def create_goals_panel() -> Panel:
    """Create the goals panel."""
    observer = get_observer()
    goals = observer.get_goals()

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("", width=2)
    table.add_column("Goal", style="white")

    if not goals:
        table.add_row("", "[dim]No goals defined[/dim]")
    else:
        for goal in sorted(goals, key=lambda g: (g.satisfied, g.priority))[:6]:
            icon = "[green]✓[/green]" if goal.satisfied else "[dim]○[/dim]"
            table.add_row(icon, goal.description[:40])

    return Panel(table, title="Goals", border_style="yellow")


def create_events_panel(events: List[dict]) -> Panel:
    """Create the recent events panel."""
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Time", width=8, style="dim")
    table.add_column("Event", style="white")

    if not events:
        table.add_row("", "[dim]No recent events[/dim]")
    else:
        for event in events[:8]:  # Limit to 8
            ts = format_timestamp(event.get("timestamp", ""))
            event_type = event.get("type", "unknown")
            organ = event.get("organ", "-")

            # Format based on type
            if event_type == "integrated":
                text = f"[green]↑[/green] {organ}"
            elif event_type == "designed":
                text = f"[blue]◆[/blue] {organ}"
            elif event_type == "failure":
                text = f"[red]✗[/red] {organ}"
            else:
                text = f"• {event_type}: {organ}"

            table.add_row(ts, text)

    return Panel(table, title="Recent Events", border_style="magenta")


def create_footer() -> Panel:
    """Create the footer panel."""
    text = Text()
    text.append("q", style="bold")
    text.append(" quit  ")
    text.append("r", style="bold")
    text.append(" refresh  ")
    text.append("s", style="bold")
    text.append(" start/stop Genesis")

    return Panel(text, box=box.SIMPLE, padding=(0, 1))


def create_dashboard_layout(
    genesis_running: bool = False,
    events: Optional[List[dict]] = None,
) -> Layout:
    """Create the full dashboard layout."""
    events = events or []

    layout = Layout()

    # Main structure
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3),
    )

    # Body split
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right"),
    )

    # Left column
    layout["left"].split_column(
        Layout(name="vitals"),
        Layout(name="goals"),
    )

    # Right column
    layout["right"].split_column(
        Layout(name="organs"),
        Layout(name="events"),
    )

    # Populate panels
    layout["header"].update(create_header(genesis_running))
    layout["vitals"].update(create_vitals_panel())
    layout["goals"].update(create_goals_panel())
    layout["organs"].update(create_organs_panel())
    layout["events"].update(create_events_panel(events))
    layout["footer"].update(create_footer())

    return layout


def run_dashboard(
    console: Console,
    runtime: Optional["GenesisRuntime"] = None,
    refresh_rate: float = 2.0,
) -> None:
    """
    Run the live dashboard.

    Args:
        console: Rich console
        runtime: Genesis runtime for status
        refresh_rate: Refresh interval in seconds
    """
    from seaa.kernel.observer import get_observer

    console.print("[dim]Starting dashboard... (q to quit)[/dim]")

    observer = get_observer()

    try:
        with Live(
            create_dashboard_layout(
                genesis_running=runtime.is_running() if runtime else False,
            ),
            console=console,
            refresh_per_second=1 / refresh_rate,
            screen=True,
        ) as live:
            while True:
                # Get latest events
                events = observer.get_timeline(limit=10)

                # Update layout
                live.update(
                    create_dashboard_layout(
                        genesis_running=runtime.is_running() if runtime else False,
                        events=events,
                    )
                )

                time.sleep(refresh_rate)

    except KeyboardInterrupt:
        pass

    console.print("[dim]Dashboard closed.[/dim]")


def run_event_stream(
    console: Console,
    patterns: Optional[List[str]] = None,
) -> None:
    """
    Stream events in real-time.

    Args:
        console: Rich console
        patterns: Event patterns to filter
    """
    from seaa.kernel.observer import get_observer

    observer = get_observer()

    console.print("[dim]Streaming events... (Ctrl+C to stop)[/dim]")
    console.print(
        "[dim]Note: Events only fire when Genesis is running.[/dim]"
    )
    console.print()

    try:
        for event in observer.stream_events(patterns):
            ts = format_timestamp(event.timestamp)
            event_type = event.event_type

            # Format data preview
            data_str = ""
            if event.data:
                if isinstance(event.data, dict):
                    # Show key pieces of data
                    parts = []
                    for key in ["organ", "module", "error"]:
                        if key in event.data:
                            parts.append(f"{key}={event.data[key]}")
                    data_str = ", ".join(parts[:2])
                else:
                    data_str = str(event.data)[:40]

            console.print(f"[dim]{ts}[/dim] [cyan]{event_type}[/cyan] {data_str}")

    except KeyboardInterrupt:
        pass

    console.print()
    console.print("[dim]Stream stopped.[/dim]")
