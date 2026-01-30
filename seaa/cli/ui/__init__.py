"""
SEAA CLI UI Components

Rich terminal UI components for displaying system state.
"""

from seaa.cli.ui.formatters import (
    format_health,
    format_timestamp,
    format_uptime,
    format_percentage,
    health_indicator,
    active_indicator,
)
from seaa.cli.ui.panels import StatusPanel, render_status
from seaa.cli.ui.tables import OrganTable, GoalTable, FailureTable

__all__ = [
    # Formatters
    "format_health",
    "format_timestamp",
    "format_uptime",
    "format_percentage",
    "health_indicator",
    "active_indicator",
    # Panels
    "StatusPanel",
    "render_status",
    # Tables
    "OrganTable",
    "GoalTable",
    "FailureTable",
]
