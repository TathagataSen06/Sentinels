import uuid
import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class MitreMapping(BaseModel):
    tactic: str
    tactic_id: str
    technique: str
    technique_id: str

class AnalyzedEvent(BaseModel):
    original_event_id: str
    source_ip: str
    plugin_name: str
    mitre_mapping: MitreMapping
    severity: int = Field(ge=0, le=100)
    confidence: int = Field(ge=0, le=100)
    timestamp: datetime.datetime

class Campaign(BaseModel):
    campaign_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_ip: str
    events: List[AnalyzedEvent] = Field(default_factory=list)
    start_time: datetime.datetime
    last_updated: datetime.datetime
    overall_severity: int = 0

# Static Mapping Dictionary for core plugins
PLUGIN_MITRE_MAP = {
    "ssh": {
        "tactic": "Credential Access",
        "tactic_id": "TA0006",
        "technique": "Brute Force",
        "technique_id": "T1110",
        "base_severity": 60,
        "base_confidence": 90
    },
    "http": {
        "tactic": "Reconnaissance",
        "tactic_id": "TA0043",
        "technique": "Active Scanning",
        "technique_id": "T1595",
        "base_severity": 30,
        "base_confidence": 70
    },
    "smb": {
        "tactic": "Lateral Movement",
        "tactic_id": "TA0008",
        "technique": "Remote Services: SMB/Windows Admin Shares",
        "technique_id": "T1021.002",
        "base_severity": 80,
        "base_confidence": 95
    }
}

class CorrelationEngine:
    def __init__(self):
        # In a real system, this would be backed by Redis or Neo4j
        # We store active campaigns keyed by source_ip
        self.active_campaigns: Dict[str, Campaign] = {}
        self.correlation_window_minutes = 60

    def analyze_event(self, event_data: Dict[str, Any]) -> AnalyzedEvent:
        """
        Takes a raw PluginEvent dict, maps it to MITRE, calculates scores, and returns an AnalyzedEvent.
        """
        plugin_name = event_data.get("plugin_name", "unknown")
        mapping_data = PLUGIN_MITRE_MAP.get(plugin_name, {
            "tactic": "Unknown", "tactic_id": "Unknown",
            "technique": "Unknown", "technique_id": "Unknown",
            "base_severity": 10, "base_confidence": 50
        })

        # Calculate dynamic severity (e.g., if credentials were used, bump severity)
        severity = mapping_data["base_severity"]
        if event_data.get("credentials_attempted"):
            severity = min(100, severity + 15)

        mitre = MitreMapping(
            tactic=mapping_data["tactic"],
            tactic_id=mapping_data["tactic_id"],
            technique=mapping_data["technique"],
            technique_id=mapping_data["technique_id"]
        )

        return AnalyzedEvent(
            original_event_id=event_data.get("id", str(uuid.uuid4())),
            source_ip=event_data.get("source_ip", "0.0.0.0"),
            plugin_name=plugin_name,
            mitre_mapping=mitre,
            severity=severity,
            confidence=mapping_data["base_confidence"],
            timestamp=datetime.datetime.utcnow()
        )

    def correlate(self, analyzed_event: AnalyzedEvent) -> Campaign:
        """
        Correlates an analyzed event into a campaign based on source IP and time window.
        """
        ip = analyzed_event.source_ip
        now = datetime.datetime.utcnow()

        if ip in self.active_campaigns:
            campaign = self.active_campaigns[ip]
            # Check if within time window
            if (now - campaign.last_updated).total_seconds() < (self.correlation_window_minutes * 60):
                campaign.events.append(analyzed_event)
                campaign.last_updated = now
                campaign.overall_severity = max(campaign.overall_severity, analyzed_event.severity)
                return campaign
        
        # Create new campaign
        new_campaign = Campaign(
            source_ip=ip,
            events=[analyzed_event],
            start_time=now,
            last_updated=now,
            overall_severity=analyzed_event.severity
        )
        self.active_campaigns[ip] = new_campaign
        return new_campaign
