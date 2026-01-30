"""
SEAA Interactive CLI

A best-in-class terminal experience for the Self-Evolving Autonomous Agent.

Features:
- Interactive REPL with history and completion
- Rich terminal UI (tables, panels, spinners)
- Fuzzy matching for typo tolerance
- Natural language command recognition
- Live dashboard with real-time updates

Dependencies:
- rich>=13.0.0
- prompt_toolkit>=3.0.0
- humanize>=4.0.0 (optional)

Install with: pip install seaa[cli]
"""

# Lazy imports to avoid import errors when dependencies aren't installed
_REPL = None
_run_interactive = None
_CommandRegistry = None
_get_registry = None


def _check_dependencies():
    """Check if required dependencies are installed."""
    missing = []

    try:
        import rich
    except ImportError:
        missing.append("rich>=13.0.0")

    try:
        import prompt_toolkit
    except ImportError:
        missing.append("prompt_toolkit>=3.0.0")

    if missing:
        raise ImportError(
            f"Interactive CLI requires additional dependencies: {', '.join(missing)}\n"
            "Install with: pip install seaa[cli]"
        )


def REPL(*args, **kwargs):
    """Get REPL class (lazy import)."""
    _check_dependencies()
    from seaa.cli.repl import REPL as _REPL
    return _REPL(*args, **kwargs)


def run_interactive(*args, **kwargs):
    """Run interactive REPL (lazy import)."""
    _check_dependencies()
    from seaa.cli.repl import run_interactive as _run_interactive
    return _run_interactive(*args, **kwargs)


def CommandRegistry(*args, **kwargs):
    """Get CommandRegistry class (lazy import)."""
    _check_dependencies()
    from seaa.cli.commands import CommandRegistry as _CommandRegistry
    return _CommandRegistry(*args, **kwargs)


def get_registry():
    """Get command registry singleton (lazy import)."""
    _check_dependencies()
    from seaa.cli.commands import get_registry as _get_registry
    return _get_registry()


__all__ = [
    "REPL",
    "run_interactive",
    "CommandRegistry",
    "get_registry",
]
