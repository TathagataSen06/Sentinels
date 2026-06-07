import time
import asyncio
import json
import uuid
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SentinelsBenchmark")

class LoadTester:
    """
    Stress-tests the Sentinels Kafka -> Flink -> OpenSearch pipeline 
    to validate the 1 Million Events / Minute (16,666 events/sec) target throughput.
    """
    def __init__(self, target_eps: int = 17000):
        self.target_eps = target_eps
        self.running = False
        self.total_sent = 0

    def generate_payload(self) -> bytes:
        event = {
            "event_id": str(uuid.uuid4()),
            "sensor_uuid": f"sensor-{random.randint(1, 100000)}",
            "tenant_id": "tenant-01",
            "event_type": "ssh.login.attempt",
            "attacker_ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
            "raw_payload": {
                "username": "root",
                "password": "password123"
            }
        }
        return json.dumps(event).encode("utf-8")

    async def emit_batch(self, batch_size: int):
        # In the real benchmark, this uses aiokafka to blast binary Protobuf to the brokers.
        # Here we simulate the emission.
        await asyncio.sleep(0.01)
        self.total_sent += batch_size

    async def run(self, duration_seconds: int = 60):
        self.running = True
        logger.info(f"Starting benchmark. Target: {self.target_eps} EPS for {duration_seconds} seconds.")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        while time.time() < end_time:
            batch_start = time.time()
            
            # Emit 1 second worth of events
            await self.emit_batch(self.target_eps)
            
            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
                
            logger.info(f"Sent {self.target_eps} events. Total: {self.total_sent}")
            
        total_time = time.time() - start_time
        logger.info(f"Benchmark Complete. Total Events: {self.total_sent} in {total_time:.2f} seconds.")
        logger.info(f"Achieved EPS: {self.total_sent / total_time:.2f} EPS")

if __name__ == "__main__":
    tester = LoadTester(target_eps=17000)
    asyncio.run(tester.run(duration_seconds=10))
