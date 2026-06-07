from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BasePlugin(ABC):
    """
    Base class for all Sentinels deception plugins (SSH, HTTP, SMB).
    """
    def __init__(self, config: dict, delivery_callback):
        self.config = config
        self.delivery_callback = delivery_callback
        self.is_running = False

    @abstractmethod
    async def start(self):
        """Start the honeypot listener."""
        pass

    @abstractmethod
    async def stop(self):
        """Stop the honeypot listener."""
        pass

    def emit_event(self, event_type: str, data: dict):
        """Send an event to the delivery module."""
        payload = {
            "type": event_type,
            "source_plugin": self.__class__.__name__,
            "data": data
        }
        self.delivery_callback(payload)
