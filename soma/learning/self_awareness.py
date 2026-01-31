from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import threading
import time

logger = get_logger("soma.learning.self_awareness")

class SelfAwarenessOrgan:
    def __init__(self):
        self.learning_rate = getattr(config, 'learning_rate', 0.01)
        self.model_complexity = getattr(config, 'model_complexity', 1)
        self.current_algorithm = getattr(config, 'algorithm', 'linear')
        
        bus.subscribe('metrics.collected', self.on_metrics_collected)
        bus.subscribe('feedback_loop.updated', self.on_feedback_updated)

    def on_metrics_collected(self, event):
        metrics = event.data
        accuracy = metrics.get('accuracy', 0.5)  # Default to 0.5 if not present

        if accuracy < 0.7:
            self.adjust_learning_rate(0.1)
        elif accuracy > 0.9:
            self.increase_model_complexity()

    def on_feedback_updated(self, event):
        feedback = event.data
        effectiveness = feedback.get('effectiveness', 0.5)  # Default to 0.5 if not present

        if effectiveness < 0.3:
            self.switch_algorithm('decision_tree')
        elif effectiveness > 0.8:
            self.decrease_model_complexity()

    def adjust_learning_rate(self, new_rate):
        self.learning_rate = new_rate
        logger.info(f"Adjusted learning rate to {new_rate}")
        bus.publish(Event(event_type="parameters.adjusted", data={
            "type": "learning_rate",
            "value": new_rate,
            "timestamp": time.time(),
            "rationale": "Accuracy was below threshold"
        }))

    def increase_model_complexity(self):
        self.model_complexity += 1
        logger.info(f"Increased model complexity to {self.model_complexity}")
        bus.publish(Event(event_type="parameters.adjusted", data={
            "type": "model_complexity",
            "value": self.model_complexity,
            "timestamp": time.time(),
            "rationale": "Accuracy was above threshold"
        }))

    def decrease_model_complexity(self):
        if self.model_complexity > 1:
            self.model_complexity -= 1
            logger.info(f"Decreased model complexity to {self.model_complexity}")
            bus.publish(Event(event_type="parameters.adjusted", data={
                "type": "model_complexity",
                "value": self.model_complexity,
                "timestamp": time.time(),
                "rationale": "Effectiveness was above threshold"
            }))

    def switch_algorithm(self, new_algorithm):
        self.current_algorithm = new_algorithm
        logger.info(f"Switched algorithm to {new_algorithm}")
        bus.publish(Event(event_type="parameters.adjusted", data={
            "type": "algorithm",
            "value": new_algorithm,
            "timestamp": time.time(),
            "rationale": "Effectiveness was below threshold"
        }))

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = SelfAwarenessOrgan()