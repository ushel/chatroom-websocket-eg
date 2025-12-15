# pubsub/pubsub.py
import asyncio
from typing import Callable, Dict, List


class PubSub:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, topic: str, callback: Callable):
        """Subscribe a callback only once per topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []

        # Prevent duplicate subscription
        if callback not in self.subscribers[topic]:
            self.subscribers[topic].append(callback)

    async def publish(self, topic: str, message: str):
        """Call all subscriber callbacks for this topic."""
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                await callback(message)


pubsub = PubSub()
