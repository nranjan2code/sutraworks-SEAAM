"""
SEAA CLI Panel Components

Rich Panel implementations for displaying status and identity.
"""

from typing import Optional, TYPE_CHECKING

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from seaa.kernel.observer import get_observer
from seaa.kernel.identity import get_identity
from seaa.kernel.protocols import Vitals
from seaa.cli.ui.formatters import (
    format_uptime,
    format_percentage,
    format_count,
    format_timestamp,
)

if TYPE_CHECKING:
    from seaa.cli.runtime import GenesisRuntime


def create_status_panel(
    vitals: Vitals,
    identity_name: str,
    identity_id: str,
    genesis_running: bool = False,
) -> Panel:
    """
    Create a Rich Panel showing system status.

    Args:
        vitals: System vitals from beacon
        identity_name: Instance name
        identity_id: Instance ID (short)
        genesis_running: Whether Genesis is running
    """
    # Build status table (no borders for cleaner look)
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="cyan", width=14)
    table.add_column("Value", style="white")

    # Health indicator
    if vitals.sick_organs > 0:
        health_text = Text("DEGRADED", style="yellow bold")
    else:
        health_text = Text("HEALTHY", style="green bold")

    # Genesis status
    if genesis_running:
        genesis_text = Text("RUNNING", style="green")
    else:
        genesis_text = Text("STOPPED", style="dim")

    table.add_row("Status", health_text)
    table.add_row("Genesis", genesis_text)
    table.add_row("Uptime", format_uptime(vitals.uptime_seconds))
    table.add_row("DNA", vitals.dna_hash)
    table.add_row("", "")  # Spacer

    # Counts
    organ_text = format_count(vitals.healthy_organs, vitals.organ_count) + " healthy"
    if vitals.sick_organs > 0:
        organ_text += f" ([red]{vitals.sick_organs} sick[/red])"

    goal_text = format_count(vitals.goals_satisfied, vitals.goals_total) + " satisfied"
    goal_pct = format_percentage(vitals.goal_progress)
    goal_text += f" ({goal_pct})"

    table.add_row("Organs", organ_text)
    table.add_row("Goals", goal_text)
    table.add_row("Evolutions", str(vitals.total_evolutions))

    if vitals.pending_blueprints > 0:
        table.add_row("Pending", f"[cyan]{vitals.pending_blueprints}[/cyan] blueprints")

    if vitals.total_failures > 0:
        table.add_row("Failures", f"[yellow]{vitals.total_failures}[/yellow] recorded")

    # Create panel with identity in title
    title = f"{identity_name} ([dim]{identity_id}[/dim])"

    return Panel(
        table,
        title=title,
        title_align="left",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2),
    )


def render_status(
    console: Console,
    show_genesis_status: bool = True,
    runtime: Optional["GenesisRuntime"] = None,
) -> None:
    """
    Render status panel to console.

    Args:
        console: Rich console for output
        show_genesis_status: Include Genesis running status
        runtime: Genesis runtime for checking running state
    """
    observer = get_observer()
    vitals = observer.get_vitals()
    identity = get_identity()

    genesis_running = False
    if show_genesis_status and runtime is not None:
        genesis_running = runtime.is_running()

    panel = create_status_panel(
        vitals=vitals,
        identity_name=identity.name,
        identity_id=identity.short_id(),
        genesis_running=genesis_running,
    )

    console.print(panel)


def create_identity_panel(
    identity_id: str,
    identity_name: str,
    genesis_time: str,
    lineage: str,
    parent_id: Optional[str] = None,
) -> Panel:
    """
    Create a Rich Panel showing instance identity.

    Args:
        identity_id: Full instance UUID
        identity_name: Instance name
        genesis_time: Creation timestamp
        lineage: Lineage hash
        parent_id: Parent instance ID if any
    """
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="cyan", width=12)
    table.add_column("Value", style="white")

    table.add_row("ID", identity_id)
    table.add_row("Name", identity_name)
    table.add_row("Genesis", format_timestamp(genesis_time, include_date=True))
    table.add_row("Lineage", lineage)

    if parent_id:
        table.add_row("Parent", parent_id)

    return Panel(
        table,
        title="Instance Identity",
        title_align="left",
        border_style="blue",
        box=box.ROUNDED,
        padding=(1, 2),
    )


def render_identity(console: Console) -> None:
    """Render identity panel to console."""
    identity = get_identity()

    panel = create_identity_panel(
        identity_id=identity.id,
        identity_name=identity.name,
        genesis_time=identity.genesis_time,
        lineage=identity.lineage,
        parent_id=identity.parent_id,
    )

    console.print(panel)


class StatusPanel:
    """
    Stateful status panel that can be refreshed.

    Useful for live dashboards.
    """

    def __init__(self, runtime: Optional["GenesisRuntime"] = None):
        self.runtime = runtime

    def render(self, console: Console) -> None:
        """Render to console."""
        render_status(console, show_genesis_status=True, runtime=self.runtime)

    def get_panel(self) -> Panel:
        """Get panel for live display."""
        observer = get_observer()
        vitals = observer.get_vitals()
        identity = get_identity()

        genesis_running = False
        if self.runtime is not None:
            genesis_running = self.runtime.is_running()

        return create_status_panel(
            vitals=vitals,
            identity_name=identity.name,
            identity_id=identity.short_id(),
            genesis_running=genesis_running,
        )
