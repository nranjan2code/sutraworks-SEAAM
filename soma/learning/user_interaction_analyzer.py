from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import threading
import time

logger = get_logger("soma.learning.user_interaction_analyzer")

class UserInteractionAnalyzer:
    def __init__(self):
        bus.subscribe('user.interaction', self.on_user_interaction)
        self.feedback_data = []
        self.lock = threading.Lock()

    def on_user_interaction(self, event):
        with self.lock:
            self.feedback_data.append({
                'timestamp': time.time(),
                'user_id': event.data.get('user_id'),
                'interaction_type': event.data['interaction_type'],
                'outcome': event.data['outcome']
            })
            logger.info(f"Received user interaction: {event.data}")

    def retrain_model(self):
        with self.lock:
            if not self.feedback_data:
                return

            # Simulate model retraining logic
            logger.info("Retraining model with new feedback data")
            # Here you would typically call a function to retrain the model
            # For example: soma.learning.predictive_model.retrain(self.feedback_data)
            self.feedback_data.clear()

# REQUIRED ENTRY POINT (zero required args)
def start():
    analyzer = UserInteractionAnalyzer()
    
    def periodic_retraining():
        while True:
            time.sleep(getattr(config, 'retraining_interval_seconds', 60))
            analyzer.retrain_model()

    thread = threading.Thread(target=periodic_retraining, daemon=True)
    thread.start()