"""
Self-Evolving Autonomous Agent

The code that writes itself.

Usage:
    python main.py [command] [options]
    python main.py -i                # Interactive mode

Commands:
    (none)      Start the agent (default)
    status      Show system status
    organs      List organs with health
    goals       Show goals and progress
    failures    Show failure records
    watch       Live event stream
    identity    Show/set instance identity
    timeline    Show evolution timeline

Options:
    -i, --interactive  Launch interactive REPL
    --reset            Reset to tabula rasa state before starting
    --config           Path to configuration file
    --log-level        Override log level
"""

import argparse
import sys
import json
from pathlib import Path

# Ensure we can import from current directory
sys.path.insert(0, str(Path(__file__).parent))

from seaa.kernel import Genesis
from seaa.core.logging import setup_logging, get_logger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Self-Evolving Autonomous Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  status      Show system status and health
  organs      List all organs with health status
  goals       Show goals and satisfaction progress
  failures    Show failure records and circuit breakers
  watch       Stream events in real-time
  identity    Show or set instance identity
  timeline    Show recent evolution timeline

Examples:
  python main.py                    # Start the agent
  python main.py -i                 # Interactive mode
  python main.py status             # Check health
  python main.py organs             # List organs
  python main.py identity --name Robinson  # Set name
  python main.py watch              # Live events
        """
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # status
    status_parser = subparsers.add_parser("status", help="Show system status")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # organs
    organs_parser = subparsers.add_parser("organs", help="List organs")
    organs_parser.add_argument("--json", action="store_true", help="Output as JSON")
    organs_parser.add_argument("--all", action="store_true", help="Include stopped organs")

    # goals
    goals_parser = subparsers.add_parser("goals", help="Show goals")
    goals_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # failures
    failures_parser = subparsers.add_parser("failures", help="Show failures")
    failures_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # watch
    watch_parser = subparsers.add_parser("watch", help="Stream events")
    watch_parser.add_argument("--pattern", type=str, action="append", help="Event patterns to watch")
    watch_parser.add_argument("--poll", action="store_true", help="Poll DNA changes (works without Genesis)")
    watch_parser.add_argument("--interval", type=float, default=2.0, help="Poll interval in seconds (default: 2.0)")

    # identity
    identity_parser = subparsers.add_parser("identity", help="Show/set identity")
    identity_parser.add_argument("--name", type=str, help="Set instance name")
    identity_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # timeline
    timeline_parser = subparsers.add_parser("timeline", help="Show evolution timeline")
    timeline_parser.add_argument("--limit", type=int, default=20, help="Max events")
    timeline_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Global options
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Launch interactive REPL with rich UI",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset to tabula rasa state before starting",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Override log level",
    )

    return parser.parse_args()


# =========================================
# Command Handlers
# =========================================

def cmd_status(args):
    """Show system status."""
    from seaa.kernel.observer import get_observer
    from seaa.kernel.identity import get_identity

    observer = get_observer()
    vitals = observer.get_vitals()
    identity = get_identity()

    if args.json:
        print(json.dumps({
            "identity": {
                "id": identity.id,
                "name": identity.name,
            },
            "vitals": vitals.to_dict(),
        }, indent=2))
        return

    # Health indicator
    if vitals.sick_organs > 0:
        health = "DEGRADED"
        health_color = "\033[93m"  # Yellow
    else:
        health = "HEALTHY"
        health_color = "\033[92m"  # Green
    reset = "\033[0m"

    print(f"\n{identity.name} ({identity.id[:8]})")
    print("=" * 40)
    print(f"Status:      {health_color}{health}{reset}")
    print(f"Uptime:      {vitals.uptime_seconds:.0f}s")
    print(f"DNA:         {vitals.dna_hash}")
    print()
    print(f"Organs:      {vitals.healthy_organs}/{vitals.organ_count} healthy")
    if vitals.sick_organs > 0:
        print(f"             {vitals.sick_organs} in circuit breaker")
    print(f"Goals:       {vitals.goals_satisfied}/{vitals.goals_total} satisfied")
    print(f"Evolutions:  {vitals.total_evolutions}")
    print(f"Pending:     {vitals.pending_blueprints}")
    if vitals.total_failures > 0:
        print(f"Failures:    {vitals.total_failures}")
    print()


def cmd_organs(args):
    """List organs with health status."""
    from seaa.kernel.observer import get_observer
    from seaa.kernel.protocols import OrganHealth

    observer = get_observer()
    organs = observer.get_organs()

    if args.json:
        print(json.dumps([o.to_dict() for o in organs], indent=2))
        return

    # Filter if not --all
    if not args.all:
        organs = [o for o in organs if o.active or o.circuit_open]

    if not organs:
        print("No organs found.")
        return

    print("\nOrgans:")
    print("-" * 60)

    for organ in organs:
        # Status indicators
        if organ.active:
            active_icon = "\033[92m●\033[0m"  # Green dot
        else:
            active_icon = "\033[90m○\033[0m"  # Gray dot

        if organ.health == OrganHealth.HEALTHY:
            health_icon = "\033[92m✓\033[0m"
        elif organ.health == OrganHealth.DEGRADED:
            health_icon = "\033[93m!\033[0m"
        elif organ.health == OrganHealth.SICK:
            health_icon = "\033[91m✗\033[0m"
        else:
            health_icon = "\033[90m-\033[0m"

        print(f"  {active_icon} {health_icon}  {organ.name}")

        if organ.last_error:
            error_preview = organ.last_error[:50] + "..." if len(organ.last_error) > 50 else organ.last_error
            print(f"        └─ {error_preview}")

    print()


def cmd_goals(args):
    """Show goals and progress."""
    from seaa.kernel.observer import get_observer

    observer = get_observer()
    goals = observer.get_goals()

    if args.json:
        print(json.dumps([g.to_dict() for g in goals], indent=2))
        return

    if not goals:
        print("No goals defined.")
        return

    print("\nGoals:")
    print("-" * 60)

    for goal in goals:
        if goal.satisfied:
            icon = "\033[92m✓\033[0m"
        else:
            icon = "\033[90m○\033[0m"

        print(f"  {icon} [{goal.priority}] {goal.description}")

        if goal.required_organs:
            matching = len(goal.matching_organs)
            patterns = ", ".join(goal.required_organs)
            print(f"       requires: {patterns}")
            if matching > 0:
                print(f"       matched:  {matching} organ(s)")

    print()


def cmd_failures(args):
    """Show failure records."""
    from seaa.kernel.observer import get_observer

    observer = get_observer()
    failures = observer.get_failures()

    if args.json:
        print(json.dumps([f.to_dict() for f in failures], indent=2))
        return

    if not failures:
        print("\nNo failures recorded.")
        return

    print("\nFailures:")
    print("-" * 60)

    for failure in failures:
        if failure.circuit_open:
            icon = "\033[91m⊘\033[0m"  # Red circuit
        else:
            icon = "\033[93m!\033[0m"  # Yellow warning

        print(f"  {icon} {failure.module}")
        print(f"     type:     {failure.error_type}")
        print(f"     attempts: {failure.attempts}")
        print(f"     message:  {failure.message[:60]}...")
        if failure.circuit_open:
            print(f"     circuit:  \033[91mOPEN\033[0m")
        print()


def cmd_watch(args):
    """Stream events or poll for changes in real-time."""
    import time

    if args.poll:
        # Poll mode: watch DNA changes directly (works without Genesis)
        from seaa.dna.repository import DNARepository
        repo = DNARepository("dna.json", verify_integrity=False)

        print("Polling DNA changes... (Ctrl+C to stop)")
        print("-" * 60)

        last_hash = None
        try:
            while True:
                try:
                    dna = repo.load()
                    current_hash = f"{dna.metadata.total_evolutions}-{len(dna.active_modules)}"
                    if last_hash is not None and current_hash != last_hash:
                        timestamp = time.strftime("%H:%M:%S")
                        print(f"[{timestamp}] DNA changed: {len(dna.active_modules)} modules, "
                              f"{dna.metadata.total_evolutions} evolutions")
                    last_hash = current_hash
                except Exception as e:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] Error loading DNA: {e}")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        # Event mode: requires Genesis to be running
        from seaa.kernel.observer import get_observer

        observer = get_observer()
        patterns = args.pattern if args.pattern else None

        print("Watching events... (Ctrl+C to stop)")
        print("NOTE: Events only fire when Genesis is running. Use --poll for standalone mode.")
        print("-" * 60)

        try:
            for event in observer.stream_events(patterns):
                timestamp = event.timestamp.split("T")[1].split(".")[0]  # HH:MM:SS
                data_preview = str(event.data)[:50] if event.data else ""
                print(f"[{timestamp}] {event.event_type}: {data_preview}")
        except KeyboardInterrupt:
            print("\nStopped.")


def cmd_identity(args):
    """Show or set instance identity."""
    from seaa.kernel.identity import get_identity, set_name

    if args.name:
        identity = set_name(args.name)
        print(f"Instance renamed to: {identity.name}")
    else:
        identity = get_identity()

    if args.json:
        print(json.dumps(identity.to_dict(), indent=2))
        return

    print(f"\nInstance Identity:")
    print("-" * 40)
    print(f"ID:       {identity.id}")
    print(f"Name:     {identity.name}")
    print(f"Genesis:  {identity.genesis_time}")
    print(f"Lineage:  {identity.lineage}")
    if identity.parent_id:
        print(f"Parent:   {identity.parent_id}")
    print()


def cmd_timeline(args):
    """Show evolution timeline."""
    from seaa.kernel.observer import get_observer

    observer = get_observer()
    events = observer.get_timeline(limit=args.limit)

    if args.json:
        print(json.dumps(events, indent=2))
        return

    if not events:
        print("\nNo evolution events yet.")
        return

    print("\nEvolution Timeline:")
    print("-" * 60)

    for event in events:
        timestamp = event.get("timestamp", "unknown")
        if "T" in timestamp:
            timestamp = timestamp.split("T")[0] + " " + timestamp.split("T")[1].split(".")[0]

        event_type = event.get("type", "unknown")
        organ = event.get("organ", "unknown")

        if event_type == "integrated":
            icon = "\033[92m↑\033[0m"
        elif event_type == "designed":
            icon = "\033[94m◆\033[0m"
        elif event_type == "failure":
            icon = "\033[91m✗\033[0m"
        else:
            icon = "•"

        print(f"  {icon} [{timestamp}] {event_type}: {organ}")

        if event_type == "failure" and event.get("error"):
            print(f"       {event['error'][:50]}...")

    print()


def reset_system():
    """Reset the system to tabula rasa state."""
    import shutil

    logger = get_logger("main")

    # Delete soma directory
    soma_dir = Path("soma")
    if soma_dir.exists():
        shutil.rmtree(soma_dir)
        logger.info("Deleted soma/ directory")

    # Reset DNA (but preserve identity!)
    dna_path = Path("dna.json")
    tabula_rasa = {
        "system_version": "1.0.0",
        "system_name": "SEAA-TabulaRasa",
        "blueprint": {},
        "goals": [
            {
                "description": "I must be able to perceive the file system.",
                "priority": 1,
                "satisfied": False,
                "required_organs": ["soma.perception.*"],
            },
            {
                "description": "I must have a memory.",
                "priority": 1,
                "satisfied": False,
                "required_organs": ["soma.memory.*"],
            },
            {
                "description": "I must be observable.",
                "priority": 2,
                "satisfied": False,
                "required_organs": ["soma.interface.*"],
            },
        ],
        "active_modules": [],
        "failures": [],
        "metadata": {},
    }

    with open(dna_path, "w") as f:
        json.dump(tabula_rasa, f, indent=2)

    # Recalculate integrity hash
    from seaa.dna.repository import DNARepository
    repo = DNARepository(dna_path)
    repo.recalculate_integrity_hash()

    logger.info("Reset DNA to tabula rasa (identity preserved)")


def run_agent():
    """Run the agent (default command)."""
    logger = get_logger("main")

    try:
        genesis = Genesis()
        genesis.awaken()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


def run_interactive():
    """Run the interactive REPL."""
    try:
        from seaa.cli import run_interactive as cli_run
        cli_run()
    except ImportError as e:
        print(f"Interactive mode requires additional dependencies: {e}")
        print("Install with: pip install rich prompt_toolkit")
        sys.exit(1)


def main():
    """Main entry point."""
    args = parse_args()

    # Setup logging (quiet for query commands)
    if args.command in ["status", "organs", "goals", "failures", "identity", "timeline"]:
        log_level = "ERROR"  # Quiet mode for queries
    else:
        log_level = args.log_level or "DEBUG"

    setup_logging(level=log_level, format_type="colored")
    logger = get_logger("main")

    # Handle reset
    if args.reset:
        logger.warning("=" * 50)
        logger.warning("TABULA RASA RESET INITIATED")
        logger.warning("=" * 50)
        reset_system()
        if not args.command:
            # If just --reset, don't start agent
            return

    # Check for interactive mode
    if args.interactive:
        run_interactive()
        return

    # Dispatch to command handler
    if args.command == "status":
        cmd_status(args)
    elif args.command == "organs":
        cmd_organs(args)
    elif args.command == "goals":
        cmd_goals(args)
    elif args.command == "failures":
        cmd_failures(args)
    elif args.command == "watch":
        cmd_watch(args)
    elif args.command == "identity":
        cmd_identity(args)
    elif args.command == "timeline":
        cmd_timeline(args)
    else:
        # Default: run the agent
        run_agent()


if __name__ == "__main__":
    main()
