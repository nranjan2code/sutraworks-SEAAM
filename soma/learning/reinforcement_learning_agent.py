from seaa.kernel.bus import bus, Event
from seaa.core.logging import get_logger
from seaa.core.config import config
import threading
import time
import numpy as np

logger = get_logger("soma.learning.reinforcement_learning_agent")

class ReinforcementLearningAgent:
    def __init__(self):
        self.policy = {}
        self.episodes = []
        self.gamma = 0.95
        self.alpha = 0.1
        self.epsilon = 0.1

        bus.subscribe('recommendation.executed', self.on_recommendation_executed)
        bus.subscribe('user.interaction', self.on_user_interaction)

    def on_recommendation_executed(self, event):
        recommendation_id = event.data.get('id')
        outcome = event.data.get('outcome')
        self.episodes.append((recommendation_id, outcome))

    def on_user_interaction(self, event):
        user_feedback = event.data.get('feedback')
        if user_feedback:
            self.update_policy(user_feedback)

    def update_policy(self, feedback):
        for episode in reversed(self.episodes):
            recommendation_id, outcome = episode
            if recommendation_id not in self.policy:
                self.policy[recommendation_id] = 0.5

            old_value = self.policy[recommendation_id]
            new_value = old_value + self.alpha * (feedback - old_value)
            self.policy[recommendation_id] = new_value

        self.episodes.clear()

    def select_action(self):
        if np.random.rand() < self.epsilon:
            return np.random.choice(list(self.policy.keys()))
        else:
            return max(self.policy, key=self.policy.get)

    def publish_policy_update(self):
        for recommendation_id, value in self.policy.items():
            bus.publish(Event(event_type="policy.update", data={"id": recommendation_id, "value": value}))

# REQUIRED ENTRY POINT (zero required args)
def start():
    agent = ReinforcementLearningAgent()

    def periodic_publish():
        while True:
            time.sleep(60)  # Adjust interval as needed
            agent.publish_policy_update()

    thread = threading.Thread(target=periodic_publish, daemon=True)
    thread.start()