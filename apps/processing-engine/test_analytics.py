import pytest
import datetime
import json
from unittest.mock import AsyncMock
from analytics import CorrelationEngine, AnalyzedEvent

@pytest.mark.asyncio
async def test_analyze_event_ssh():
    redis_mock = AsyncMock()
    engine = CorrelationEngine(redis_mock)
    
    raw_event = {
        "id": "event-1",
        "plugin_name": "ssh",
        "source_ip": "192.168.1.10",
        "credentials_attempted": True
    }
    
    analyzed = engine.analyze_event(raw_event)
    
    assert analyzed.plugin_name == "ssh"
    assert analyzed.mitre_mapping.tactic_id == "TA0006"
    assert analyzed.severity == 75  # 60 base + 15 for credentials
    assert analyzed.source_ip == "192.168.1.10"

@pytest.mark.asyncio
async def test_analyze_event_unknown_plugin():
    redis_mock = AsyncMock()
    engine = CorrelationEngine(redis_mock)
    
    raw_event = {
        "plugin_name": "custom_plugin",
        "source_ip": "10.1.1.1"
    }
    
    analyzed = engine.analyze_event(raw_event)
    assert analyzed.severity == 10
    assert analyzed.mitre_mapping.tactic == "Unknown"

@pytest.mark.asyncio
async def test_correlate_new_campaign():
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None  # Simulating no existing campaign in Redis
    
    engine = CorrelationEngine(redis_mock)
    analyzed = engine.analyze_event({"plugin_name": "http", "source_ip": "10.0.0.5"})
    
    campaign = await engine.correlate(analyzed)
    
    assert campaign.source_ip == "10.0.0.5"
    assert len(campaign.events) == 1
    assert campaign.overall_severity == 30
    assert redis_mock.set.call_count == 1

@pytest.mark.asyncio
async def test_correlate_existing_campaign():
    redis_mock = AsyncMock()
    
    # Mock an existing campaign in Redis
    existing_campaign = {
        "campaign_id": "1234",
        "source_ip": "10.0.0.5",
        "events": [],
        "start_time": datetime.datetime.utcnow().isoformat(),
        "last_updated": datetime.datetime.utcnow().isoformat(),
        "overall_severity": 30
    }
    # Return bytes as redis-py often does
    redis_mock.get.return_value = json.dumps(existing_campaign).encode('utf-8')
    
    engine = CorrelationEngine(redis_mock)
    
    # New event with higher severity (SMB)
    analyzed = engine.analyze_event({"plugin_name": "smb", "source_ip": "10.0.0.5"})
    
    campaign = await engine.correlate(analyzed)
    
    assert campaign.source_ip == "10.0.0.5"
    assert len(campaign.events) == 1
    assert campaign.overall_severity == 80  # Severity should be upgraded to match the new higher-severity event
    assert redis_mock.set.call_count == 1
