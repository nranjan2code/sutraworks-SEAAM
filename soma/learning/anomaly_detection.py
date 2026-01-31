from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import threading
import time
import numpy as np
from sklearn.ensemble import IsolationForest

logger = get_logger("soma.learning.anomaly_detection")

class AnomalyDetection:
    def __init__(self):
        self.model = None
        self.historical_data = []
        self.lock = threading.Lock()
        
        # Subscribe to relevant events
        bus.subscribe('metrics.collected', self.on_metrics_collected)
        bus.subscribe('predictions.made', self.on_predictions_made)
        
        # Initialize the anomaly detection model
        self.initialize_model()

    def initialize_model(self):
        # Load historical data if available, otherwise start fresh
        try:
            with open(config.paths.soma + '/historical_data.npy', 'rb') as f:
                self.historical_data = np.load(f).tolist()
        except FileNotFoundError:
            logger.info("No historical data found. Starting with an empty dataset.")
        
        # Initialize the Isolation Forest model
        self.model = IsolationForest(contamination=0.1, random_state=42)
        if self.historical_data:
            self.model.fit(np.array(self.historical_data))

    def on_metrics_collected(self, event):
        metrics = event.data
        with self.lock:
            self.historical_data.append(metrics)
            # Re-train the model periodically or when enough data is collected
            if len(self.historical_data) % 100 == 0:
                self.model.fit(np.array(self.historical_data))
        
        # Save historical data to disk
        with open(config.paths.soma + '/historical_data.npy', 'wb') as f:
            np.save(f, np.array(self.historical_data))

    def on_predictions_made(self, event):
        predictions = event.data
        for prediction in predictions:
            if self.detect_anomaly(prediction):
                self.publish_anomaly_event(prediction)

    def detect_anomaly(self, data_point):
        # Predict anomalies using the model
        prediction = self.model.predict([data_point])
        return prediction == -1

    def publish_anomaly_event(self, data_point):
        anomaly_type = "Unknown"
        severity_level = "High"  # Placeholder for actual severity calculation
        affected_organ = "Unknown"  # Placeholder for actual organ identification
        
        event_data = {
            "type": anomaly_type,
            "timestamp": time.time(),
            "affected_organ": affected_organ,
            "severity_level": severity_level,
            "data_point": data_point
        }
        
        bus.publish(Event(event_type="anomaly.detected", data=event_data))
        logger.warning(f"Anomaly detected: {event_data}")

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = AnomalyDetection()
    # No need for a background thread here as we are only subscribing to events