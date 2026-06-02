from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class IntelResult(BaseModel):
    """
    Standardized schema for Threat Intelligence enrichment.
    """
    provider_name: str
    ip_address: str
    is_malicious: bool
    confidence_score: int = Field(ge=0, le=100, default=0)
    tags: List[str] = Field(default_factory=list)
    raw_response: Dict[str, Any] = Field(default_factory=dict)
    asn: Optional[str] = None
    country: Optional[str] = None


class ThreatIntelProvider(ABC):
    """
    Base Interface for all Threat Intelligence providers (e.g. VirusTotal, AbuseIPDB).
    """

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def lookup_ip(self, ip_address: str) -> IntelResult:
        """
        Query the provider for IP reputation and return a standardized IntelResult.
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Return the name of the provider.
        """
        pass
