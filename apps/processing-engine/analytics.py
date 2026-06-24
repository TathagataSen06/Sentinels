import uuid
import datetime
import json
import asyncio
import os
import logging
import redis.asyncio as redis_async
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

logger = logging.getLogger("processing_engine")

MAX_CAMPAIGN_EVENTS = int(os.getenv("MAX_CAMPAIGN_EVENTS", "50"))


class MitreMapping(BaseModel):
    tactic: str
    tactic_id: str
    technique: str
    technique_id: str

class AnalyzedEvent(BaseModel):
    original_event_id: str
    source_ip: str
    plugin_name: str
    event_type: str = ""
    sensor_id: Optional[str] = None
    sensor_name: Optional[str] = None
    tenant_id: Optional[str] = None
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

# Human-readable incident titles keyed by the dominant plugin.
PLUGIN_TITLE_MAP = {
    "ssh": "SSH Brute Force Campaign",
    "http": "HTTP Reconnaissance",
    "smb": "SMB Lateral Movement",
}


def severity_label(score: int) -> str:
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 30:
        return "MEDIUM"
    return "LOW"


class CorrelationEngine:
    def __init__(self, redis_client: redis_async.Redis):
        self.redis = redis_client
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
            source_ip=event_data.get("source_ip") or "0.0.0.0",
            plugin_name=plugin_name,
            event_type=event_data.get("event_type", ""),
            sensor_id=event_data.get("sensor_id"),
            sensor_name=event_data.get("sensor_name"),
            tenant_id=event_data.get("tenant_id"),
            mitre_mapping=mitre,
            severity=severity,
            confidence=mapping_data["base_confidence"],
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

    async def correlate(self, analyzed_event: AnalyzedEvent) -> Campaign:
        """
        Correlates an analyzed event into a campaign based on tenant + source IP
        and time window. Uses Redis to persist state across instances.
        """
        ip = analyzed_event.source_ip
        now = datetime.datetime.now(datetime.timezone.utc)
        # Key on tenant + IP so campaigns never collide across tenants.
        redis_key = f"campaign:{analyzed_event.tenant_id}:{ip}"

        campaign_data = await self.redis.get(redis_key)

        if campaign_data:
            campaign = Campaign.model_validate_json(campaign_data)
            # Normalize naive timestamps to UTC before comparing against an
            # aware `now` (older state or hand-crafted input may be naive).
            last_updated = campaign.last_updated
            if last_updated.tzinfo is None:
                last_updated = last_updated.replace(tzinfo=datetime.timezone.utc)
            # Check if within time window
            if (now - last_updated).total_seconds() < (self.correlation_window_minutes * 60):
                campaign.events.append(analyzed_event)
                # Cap retained events so campaign state cannot grow unbounded.
                campaign.events = campaign.events[-MAX_CAMPAIGN_EVENTS:]
                campaign.last_updated = now
                campaign.overall_severity = max(campaign.overall_severity, analyzed_event.severity)
                await self.redis.set(redis_key, campaign.model_dump_json(), ex=self.correlation_window_minutes * 60 * 2)
                return campaign

        # Create new campaign
        new_campaign = Campaign(
            source_ip=ip,
            events=[analyzed_event],
            start_time=now,
            last_updated=now,
            overall_severity=analyzed_event.severity
        )
        await self.redis.set(redis_key, new_campaign.model_dump_json(), ex=self.correlation_window_minutes * 60 * 2)
        return new_campaign


def _normalize_dsn(url: str) -> str:
    """asyncpg wants a plain libpq DSN, not a SQLAlchemy dialect URL."""
    return (url or "").replace("+asyncpg", "").replace("+psycopg2", "").replace("+psycopg", "")


class IncidentStore:
    """Persists correlated campaigns to Postgres so the API and SOC dashboard
    read real incidents. Decoupled from the API's ORM — it owns only the upsert.
    """
    UPSERT_SQL = """
        INSERT INTO incidents (
            id, tenant_id, source_ip, title, severity, severity_score, status,
            sensor_name, mitre, event_count, events, first_seen, last_seen, created_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, 'NEW', $7, $8::jsonb, $9, $10::jsonb, $11, $12, $11
        )
        ON CONFLICT (tenant_id, source_ip) DO UPDATE SET
            title = EXCLUDED.title,
            severity = EXCLUDED.severity,
            severity_score = GREATEST(incidents.severity_score, EXCLUDED.severity_score),
            sensor_name = EXCLUDED.sensor_name,
            mitre = EXCLUDED.mitre,
            event_count = EXCLUDED.event_count,
            events = EXCLUDED.events,
            last_seen = EXCLUDED.last_seen;
    """

    def __init__(self, dsn: str):
        self.dsn = _normalize_dsn(dsn)
        self.pool = None

    async def connect(self):
        if self.pool is None:
            import asyncpg
            self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=5)

    async def upsert(self, campaign: Campaign, latest: AnalyzedEvent):
        if not latest.tenant_id:
            logger.debug("Skipping incident upsert: event has no tenant_id.")
            return
        await self.connect()

        score = campaign.overall_severity
        # Title derives from the highest-severity plugin seen in the campaign.
        dominant = max(campaign.events, key=lambda e: e.severity, default=latest)
        title = PLUGIN_TITLE_MAP.get(dominant.plugin_name, "Suspicious Activity")

        mitre = sorted({
            e.mitre_mapping.technique_id
            for e in campaign.events
            if e.mitre_mapping.technique_id and e.mitre_mapping.technique_id != "Unknown"
        })
        events_summary = [
            {
                "time": e.timestamp.isoformat(),
                "event_type": e.event_type,
                "plugin": e.plugin_name,
                "technique_id": e.mitre_mapping.technique_id,
                "tactic": e.mitre_mapping.tactic,
                "severity": e.severity,
            }
            for e in campaign.events
        ]

        async with self.pool.acquire() as conn:
            await conn.execute(
                self.UPSERT_SQL,
                uuid.uuid4(),                       # $1 id (kept only on insert)
                uuid.UUID(latest.tenant_id),        # $2 tenant_id
                campaign.source_ip,                 # $3 source_ip
                title,                              # $4 title
                severity_label(score),              # $5 severity
                score,                              # $6 severity_score
                latest.sensor_name,                 # $7 sensor_name
                json.dumps(mitre),                  # $8 mitre
                len(campaign.events),               # $9 event_count
                json.dumps(events_summary),         # $10 events
                campaign.start_time,                # $11 first_seen / created_at
                campaign.last_updated,              # $12 last_seen
            )

    async def close(self):
        if self.pool is not None:
            await self.pool.close()


async def run_worker():
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    redis_client = redis_async.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    engine = CorrelationEngine(redis_client)
    incident_store = IncidentStore(os.getenv("DATABASE_URL", ""))

    stream_name = "sentinels_events"
    group_name = "processing_group"

    try:
        await redis_client.xgroup_create(stream_name, group_name, mkstream=True)
    except Exception:
        # Group might already exist
        pass

    logger.info("Starting processing engine worker loop...")
    while True:
        try:
            results = await redis_client.xreadgroup(group_name, "worker-1", {stream_name: ">"}, count=10, block=2000)
            if results:
                for stream, messages in results:
                    for message_id, message_data in messages:
                        event_str = message_data.get(b"event", b"{}").decode("utf-8")
                        event_data = json.loads(event_str)

                        analyzed = engine.analyze_event(event_data)
                        campaign = await engine.correlate(analyzed)

                        try:
                            await incident_store.upsert(campaign, analyzed)
                        except Exception as e:
                            logger.error(f"Failed to persist incident: {e}")

                        logger.info(
                            "Processed event from %s, Campaign Severity: %s",
                            analyzed.source_ip, campaign.overall_severity)

                        await redis_client.xack(stream_name, group_name, message_id)
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_worker())
