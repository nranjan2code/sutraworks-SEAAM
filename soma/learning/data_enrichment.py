from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import threading
import time
import json
import os
import re
from typing import Any, Callable

logger = get_logger("soma.learning.data_enrichment")

class DataEnrichmentOrgan:
    def __init__(self):
        bus.subscribe('file.created', self.on_file_created)
        bus.subscribe('metrics.collected', self.on_metrics_collected)
        bus.subscribe('user.interaction', self.on_user_interaction)
        # Access config using attribute access:
        self.llm_model = getattr(config.llm, 'model', 'default_model')
        self.paths_soma = getattr(config.paths, 'soma', '/path/to/soma')

    def on_file_created(self, event: Event):
        file_path = event.data.get('file_path')
        if not file_path:
            logger.warning("File path missing in event data")
            return

        try:
            with open(file_path, 'r') as file:
                raw_data = file.read()
                enriched_data = self.enrich_data(raw_data)
                metadata = {
                    'source': 'file',
                    'path': file_path,
                    'timestamp': time.time(),
                    'model_used': self.llm_model
                }
                bus.publish(Event(event_type='data.enriched', data={'enriched_data': enriched_data, 'metadata': metadata}))
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")

    def on_metrics_collected(self, event: Event):
        metrics = event.data.get('metrics')
        if not metrics:
            logger.warning("Metrics missing in event data")
            return

        try:
            enriched_metrics = self.enrich_data(json.dumps(metrics))
            metadata = {
                'source': 'metrics',
                'timestamp': time.time(),
                'model_used': self.llm_model
            }
            bus.publish(Event(event_type='data.enriched', data={'enriched_data': enriched_metrics, 'metadata': metadata}))
        except Exception as e:
            logger.error(f"Error processing metrics: {e}")

    def on_user_interaction(self, event: Event):
        interaction = event.data.get('interaction')
        if not interaction:
            logger.warning("Interaction missing in event data")
            return

        try:
            enriched_interaction = self.enrich_data(interaction)
            metadata = {
                'source': 'user',
                'timestamp': time.time(),
                'model_used': self.llm_model
            }
            bus.publish(Event(event_type='data.enriched', data={'enriched_data': enriched_interaction, 'metadata': metadata}))
        except Exception as e:
            logger.error(f"Error processing user interaction: {e}")

    def enrich_data(self, raw_data: str) -> str:
        # Placeholder for actual NLP and ML enrichment logic
        # For demonstration, we'll just add some context to the data
        enriched_data = f"Enriched with model {self.llm_model}: {raw_data}"
        return enriched_data

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = DataEnrichmentOrgan()
    # Loop or wait if needed, but this organ doesn't require a background thread