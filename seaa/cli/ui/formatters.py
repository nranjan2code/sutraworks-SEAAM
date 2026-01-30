"""
SEAA CLI Output Formatters

Utility functions for formatting output with Rich styling.
"""

from datetime import datetime
from typing import Optional

from rich.text import Text

from seaa.kernel.protocols import OrganHealth


def format_health(health: OrganHealth) -> Text:
    """
    Format health status with appropriate color.

    Returns styled Rich Text.
    """
    colors = {
        OrganHealth.HEALTHY: "green",
        OrganHealth.DEGRADED: "yellow",
        OrganHealth.SICK: "red",
        OrganHealth.STOPPED: "dim",
    }
    color = colors.get(health, "white")
    return Text(health.value.upper(), style=color)


def health_indicator(health: OrganHealth) -> str:
    """
    Return a colored indicator for health status.

    Uses Unicode circles with Rich markup.
    """
    indicators = {
        OrganHealth.HEALTHY: "[green]●[/green]",
        OrganHealth.DEGRADED: "[yellow]●[/yellow]",
        OrganHealth.SICK: "[red]●[/red]",
        OrganHealth.STOPPED: "[dim]○[/dim]",
    }
    return indicators.get(health, "[white]?[/white]")


def active_indicator(active: bool) -> str:
    """
    Return a colored indicator for active status.

    Green dot = active, gray circle = inactive.
    """
    if active:
        return "[green]●[/green]"
    return "[dim]○[/dim]"


def format_timestamp(iso_timestamp: Optional[str], include_date: bool = False) -> str:
    """
    Format ISO timestamp for display.

    Args:
        iso_timestamp: ISO 8601 timestamp string
        include_date: If True, include the date portion

    Returns:
        Formatted time string (HH:MM:SS or YYYY-MM-DD HH:MM:SS)
    """
    if not iso_timestamp:
        return "-"

    try:
        # Handle various ISO formats
        ts = iso_timestamp.replace("Z", "+00:00")
        if "T" in ts:
            date_part, time_part = ts.split("T")
            # Remove microseconds and timezone
            time_clean = time_part.split(".")[0].split("+")[0].split("-")[0]

            if include_date:
                return f"{date_part} {time_clean}"
            return time_clean
        return iso_timestamp[:19]
    except Exception:
        return iso_timestamp[:19] if len(iso_timestamp) > 19 else iso_timestamp


def format_uptime(seconds: float) -> str:
    """
    Format uptime in human-readable form.

    Examples:
        - 45 -> "45s"
        - 120 -> "2m 0s"
        - 3665 -> "1h 1m"
        - 90061 -> "1d 1h"
    """
    if seconds < 60:
        return f"{int(seconds)}s"

    minutes = int(seconds // 60)
    secs = int(seconds % 60)

    if minutes < 60:
        return f"{minutes}m {secs}s"

    hours = minutes // 60
    mins = minutes % 60

    if hours < 24:
        return f"{hours}h {mins}m"

    days = hours // 24
    hrs = hours % 24
    return f"{days}d {hrs}h"


def format_percentage(value: float, decimals: int = 0) -> str:
    """
    Format a ratio as percentage.

    Args:
        value: Float between 0 and 1
        decimals: Number of decimal places

    Returns:
        Percentage string like "75%" or "75.5%"
    """
    pct = value * 100
    if decimals == 0:
        return f"{int(pct)}%"
    return f"{pct:.{decimals}f}%"


def format_count(current: int, total: int) -> str:
    """
    Format a count ratio.

    Examples:
        - (2, 4) -> "2/4"
        - (0, 0) -> "0"
    """
    if total == 0:
        return "0"
    return f"{current}/{total}"


def truncate(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Truncate text to max length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncated

    Returns:
        Truncated text or original if short enough
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def genesis_status_indicator(running: bool) -> str:
    """
    Return Genesis status indicator for prompt.

    Green dot = running, red dot = stopped.
    """
    if running:
        return "[green]●[/green]"
    return "[red]●[/red]"


def format_error_preview(error: Optional[str], max_length: int = 60) -> str:
    """
    Format error message for preview display.

    Truncates and cleans up error messages.
    """
    if not error:
        return "-"

    # Clean up common noise
    cleaned = error.replace("\n", " ").strip()

    return truncate(cleaned, max_length)


def format_relative_time(iso_timestamp: Optional[str]) -> str:
    """
    Format timestamp as relative time (e.g., "2 hours ago").

    Falls back to absolute time if humanize not available.
    """
    if not iso_timestamp:
        return "-"

    try:
        import humanize

        # Parse ISO timestamp
        ts = iso_timestamp.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts.replace("+00:00", ""))
        return humanize.naturaltime(dt)
    except ImportError:
        # Fallback to absolute time
        return format_timestamp(iso_timestamp, include_date=True)
    except Exception:
        return format_timestamp(iso_timestamp)
