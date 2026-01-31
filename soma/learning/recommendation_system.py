from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import threading
import time
from typing import Any, Callable, Dict

logger = get_logger("soma.learning.recommendation_system")

class RecommendationSystem:
    def __init__(self):
        self.predictions: Dict[str, Any] = {}
        self.user_feedback: Dict[str, Any] = {}
        bus.subscribe('predictions.updated', self.on_predictions_updated)
        bus.subscribe('user.feedback', self.on_user_feedback)

    def on_predictions_updated(self, event: Event):
        self.predictions = event.data
        logger.info("Received updated predictions")

    def on_user_feedback(self, event: Event):
        self.user_feedback[event.data['resource']] = event.data['feedback']
        logger.info(f"Received user feedback for resource {event.data['resource']}")

    def generate_recommendations(self) -> Dict[str, Any]:
        recommendations = []
        for resource, prediction in self.predictions.items():
            if resource not in self.user_feedback:
                confidence_score = 0.8
                recommendation = {
                    "type": "action",
                    "target_resource": resource,
                    "suggested_action": prediction['action'],
                    "confidence_score": confidence_score,
                    "timestamp": time.time()
                }
                recommendations.append(recommendation)
        return recommendations

    def publish_recommendations(self):
        recommendations = self.generate_recommendations()
        for recommendation in recommendations:
            bus.publish(Event(event_type="recommendation.generated", data=recommendation))

# REQUIRED ENTRY POINT (zero required args)
def start():
    organ = RecommendationSystem()
    threading.Thread(target=organ.publish_recommendations, daemon=True).start()