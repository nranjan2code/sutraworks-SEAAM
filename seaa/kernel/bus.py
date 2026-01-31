"""
SEAA Event Bus (Nervous System)

A robust, async-capable event bus that serves as the central
communication mechanism between organs.

Features:
- Async/await native with synchronous wrapper
- Event queue with backpressure
- Unsubscribe mechanism (prevents memory leaks)
- Correlation IDs for tracing
- Timestamps on all events
- Graceful shutdown with drain
- Both sync and async subscribe/publish
"""

import asyncio
import threading
import queue
import time
import collections
from datetime import datetime
from typing import Callable, Any, Optional, List
from uuid import uuid4
from dataclasses import dataclass, field
from enum import Enum

from seaa.core.logging import get_logger
from seaa.core.config import config

logger = get_logger("bus")


@dataclass
class Event:
    """
    A typed event for the nervous system.
    
    All events have:
    - event_type: String identifier for routing
    - data: Optional payload
    - timestamp: When created
    - source: Which organ sent it
    - correlation_id: For tracing related events
    """
    event_type: str
    data: Any = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    source: str = "unknown"
    correlation_id: str = field(default_factory=lambda: str(uuid4())[:8])
    
    def __repr__(self):
        return f"<Event type={self.event_type} source={self.source} id={self.correlation_id}>"
    
    def with_response(self, response_type: str, data: Any = None) -> "Event":
        """Create a response event with the same correlation ID."""
        return Event(
            event_type=response_type,
            data=data,
            source=self.source,
            correlation_id=self.correlation_id,
        )


class SubscriptionHandle:
    """Handle returned when subscribing, used to unsubscribe."""
    
    def __init__(self, event_type: str, callback: Callable, unsubscribe_fn: Callable):
        self.event_type = event_type
        self.callback = callback
        self._unsubscribe = unsubscribe_fn
        self._active = True
    
    def unsubscribe(self) -> bool:
        """Unsubscribe this handler. Returns True if was active."""
        if self._active:
            self._unsubscribe()
            self._active = False
            return True
        return False
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.unsubscribe()


class EventBus:
    """
    The Nervous System.
    
    A singleton event bus that allows decoupled organs to communicate.
    Supports both synchronous and asynchronous usage patterns.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super(EventBus, cls).__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return

        self._subscribers: dict[str, list[Callable[[Event], None]]] = {}
        self._async_subscribers: dict[str, list[Callable[[Event], Any]]] = {}
        self._queue: queue.Queue = queue.Queue(maxsize=1000)  # Backpressure
        self._running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._sub_lock = threading.RLock()

        # Event retention (for debugging long-running systems)
        max_retained = getattr(config.event_bus, 'max_retained_events', 100)
        self._retained_events: collections.deque = collections.deque(maxlen=max_retained)
        self._retention_enabled = max_retained > 0

        self._initialized = True
        logger.debug(f"EventBus initialized (retention: {max_retained} events)")
    
    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Event], None],
    ) -> SubscriptionHandle:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The event type to listen for (e.g., 'file.changed')
            callback: Function to call when event fires
        
        Returns:
            SubscriptionHandle that can be used to unsubscribe
        """
        with self._sub_lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
        
        logger.debug(f"Subscribed to '{event_type}' ({len(self._subscribers[event_type])} listeners)")
        
        def unsubscribe():
            with self._sub_lock:
                if event_type in self._subscribers and callback in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(callback)
                    logger.debug(f"Unsubscribed from '{event_type}'")
        
        return SubscriptionHandle(event_type, callback, unsubscribe)
    
    def publish(self, event: Event) -> None:
        """
        Publish an event synchronously.

        Callbacks are invoked in the calling thread, one at a time.
        Exceptions in callbacks are caught and logged.
        """
        # Retain event for debugging (if enabled)
        if self._retention_enabled:
            self._retained_events.append(event)

        with self._sub_lock:
            listeners = list(self._subscribers.get(event.event_type, []))

        if not listeners:
            logger.debug(f"No listeners for event: {event.event_type}")
            return

        logger.debug(f"Publishing: {event.event_type} -> {len(listeners)} listeners")

        for callback in listeners:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Subscriber error for {event.event_type}: {e}")
    
    def publish_async(self, event: Event) -> None:
        """
        Queue an event for async processing.
        
        Events are processed by a background worker thread.
        Use this when you don't want to block the caller.
        """
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            logger.warning(f"Event queue full, dropping: {event.event_type}")
    
    def start_worker(self) -> None:
        """Start the background worker for async events."""
        if self._running:
            return
        
        self._running = True
        self._worker_thread = threading.Thread(
            target=self._worker_loop,
            name="eventbus-worker",
            daemon=True,
        )
        self._worker_thread.start()
        logger.info("EventBus worker started")
    
    def stop_worker(self, drain: bool = True, timeout: float = 5.0) -> None:
        """
        Stop the background worker.
        
        Args:
            drain: If True, process remaining events before stopping
            timeout: Max seconds to wait for drain
        """
        if not self._running:
            return
        
        self._running = False
        
        if drain:
            start = time.time()
            while not self._queue.empty() and (time.time() - start) < timeout:
                time.sleep(0.1)
        
        # Signal worker to stop by adding sentinel
        self._queue.put(None)
        
        if self._worker_thread:
            self._worker_thread.join(timeout=1.0)
        
        logger.info("EventBus worker stopped")
    
    def _worker_loop(self) -> None:
        """Background worker that processes async events."""
        while self._running:
            try:
                event = self._queue.get(timeout=0.5)
                if event is None:  # Sentinel
                    break
                self.publish(event)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def get_subscriber_count(self, event_type: Optional[str] = None) -> int:
        """Get number of subscribers for an event type (or total)."""
        with self._sub_lock:
            if event_type:
                return len(self._subscribers.get(event_type, []))
            return sum(len(subs) for subs in self._subscribers.values())
    
    def get_queue_size(self) -> int:
        """Get current size of the async event queue."""
        return self._queue.qsize()

    def get_retained_events(self, count: Optional[int] = None, event_type: Optional[str] = None) -> List[Event]:
        """
        Get recent retained events.

        Args:
            count: Maximum number of events to return (default: all)
            event_type: Filter by event type (default: all types)

        Returns:
            List of recent events, most recent last
        """
        events = list(self._retained_events)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if count:
            events = events[-count:]

        return events

    def get_retained_count(self) -> int:
        """Get number of retained events."""
        return len(self._retained_events)

    def clear_subscribers(self, event_type: Optional[str] = None) -> None:
        """
        Clear all subscribers (for testing or reset).
        
        Args:
            event_type: If provided, only clear this type. Otherwise clear all.
        """
        with self._sub_lock:
            if event_type:
                self._subscribers.pop(event_type, None)
            else:
                self._subscribers.clear()
        logger.debug(f"Cleared subscribers: {event_type or 'all'}")
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (for testing).
        """
        with cls._lock:
            if cls._instance:
                cls._instance.stop_worker(drain=False)
                cls._instance = None


# Convenience: Global singleton instance
bus = EventBus()

# Convenience: Module-level functions for common operations
def publish(event: Event) -> None:
    """Publish an event to the global bus."""
    bus.publish(event)

def subscribe(event_type: str, callback: Callable[[Event], None]) -> SubscriptionHandle:
    """Subscribe to events on the global bus."""
    return bus.subscribe(event_type, callback)

def create_event(event_type: str, data: Any = None, source: str = "unknown") -> Event:
    """Helper to create an event."""
    return Event(event_type=event_type, data=data, source=source)
