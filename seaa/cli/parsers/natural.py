"""
SEAA CLI Natural Language Parser

Maps natural language phrases to commands.
"""

import re
from typing import Dict, List, Optional, Tuple

from seaa.core.logging import get_logger

logger = get_logger("cli.natural")


# Intent patterns: regex -> command name
# Patterns are tried in order, first match wins
INTENT_PATTERNS: List[Tuple[str, str]] = [
    # Status/health queries
    (r"how\s+(are\s+you|is\s+it|are\s+things)", "status"),
    (r"how('s|s)\s+(it\s+going|everything)", "status"),
    (r"what('s|s)\s+up", "status"),
    (r"(are\s+you\s+)?(ok|okay|alright|fine)", "status"),
    (r"health(\s+check)?", "status"),
    (r"vitals", "status"),

    # Organ queries
    (r"(show|list|what)\s+(are\s+)?(the\s+)?organs", "organs"),
    (r"organs?\s+(status|list|info)", "organs"),
    (r"what\s+organs\s+(do\s+you\s+have|exist)", "organs"),

    # Goal queries
    (r"(show|what\s+are)\s+(the\s+)?goals", "goals"),
    (r"goals?\s+(status|progress|list)", "goals"),
    (r"(what('s|s)|show)\s+(the\s+)?progress", "goals"),
    (r"objectives", "goals"),

    # Failure queries
    (r"(show|what\s+are)\s+(the\s+)?failures?", "failures"),
    (r"(what|any)\s+(went\s+wrong|failed|errors?)", "failures"),
    (r"errors?(\s+list)?", "failures"),

    # Dashboard
    (r"(show|open|launch)\s+(the\s+)?dashboard", "dashboard"),
    (r"dashboard", "dashboard"),
    (r"live\s+(view|display|monitor)", "dashboard"),
    (r"full\s*screen", "dashboard"),

    # Watch/stream
    (r"(watch|stream|monitor)\s+(events?)?", "watch"),
    (r"event\s+stream", "watch"),
    (r"show\s+events", "watch"),

    # Timeline
    (r"(show|what('s|s))\s+(the\s+)?timeline", "timeline"),
    (r"evolution\s+(history|timeline)", "timeline"),
    (r"history", "timeline"),

    # Identity
    (r"who\s+(are\s+you|am\s+i)", "identity"),
    (r"what('s|s)\s+(your|the)\s+name", "identity"),
    (r"identity", "identity"),
    (r"(my|your)\s+id", "identity"),

    # Start/awaken
    (r"(start|awaken|wake)\s*(up)?", "start"),
    (r"run", "start"),
    (r"begin", "start"),
    (r"let('s|s)?\s+go", "start"),

    # Stop/sleep
    (r"(stop|sleep|shutdown|shut\s+down)", "stop"),
    (r"go\s+to\s+sleep", "stop"),
    (r"rest", "stop"),

    # Evolve
    (r"evolve", "evolve"),
    (r"grow", "evolve"),
    (r"adapt", "evolve"),
    (r"(trigger|run)\s+(an?\s+)?evolution", "evolve"),

    # Help
    (r"help(\s+me)?", "help"),
    (r"what\s+can\s+(you|i)\s+do", "help"),
    (r"(show|list)\s+(the\s+)?commands", "help"),
    (r"how\s+do\s+i", "help"),

    # Exit
    (r"(bye|goodbye|see\s+you|exit|quit)", "exit"),
    (r"(i('m|am)\s+)?(done|finished|leaving)", "exit"),
]


class NaturalParser:
    """
    Parse natural language input to detect command intent.

    Uses regex patterns to match conversational phrases
    to their corresponding commands.
    """

    def __init__(self, custom_patterns: Optional[List[Tuple[str, str]]] = None):
        """
        Initialize parser with optional custom patterns.

        Args:
            custom_patterns: Additional (regex, command) patterns
        """
        self._patterns = list(INTENT_PATTERNS)
        if custom_patterns:
            self._patterns.extend(custom_patterns)

        # Compile patterns for efficiency
        self._compiled = [(re.compile(p, re.IGNORECASE), cmd) for p, cmd in self._patterns]

    def parse(self, text: str) -> Optional[str]:
        """
        Parse input and return detected command.

        Args:
            text: Natural language input

        Returns:
            Command name or None if no match
        """
        text = text.strip()
        if not text:
            return None

        # Strip question marks and punctuation
        text = re.sub(r"[?!.,]+$", "", text).strip()

        # Try each pattern
        for pattern, command in self._compiled:
            if pattern.search(text):
                logger.debug(f"Natural match: '{text}' -> {command}")
                return command

        return None

    def get_confidence(self, text: str) -> Tuple[Optional[str], float]:
        """
        Parse with confidence score.

        Returns:
            (command, confidence) where confidence is 0.0 to 1.0
        """
        text = text.strip().lower()
        if not text:
            return (None, 0.0)

        # Clean up
        text = re.sub(r"[?!.,]+$", "", text).strip()

        best_match = None
        best_coverage = 0.0

        for pattern, command in self._compiled:
            match = pattern.search(text)
            if match:
                # Calculate how much of the input the pattern covers
                coverage = (match.end() - match.start()) / len(text)
                if coverage > best_coverage:
                    best_match = command
                    best_coverage = coverage

        # Confidence based on coverage
        confidence = min(best_coverage * 1.2, 1.0)  # Slight boost

        return (best_match, confidence)


# Module-level singleton
_parser: Optional[NaturalParser] = None


def get_parser() -> NaturalParser:
    """Get the natural parser singleton."""
    global _parser
    if _parser is None:
        _parser = NaturalParser()
    return _parser


def detect_intent(text: str) -> Optional[str]:
    """
    Detect command intent from natural language.

    Args:
        text: Natural language input

    Returns:
        Command name or None
    """
    return get_parser().parse(text)


def is_natural_query(text: str) -> bool:
    """
    Check if text looks like a natural language query.

    Returns True if text contains spaces or question marks,
    suggesting conversational rather than command input.
    """
    text = text.strip()

    # Contains question mark
    if "?" in text:
        return True

    # Multiple words (commands are typically single words)
    if " " in text:
        return True

    return False
