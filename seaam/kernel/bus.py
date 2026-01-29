import threading
from typing import Callable, List, Dict, Any

class Event:
    def __init__(self, event_type: str, data: Any = None):
        self.event_type = event_type
        self.data = data

    def __repr__(self):
        return f"<Event type={self.event_type} data={self.data}>"

class EventBus:
    """
    The Nervous System.
    Allows decoupled components to communicate.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EventBus, cls).__new__(cls)
                    cls._instance.subscribers: Dict[str, List[Callable]] = {}
        return cls._instance

    def subscribe(self, event_type: str, callback: Callable[[Event], None]):
        """Attach a nerve ending (callback) to a specific stimulus (event_type)."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        print(f"[NERVOUS SYSTEM] Connected new synapse for '{event_type}'")

    def publish(self, event: Event):
        """Fire a signal across the nervous system."""
        if event.event_type in self.subscribers:
            print(f"[NERVOUS SYSTEM] Firing signal: {event.event_type} -> {len(self.subscribers[event.event_type])} listeners")
            for callback in self.subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[NERVOUS SYSTEM] Synapse failure: {e}")

# Global instance
bus = EventBus()
publish = bus.publish
subscribe = bus.subscribe
