"""
Tests for SEAA Interactive CLI

Tests cover:
- Command registry
- Fuzzy matching
- Natural language parsing
- Output formatters
"""

import pytest
from unittest.mock import MagicMock, patch


# =========================================
# Fuzzy Matching Tests
# =========================================


class TestLevenshteinDistance:
    """Test Levenshtein distance calculation."""

    def test_identical_strings(self):
        from seaa.cli.parsers.fuzzy import levenshtein_distance

        assert levenshtein_distance("hello", "hello") == 0

    def test_empty_strings(self):
        from seaa.cli.parsers.fuzzy import levenshtein_distance

        assert levenshtein_distance("", "") == 0
        assert levenshtein_distance("hello", "") == 5
        assert levenshtein_distance("", "world") == 5

    def test_single_substitution(self):
        from seaa.cli.parsers.fuzzy import levenshtein_distance

        assert levenshtein_distance("cat", "bat") == 1

    def test_single_insertion(self):
        from seaa.cli.parsers.fuzzy import levenshtein_distance

        assert levenshtein_distance("cat", "cats") == 1

    def test_single_deletion(self):
        from seaa.cli.parsers.fuzzy import levenshtein_distance

        assert levenshtein_distance("cats", "cat") == 1

    def test_multiple_edits(self):
        from seaa.cli.parsers.fuzzy import levenshtein_distance

        assert levenshtein_distance("kitten", "sitting") == 3


class TestFuzzyMatch:
    """Test fuzzy matching functionality."""

    def test_exact_match_returns_1(self):
        from seaa.cli.parsers.fuzzy import similarity

        assert similarity("status", "status") == 1.0

    def test_similar_strings(self):
        from seaa.cli.parsers.fuzzy import similarity

        # "staus" is close to "status" (transposed letters)
        score = similarity("staus", "status")
        assert 0.7 < score < 1.0

    def test_fuzzy_match_finds_candidates(self):
        from seaa.cli.parsers.fuzzy import fuzzy_match

        candidates = ["status", "stop", "start", "organs", "goals"]
        matches = fuzzy_match("staus", candidates, threshold=0.6)

        assert len(matches) > 0
        assert matches[0][0] == "status"  # Best match

    def test_get_best_match(self):
        from seaa.cli.parsers.fuzzy import get_best_match

        candidates = ["status", "stop", "start", "organs"]

        # Typo in "status"
        result = get_best_match("staus", candidates, threshold=0.6)
        assert result is not None
        assert result[0] == "status"

    def test_no_match_below_threshold(self):
        from seaa.cli.parsers.fuzzy import get_best_match

        candidates = ["status", "stop", "start"]
        result = get_best_match("xyz", candidates, threshold=0.6)
        assert result is None

    def test_suggest_correction(self):
        from seaa.cli.parsers.fuzzy import suggest_correction

        candidates = ["status", "stop", "start", "organs", "goals"]

        assert suggest_correction("staus", candidates) == "status"
        assert suggest_correction("oragns", candidates) == "organs"
        assert suggest_correction("status", candidates) is None  # Already correct


class TestIsLikelyTypo:
    """Test typo detection."""

    def test_likely_typo(self):
        from seaa.cli.parsers.fuzzy import is_likely_typo

        assert is_likely_typo("staus", "status")
        assert is_likely_typo("oragns", "organs")

    def test_not_typo_identical(self):
        from seaa.cli.parsers.fuzzy import is_likely_typo

        assert not is_likely_typo("status", "status")

    def test_not_typo_too_different(self):
        from seaa.cli.parsers.fuzzy import is_likely_typo

        assert not is_likely_typo("xyz", "status", max_distance=2)


# =========================================
# Natural Language Parser Tests
# =========================================


class TestNaturalParser:
    """Test natural language intent detection."""

    def test_status_intents(self):
        from seaa.cli.parsers.natural import detect_intent

        assert detect_intent("how are you") == "status"
        assert detect_intent("how are you?") == "status"
        assert detect_intent("how's it going") == "status"
        assert detect_intent("what's up") == "status"
        assert detect_intent("health check") == "status"

    def test_organ_intents(self):
        from seaa.cli.parsers.natural import detect_intent

        assert detect_intent("show organs") == "organs"
        assert detect_intent("list organs") == "organs"
        assert detect_intent("what organs do you have") == "organs"

    def test_goal_intents(self):
        from seaa.cli.parsers.natural import detect_intent

        assert detect_intent("show goals") == "goals"
        assert detect_intent("what's the progress") == "goals"
        assert detect_intent("objectives") == "goals"

    def test_start_intents(self):
        from seaa.cli.parsers.natural import detect_intent

        assert detect_intent("wake up") == "start"
        assert detect_intent("awaken") == "start"
        assert detect_intent("start") == "start"

    def test_stop_intents(self):
        from seaa.cli.parsers.natural import detect_intent

        assert detect_intent("go to sleep") == "stop"
        assert detect_intent("shutdown") == "stop"
        assert detect_intent("stop") == "stop"

    def test_help_intents(self):
        from seaa.cli.parsers.natural import detect_intent

        assert detect_intent("help") == "help"
        assert detect_intent("what can you do") == "help"

    def test_exit_intents(self):
        from seaa.cli.parsers.natural import detect_intent

        assert detect_intent("bye") == "exit"
        assert detect_intent("goodbye") == "exit"
        assert detect_intent("quit") == "exit"

    def test_no_intent(self):
        from seaa.cli.parsers.natural import detect_intent

        assert detect_intent("") is None
        assert detect_intent("random gibberish xyz") is None


class TestIsNaturalQuery:
    """Test natural query detection."""

    def test_question_mark(self):
        from seaa.cli.parsers.natural import is_natural_query

        assert is_natural_query("how are you?")
        assert is_natural_query("what's up?")

    def test_multiple_words(self):
        from seaa.cli.parsers.natural import is_natural_query

        assert is_natural_query("how are you")
        assert is_natural_query("show organs")

    def test_single_word_not_natural(self):
        from seaa.cli.parsers.natural import is_natural_query

        assert not is_natural_query("status")
        assert not is_natural_query("organs")


# =========================================
# Formatter Tests
# =========================================


class TestFormatUptime:
    """Test uptime formatting."""

    def test_seconds(self):
        from seaa.cli.ui.formatters import format_uptime

        assert format_uptime(45) == "45s"

    def test_minutes(self):
        from seaa.cli.ui.formatters import format_uptime

        assert format_uptime(120) == "2m 0s"
        assert format_uptime(125) == "2m 5s"

    def test_hours(self):
        from seaa.cli.ui.formatters import format_uptime

        assert format_uptime(3665) == "1h 1m"

    def test_days(self):
        from seaa.cli.ui.formatters import format_uptime

        assert format_uptime(90061) == "1d 1h"


class TestFormatTimestamp:
    """Test timestamp formatting."""

    def test_iso_timestamp(self):
        from seaa.cli.ui.formatters import format_timestamp

        ts = "2024-01-15T14:30:45.123Z"
        assert format_timestamp(ts) == "14:30:45"

    def test_with_date(self):
        from seaa.cli.ui.formatters import format_timestamp

        ts = "2024-01-15T14:30:45.123Z"
        assert format_timestamp(ts, include_date=True) == "2024-01-15 14:30:45"

    def test_none(self):
        from seaa.cli.ui.formatters import format_timestamp

        assert format_timestamp(None) == "-"


class TestFormatPercentage:
    """Test percentage formatting."""

    def test_whole_number(self):
        from seaa.cli.ui.formatters import format_percentage

        assert format_percentage(0.75) == "75%"
        assert format_percentage(1.0) == "100%"
        assert format_percentage(0.0) == "0%"

    def test_with_decimals(self):
        from seaa.cli.ui.formatters import format_percentage

        assert format_percentage(0.756, decimals=1) == "75.6%"


class TestTruncate:
    """Test text truncation."""

    def test_short_text_unchanged(self):
        from seaa.cli.ui.formatters import truncate

        assert truncate("hello", 50) == "hello"

    def test_long_text_truncated(self):
        from seaa.cli.ui.formatters import truncate

        result = truncate("this is a very long message", 15)
        assert len(result) == 15
        assert result.endswith("...")


class TestHealthIndicators:
    """Test health indicator formatting."""

    def test_health_indicator(self):
        from seaa.cli.ui.formatters import health_indicator
        from seaa.kernel.protocols import OrganHealth

        # Just verify it returns markup strings
        assert "green" in health_indicator(OrganHealth.HEALTHY)
        assert "yellow" in health_indicator(OrganHealth.DEGRADED)
        assert "red" in health_indicator(OrganHealth.SICK)

    def test_active_indicator(self):
        from seaa.cli.ui.formatters import active_indicator

        assert "green" in active_indicator(True)
        assert "dim" in active_indicator(False)


# =========================================
# Command Registry Tests
# =========================================


class TestCommandRegistry:
    """Test command registry functionality."""

    def setup_method(self):
        """Reset registry before each test."""
        from seaa.cli.commands import CommandRegistry

        CommandRegistry.reset()

    def test_register_command(self):
        from seaa.cli.commands import CommandRegistry, Command

        registry = CommandRegistry()
        cmd = Command(
            name="test",
            handler=lambda: None,
            description="Test command",
            aliases=["t"],
        )
        registry.register(cmd)

        assert registry.get("test") is cmd

    def test_get_by_alias(self):
        from seaa.cli.commands import CommandRegistry, Command

        registry = CommandRegistry()
        cmd = Command(
            name="test",
            handler=lambda: None,
            description="Test command",
            aliases=["t", "tst"],
        )
        registry.register(cmd)

        assert registry.get("t") is cmd
        assert registry.get("tst") is cmd

    def test_get_nonexistent(self):
        from seaa.cli.commands import CommandRegistry

        registry = CommandRegistry()
        assert registry.get("nonexistent") is None

    def test_get_all_names_and_aliases(self):
        from seaa.cli.commands import CommandRegistry, Command

        registry = CommandRegistry()
        cmd = Command(
            name="test",
            handler=lambda: None,
            description="Test",
            aliases=["t"],
        )
        registry.register(cmd)

        names = registry.get_all_names_and_aliases()
        assert "test" in names
        assert "t" in names


# =========================================
# Integration Tests (with mocks)
# =========================================


class TestCommandHandlers:
    """Test command handlers with mocked dependencies."""

    @patch("seaa.cli.handlers.get_observer")
    @patch("seaa.cli.handlers.get_identity")
    def test_cmd_status(self, mock_identity, mock_observer):
        """Test status command renders without error."""
        from seaa.cli.handlers import cmd_status, CommandContext
        from seaa.kernel.protocols import Vitals
        from rich.console import Console
        from unittest.mock import MagicMock
        import io

        # Setup mocks
        mock_identity.return_value = MagicMock(
            name="TestInstance",
            id="test-uuid-1234",
            short_id=lambda: "test-uui",
        )

        mock_vitals = MagicMock(spec=Vitals)
        mock_vitals.sick_organs = 0
        mock_vitals.healthy_organs = 2
        mock_vitals.organ_count = 2
        mock_vitals.goals_satisfied = 1
        mock_vitals.goals_total = 3
        mock_vitals.uptime_seconds = 120.0
        mock_vitals.dna_hash = "abc123"
        mock_vitals.total_evolutions = 5
        mock_vitals.pending_blueprints = 0
        mock_vitals.total_failures = 0
        mock_vitals.goal_progress = 0.33

        mock_observer.return_value = MagicMock()
        mock_observer.return_value.get_vitals.return_value = mock_vitals

        # Execute
        output = io.StringIO()
        console = Console(file=output, force_terminal=True)
        ctx = CommandContext(console=console)

        # Should not raise
        cmd_status(ctx)


class TestREPLParsing:
    """Test REPL input parsing logic."""

    def test_empty_input(self):
        """Empty input should return None command."""
        # This tests the parsing logic conceptually
        from seaa.cli.parsers.fuzzy import get_best_match

        result = get_best_match("", ["status", "organs"], threshold=0.6)
        assert result is None
