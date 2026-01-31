from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import threading
import time
import psutil

logger = get_logger("soma.extensions.metrics")

class MetricsOrgan:
    def __init__(self):
        self.metrics = {
            'total_events': 0,
            'events_per_minute': 0,
            'active_organs_count': 0,
            'failed_organs_count': 0,
            'average_event_latency': 0.0,
            'organ_health_scores': {}
        }
        self.last_collection_time = time.time()
        self.event_count_last_interval = 0
        bus.subscribe('*', self.on_event)
        logger.info("Metrics organ initialized")

    def on_event(self, event):
        self.metrics['total_events'] += 1
        current_time = time.time()
        if current_time - self.last_collection_time >= 60:
            self.metrics['events_per_minute'] = (self.metrics['total_events'] - self.event_count_last_interval) / (current_time - self.last_collection_time)
            self.event_count_last_interval = self.metrics['total_events']
            self.last_collection_time = current_time

    def collect_system_metrics(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        return {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_info.percent
        }

    def publish_metrics(self):
        system_metrics = self.collect_system_metrics()
        metrics_data = {
            **self.metrics,
            **system_metrics
        }
        bus.publish(Event(event_type="metrics.collected", data=metrics_data))
        logger.info("Metrics collected and published")

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = MetricsOrgan()
    def collect_metrics():
        while True:
            if getattr(config.metrics, 'enabled', False):
                organ.publish_metrics()
            time.sleep(getattr(config.metrics, 'collection_interval_seconds', 5))
    thread = threading.Thread(target=collect_metrics, daemon=True)
    thread.start()