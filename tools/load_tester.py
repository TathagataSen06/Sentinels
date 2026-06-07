import asyncio
import httpx
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"
NUM_SENSORS = 1000

async def simulate_sensor(sensor_id: int):
    """Simulate a single sensor enrolling and heartbeating."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Enrollment
        enroll_payload = {
            "bootstrap_token": "load-test-token",
            "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\nMOCK\n-----END CERTIFICATE REQUEST-----",
            "platform": "Linux",
            "version": "1.0.0"
        }
        
        try:
            start_time = time.time()
            resp = await client.post(f"{API_URL}/api/v1/sensors/enroll", json=enroll_payload)
            resp.raise_for_status()
            enroll_latency = time.time() - start_time
            data = resp.json()
            sensor_uuid = data["sensor_uuid"]
        except Exception as e:
            logger.error(f"Sensor {sensor_id} enrollment failed: {e}")
            return None, None

        # Heartbeat
        heartbeat_payload = {
            "sensor_uuid": sensor_uuid,
            "status": "ONLINE",
            "active_honeypots": 3,
            "metrics": {"cpu": 10.0, "ram_mb": 128}
        }
        
        try:
            start_time = time.time()
            resp = await client.post(f"{API_URL}/api/v1/sensors/heartbeat", json=heartbeat_payload)
            resp.raise_for_status()
            heartbeat_latency = time.time() - start_time
        except Exception as e:
            logger.error(f"Sensor {sensor_uuid} heartbeat failed: {e}")
            return enroll_latency, None
            
        return enroll_latency, heartbeat_latency

async def main():
    logger.info(f"Starting load test with {NUM_SENSORS} concurrent sensors...")
    start_time = time.time()
    
    tasks = [simulate_sensor(i) for i in range(NUM_SENSORS)]
    results = await asyncio.gather(*tasks)
    
    total_time = time.time() - start_time
    
    successful_enrollments = [r[0] for r in results if r[0] is not None]
    successful_heartbeats = [r[1] for r in results if r[1] is not None]
    
    if successful_enrollments:
        avg_enroll = sum(successful_enrollments) / len(successful_enrollments)
        logger.info(f"Enrollments: {len(successful_enrollments)}/{NUM_SENSORS}. Avg Latency: {avg_enroll*1000:.2f}ms")
    
    if successful_heartbeats:
        avg_hb = sum(successful_heartbeats) / len(successful_heartbeats)
        logger.info(f"Heartbeats: {len(successful_heartbeats)}/{NUM_SENSORS}. Avg Latency: {avg_hb*1000:.2f}ms")
        
    logger.info(f"Total test duration: {total_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(main())
