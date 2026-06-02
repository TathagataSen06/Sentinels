from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import datetime
import uuid

class PluginEvent(BaseModel):
    """
    Standardized event schema that every plugin must emit.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    plugin_name: str
    source_ip: str
    source_port: Optional[int] = None
    destination_port: Optional[int] = None
    protocol: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    credentials_attempted: Optional[Dict[str, str]] = None


class SentinelsPlugin(ABC):
    """
    Base class for all Sentinels Deception Plugins.
    Every new plugin MUST inherit from this class and implement these four methods.
    """
    
    @abstractmethod
    def init(self, config: Dict[str, Any]) -> None:
        """
        Initialize the plugin with the provided configuration dictionary.
        This is where sockets should be prepared, but not necessarily bound.
        """
        pass
    
    @abstractmethod
    def start(self) -> None:
        """
        Start the plugin. It should begin listening for interactions and 
        yield or emit PluginEvent objects to the core agent.
        """
        pass
        
    @abstractmethod
    def stop(self) -> None:
        """
        Gracefully stop the plugin, closing any open sockets or resources.
        """
        pass
        
    @abstractmethod
    def health_check(self) -> bool:
        """
        Return True if the plugin is healthy and actively listening/functioning.
        """
        pass
