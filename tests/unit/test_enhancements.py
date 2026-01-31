"""
Tests for production enhancements:
1. Event bus retention policy
2. Dependency ordering
3. Remote logging with sanitization
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from queue import Queue

from seaa.kernel.bus import EventBus, Event, bus
from seaa.kernel.genesis import Genesis
from seaa.dna.schema import DNA, OrganBlueprint
from seaa.core.remote_logging import RemoteLoggingHandler, setup_remote_logging
from seaa.core.config import config


# =========================================
# Event Bus Retention Tests
# =========================================


class TestEventBusRetention:
    """Test event bus retention functionality."""

    def test_event_retention_enabled(self):
        """Test that events are retained when enabled."""
        bus = EventBus()

        # Create and publish test events
        event1 = Event(event_type="test.event1", data={"value": 1})
        event2 = Event(event_type="test.event2", data={"value": 2})

        bus.publish(event1)
        bus.publish(event2)

        # Check retention
        retained = bus.get_retained_events()
        assert len(retained) >= 2, "Events should be retained"
        assert retained[-2].event_type == "test.event1"
        assert retained[-1].event_type == "test.event2"

    def test_get_retained_count(self):
        """Test getting count of retained events."""
        bus = EventBus()

        initial_count = bus.get_retained_count()

        event = Event(event_type="test.count", source="test")
        bus.publish(event)

        new_count = bus.get_retained_count()
        assert new_count > initial_count

    def test_get_retained_events_with_filter(self):
        """Test filtering retained events by type."""
        bus = EventBus()

        # Create events of different types
        event1 = Event(event_type="organ.evolved", data={})
        event2 = Event(event_type="organ.integrated", data={})
        event3 = Event(event_type="organ.evolved", data={})

        bus.publish(event1)
        bus.publish(event2)
        bus.publish(event3)

        # Filter by type
        evolved = bus.get_retained_events(event_type="organ.evolved")
        assert len(evolved) >= 2
        assert all(e.event_type == "organ.evolved" for e in evolved)

    def test_get_retained_events_with_limit(self):
        """Test limiting returned events."""
        bus = EventBus()

        # Publish 5 events
        for i in range(5):
            event = Event(event_type="test.event", data={"index": i})
            bus.publish(event)

        # Get last 2
        recent = bus.get_retained_events(count=2)
        assert len(recent) == 2

    def test_max_retained_events_limit(self):
        """Test that retained events don't exceed maxlen."""
        # The ring buffer has maxlen set in config
        bus = EventBus()
        max_retained = config.event_bus.max_retained_events

        # Publish more than max
        for i in range(max_retained + 10):
            event = Event(event_type="test.overflow", data={"index": i})
            bus.publish(event)

        # Should be at most max_retained
        retained = bus.get_retained_events()
        assert len(retained) <= max_retained


# =========================================
# Dependency Ordering Tests
# =========================================


class TestDependencyOrdering:
    """Test organ dependency checking."""

    def test_organ_without_dependencies_is_buildable(self):
        """Test that organs without dependencies can be built immediately."""
        genesis = Genesis()

        bp1 = OrganBlueprint(
            name="soma.perception.observer",
            description="Observe files",
            dependencies=[]
        )

        pending = {"soma.perception.observer": bp1}
        buildable = genesis._get_buildable_organs(pending)

        assert len(buildable) == 1
        assert buildable[0][0] == "soma.perception.observer"

    def test_organ_with_satisfied_dependency_is_buildable(self):
        """Test that organs with satisfied dependencies can be built."""
        genesis = Genesis()
        genesis.dna.mark_active("soma.perception.observer")

        bp = OrganBlueprint(
            name="soma.memory.journal",
            description="Memory storage",
            dependencies=["soma.perception.observer"]
        )

        pending = {"soma.memory.journal": bp}
        buildable = genesis._get_buildable_organs(pending)

        assert len(buildable) == 1
        assert buildable[0][0] == "soma.memory.journal"

    def test_organ_with_unsatisfied_dependency_not_buildable(self):
        """Test that organs with unsatisfied dependencies are not buildable."""
        genesis = Genesis()
        # Don't mark the dependency as active

        bp = OrganBlueprint(
            name="soma.memory.journal",
            description="Memory storage",
            dependencies=["soma.perception.observer"]  # Not active
        )

        pending = {"soma.memory.journal": bp}
        buildable = genesis._get_buildable_organs(pending)

        assert len(buildable) == 0

    def test_wildcard_dependency_matching(self):
        """Test that wildcard dependencies work correctly."""
        genesis = Genesis()
        genesis.dna.mark_active("soma.perception.observer")
        genesis.dna.mark_active("soma.perception.analyzer")

        bp = OrganBlueprint(
            name="soma.memory.journal",
            description="Memory storage",
            dependencies=["soma.perception.*"]  # Wildcard
        )

        pending = {"soma.memory.journal": bp}
        buildable = genesis._get_buildable_organs(pending)

        assert len(buildable) == 1

    def test_multiple_dependencies(self):
        """Test organs with multiple dependencies."""
        genesis = Genesis()
        genesis.dna.mark_active("soma.perception.observer")
        genesis.dna.mark_active("soma.memory.journal")  # Mark both as active

        bp = OrganBlueprint(
            name="soma.interface.dashboard",
            description="UI dashboard",
            dependencies=[
                "soma.perception.observer",
                "soma.memory.journal"  # Now satisfied
            ]
        )

        pending = {"soma.interface.dashboard": bp}
        buildable = genesis._get_buildable_organs(pending)

        # Should be buildable since both dependencies are satisfied
        assert len(buildable) == 1


# =========================================
# Remote Logging Tests
# =========================================


class TestRemoteLoggingHandler:
    """Test remote logging with sanitization."""

    def test_handler_sanitizes_file_paths(self):
        """Test that file paths are sanitized."""
        handler = RemoteLoggingHandler(url="http://logging.example.com/logs")

        message = "Error in /home/user/project/file.py at line 42"
        sanitized = handler._sanitize_message(message)

        assert "/home/user" not in sanitized
        assert "<path>" in sanitized

    def test_handler_sanitizes_api_keys(self):
        """Test that potential API keys are masked."""
        handler = RemoteLoggingHandler(url="http://logging.example.com/logs")

        message = "Failed to authenticate with key: abcdef1234567890abcdef1234567890"
        sanitized = handler._sanitize_message(message)

        assert "abcdef1234567890abcdef1234567890" not in sanitized
        assert "<key>" in sanitized

    def test_handler_limits_message_length(self):
        """Test that long messages are truncated."""
        handler = RemoteLoggingHandler(url="http://logging.example.com/logs")

        long_message = "A" * 1000
        sanitized = handler._sanitize_message(long_message)

        assert len(sanitized) <= 500

    def test_handler_masks_urls(self):
        """Test that URLs in messages are masked."""
        handler = RemoteLoggingHandler(url="http://logging.example.com/logs")

        message = "Called http://localhost:11434/api/generate for model inference"
        sanitized = handler._sanitize_message(message)

        # URLs and paths are masked
        assert "localhost" not in sanitized
        assert "<path>" in sanitized  # Path parts replaced with <path>

    def test_handler_only_sends_warning_level(self):
        """Test that only WARNING+ logs are sent."""
        handler = RemoteLoggingHandler(url="http://logging.example.com/logs")

        import logging

        # Create mock records
        debug_record = MagicMock()
        debug_record.levelno = logging.DEBUG
        debug_record.getMessage.return_value = "Debug message"

        warning_record = MagicMock()
        warning_record.levelno = logging.WARNING
        warning_record.getMessage.return_value = "Warning message"

        # Debug should return empty (below threshold)
        result = handler._sanitize_record(debug_record)
        assert result == {}

        # Warning should return non-empty
        result = handler._sanitize_record(warning_record)
        assert result != {}

    def test_handler_queues_messages(self):
        """Test that messages are queued for batch sending."""
        handler = RemoteLoggingHandler(
            url="http://logging.example.com/logs",
            batch_size=2
        )

        import logging

        # Create mock records
        record = MagicMock()
        record.levelno = logging.WARNING
        record.getMessage.return_value = "Test message"
        record.levelname = "WARNING"
        record.name = "test.logger"
        record.created = 1234567890.0

        handler.emit(record)

        assert not handler._queue.empty()

    def test_setup_remote_logging_respects_disabled(self):
        """Test that remote logging respects disabled config."""
        # Save original config
        original_enabled = config.remote_logging.enabled
        try:
            config.remote_logging.enabled = False
            config.remote_logging.url = ""

            handler = setup_remote_logging()
            assert handler is None
        finally:
            config.remote_logging.enabled = original_enabled

    def test_remote_logging_handler_closes_cleanly(self):
        """Test that handler closes without errors."""
        handler = RemoteLoggingHandler(url="http://logging.example.com/logs")

        # Should not raise
        handler.close()
        assert not handler._running


# =========================================
# Integration Tests
# =========================================


class TestEnhancementsIntegration:
    """Integration tests for all enhancements together."""

    def test_dependency_ordering_in_evolution_cycle(self):
        """Test that dependencies are respected during evolution."""
        genesis = Genesis()

        # Create blueprints with dependencies
        perception_bp = OrganBlueprint(
            name="soma.perception.observer",
            description="Observe files",
            dependencies=[]
        )

        memory_bp = OrganBlueprint(
            name="soma.memory.journal",
            description="Memory storage",
            dependencies=["soma.perception.observer"]
        )

        # Mark perception as active
        genesis.dna.mark_active("soma.perception.observer")

        # Test the buildable organs filter directly
        pending = {
            "soma.perception.observer": perception_bp,
            "soma.memory.journal": memory_bp
        }
        buildable = genesis._get_buildable_organs(pending)
        buildable_names = [name for name, _ in buildable]

        # soma.memory.journal should be buildable (dependency satisfied)
        assert "soma.memory.journal" in buildable_names

    def test_event_retention_survives_across_publishes(self):
        """Test that events are retained across multiple publish calls."""
        bus = EventBus()
        bus.clear_subscribers()  # Reset for this test

        # Simulate organ evolution events
        for i in range(3):
            event = Event(
                event_type="organ.evolved",
                data={"organ": f"soma.organ{i}"},
                source="genesis"
            )
            bus.publish(event)

        retained = bus.get_retained_events(event_type="organ.evolved")
        assert len(retained) >= 3
