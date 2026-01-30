"""
Unit tests for the EventBus (Nervous System)
"""

import pytest
import time
import threading
from seaa.kernel.bus import EventBus, Event, bus, subscribe, publish


class TestEvent:
    """Tests for the Event class."""
    
    def test_event_creation(self):
        """Test basic event creation."""
        event = Event(event_type="test.event", data={"key": "value"})
        
        assert event.event_type == "test.event"
        assert event.data == {"key": "value"}
        assert event.source == "unknown"
        assert event.correlation_id is not None
        assert event.timestamp is not None
    
    def test_event_with_source(self):
        """Test event with custom source."""
        event = Event(
            event_type="test.event",
            data="test",
            source="test_module"
        )
        assert event.source == "test_module"
    
    def test_event_response(self):
        """Test creating response events with same correlation ID."""
        original = Event(event_type="request", data="hello")
        response = original.with_response("response", data="world")
        
        assert response.event_type == "response"
        assert response.data == "world"
        assert response.correlation_id == original.correlation_id


class TestEventBus:
    """Tests for the EventBus class."""
    
    def test_singleton(self, reset_event_bus):
        """Test EventBus is a singleton."""
        bus1 = EventBus()
        bus2 = EventBus()
        assert bus1 is bus2
    
    def test_subscribe_and_publish(self, reset_event_bus):
        """Test basic subscribe/publish flow."""
        bus = EventBus()
        received = []
        
        def handler(event):
            received.append(event)
        
        bus.subscribe("test.event", handler)
        bus.publish(Event(event_type="test.event", data="hello"))
        
        assert len(received) == 1
        assert received[0].data == "hello"
    
    def test_multiple_subscribers(self, reset_event_bus):
        """Test multiple subscribers to same event."""
        bus = EventBus()
        calls = {"a": 0, "b": 0}
        
        def handler_a(event):
            calls["a"] += 1
        
        def handler_b(event):
            calls["b"] += 1
        
        bus.subscribe("multi.event", handler_a)
        bus.subscribe("multi.event", handler_b)
        bus.publish(Event(event_type="multi.event"))
        
        assert calls["a"] == 1
        assert calls["b"] == 1
    
    def test_unsubscribe(self, reset_event_bus):
        """Test unsubscribing from events."""
        bus = EventBus()
        calls = 0
        
        def handler(event):
            nonlocal calls
            calls += 1
        
        handle = bus.subscribe("unsub.event", handler)
        
        bus.publish(Event(event_type="unsub.event"))
        assert calls == 1
        
        handle.unsubscribe()
        
        bus.publish(Event(event_type="unsub.event"))
        assert calls == 1  # Still 1, not called again
    
    def test_no_listeners(self, reset_event_bus):
        """Test publishing to event with no listeners."""
        bus = EventBus()
        # Should not raise
        bus.publish(Event(event_type="no.listeners"))
    
    def test_handler_exception(self, reset_event_bus):
        """Test that handler exceptions don't break other handlers."""
        bus = EventBus()
        calls = []
        
        def bad_handler(event):
            raise ValueError("Test error")
        
        def good_handler(event):
            calls.append(event)
        
        bus.subscribe("error.event", bad_handler)
        bus.subscribe("error.event", good_handler)
        
        # Should not raise, good_handler should still be called
        bus.publish(Event(event_type="error.event"))
        assert len(calls) == 1
    
    def test_subscriber_count(self, reset_event_bus):
        """Test getting subscriber counts."""
        bus = EventBus()
        
        bus.subscribe("count.a", lambda e: None)
        bus.subscribe("count.a", lambda e: None)
        bus.subscribe("count.b", lambda e: None)
        
        assert bus.get_subscriber_count("count.a") == 2
        assert bus.get_subscriber_count("count.b") == 1
        assert bus.get_subscriber_count("count.c") == 0
        assert bus.get_subscriber_count() == 3  # Total


class TestAsyncEventBus:
    """Tests for async event processing."""
    
    def test_async_publish(self, reset_event_bus):
        """Test async event publishing via worker."""
        bus = EventBus()
        received = []
        event_received = threading.Event()
        
        def handler(event):
            received.append(event)
            event_received.set()
        
        bus.subscribe("async.event", handler)
        bus.start_worker()
        
        bus.publish_async(Event(event_type="async.event", data="async"))
        
        # Wait for event to be processed
        assert event_received.wait(timeout=2.0)
        assert len(received) == 1
        assert received[0].data == "async"
        
        bus.stop_worker()
    
    def test_worker_stop_drain(self, reset_event_bus):
        """Test worker drains queue on stop."""
        bus = EventBus()
        processed = []
        all_done = threading.Event()
        
        def handler(event):
            processed.append(event)
            if len(processed) >= 3:
                all_done.set()
        
        bus.subscribe("drain.event", handler)
        bus.start_worker()
        
        for i in range(3):
            bus.publish_async(Event(event_type="drain.event", data=i))
        
        # Wait for processing, then stop
        all_done.wait(timeout=5.0)
        bus.stop_worker(drain=True, timeout=2.0)
        
        assert len(processed) == 3


class TestModuleFunctions:
    """Test module-level convenience functions."""
    
    def test_module_subscribe_publish(self, reset_event_bus):
        """Test module-level subscribe and publish."""
        received = []
        
        handle = subscribe("module.event", lambda e: received.append(e))
        publish(Event(event_type="module.event", data="test"))
        
        assert len(received) == 1
        handle.unsubscribe()
