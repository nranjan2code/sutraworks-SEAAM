from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import threading
import time
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Any, Callable

logger = get_logger("soma.learning.anomaly_detection")

class AnomalyDetection:
    def __init__(self):
        self.model = None
        self.historical_data = []
        self.lock = threading.Lock()
        
        bus.subscribe('metrics.collected', self.on_metrics_collected)
        bus.subscribe('predictions.made', self.on_predictions_made)

        # Start a background thread to train the model periodically
        def train_model():
            while True:
                with self.lock:
                    if len(self.historical_data) > 100:  # Train only when there is enough data
                        self.train_isolation_forest()
                time.sleep(getattr(config.metrics, 'collection_interval_seconds', 5))
        
        thread = threading.Thread(target=train_model, daemon=True)
        thread.start()

    def on_metrics_collected(self, event):
        with self.lock:
            self.historical_data.append(event.data['value'])
            if len(self.historical_data) > 1000:  # Limit the size of historical data
                self.historical_data.pop(0)

    def on_predictions_made(self, event):
        if self.model is None:
            return
        
        prediction = event.data['prediction']
        anomaly_score = self.model.decision_function([[prediction]])[0]
        
        if anomaly_score < -0.5:  # Threshold for anomaly detection
            bus.publish(Event(
                event_type='anomaly.detected',
                data={
                    'type': 'Prediction Anomaly',
                    'timestamp': time.time(),
                    'affected_organ': 'soma.learning.predictive_model',
                    'severity': 'High'
                }
            ))

    def train_isolation_forest(self):
        if len(self.historical_data) < 10:
            return
        
        X = np.array(self.historical_data).reshape(-1, 1)
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.model.fit(X)

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = AnomalyDetection()