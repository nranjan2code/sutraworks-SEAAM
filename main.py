"""
Self-Evolving Autonomous Agent

The code that writes itself.

Usage:
    python main.py [--reset] [--config CONFIG_PATH]
"""

import argparse
import sys
from pathlib import Path

# Ensure we can import from current directory
sys.path.insert(0, str(Path(__file__).parent))

from seaa.kernel import Genesis
from seaa.core.logging import setup_logging, get_logger


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Self-Evolving Autonomous Agent"
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


def reset_system():
    """Reset the system to tabula rasa state."""
    import shutil
    import json
    
    logger = get_logger("main")
    
    # Delete soma directory
    soma_dir = Path("soma")
    if soma_dir.exists():
        shutil.rmtree(soma_dir)
        logger.info("Deleted soma/ directory")
    
    # Reset DNA
    dna_path = Path("dna.json")
    tabula_rasa = {
        "system_version": "1.0.0",
        "system_name": "SEAA-TabulaRasa",
        "blueprint": {},
        "goals": [
            {"description": "I must be able to perceive the file system.", "priority": 1, "satisfied": False},
            {"description": "I must have a memory.", "priority": 1, "satisfied": False},
            {"description": "I must have a visual dashboard.", "priority": 2, "satisfied": False},
        ],
        "active_modules": [],
        "failures": [],
        "metadata": {},
    }
    
    with open(dna_path, "w") as f:
        json.dump(tabula_rasa, f, indent=2)
    
    logger.info("Reset DNA to tabula rasa")


def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    log_level = args.log_level or "DEBUG"
    setup_logging(level=log_level, format_type="colored")
    logger = get_logger("main")
    
    # Handle reset
    if args.reset:
        logger.warning("=" * 50)
        logger.warning("ROBINSON CRUSOE RESET INITIATED")
        logger.warning("=" * 50)
        reset_system()
    
    # Initialize and awaken
    try:
        genesis = Genesis()
        genesis.awaken()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
