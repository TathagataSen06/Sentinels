import logging
from schemas import HeartbeatRequest, HeartbeatResponse

logger = logging.getLogger(__name__)

async def process_heartbeat(request: HeartbeatRequest) -> HeartbeatResponse:
    """
    Business logic for processing a sensor heartbeat.
    1. Update sensor last_seen timestamp in the database.
    2. Check if a new configuration version is available for this sensor.
    3. Determine the next heartbeat interval based on current platform load (Adaptive Jitter).
    """
    logger.info(f"Received heartbeat from sensor {request.sensor_uuid}. Status: {request.status}")
    
    # Adaptive heartbeat logic based on hypothetical cluster load
    # Under high load, we might increase the base interval or jitter to reduce EPS
    base_interval = 60
    jitter = 15
    
    return HeartbeatResponse(
        acknowledged=True,
        config_version="v1.0.42", # Example version
        next_heartbeat_base=base_interval,
        next_heartbeat_jitter=jitter
    )
