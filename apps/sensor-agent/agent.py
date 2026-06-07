import asyncio
import random
import logging
import uuid
import httpx

from core.config import ConfigManager
from core.delivery import DeliveryModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorAgent:
    def __init__(self, api_url: str, bootstrap_token: str):
        self.api_url = api_url
        self.bootstrap_token = bootstrap_token
        self.config = ConfigManager()
        self.delivery = DeliveryModule(api_url)

    async def generate_csr(self):
        logger.info("Generating RSA Keypair and CSR...")
        await asyncio.sleep(0.5)
        return "-----BEGIN CERTIFICATE REQUEST-----\nMOCK_CSR\n-----END CERTIFICATE REQUEST-----"

    async def enroll(self):
        if self.config.is_enrolled():
            logger.info("Agent already enrolled. Bypassing enrollment.")
            return

        logger.info("Starting enrollment process...")
        csr_pem = await self.generate_csr()
        
        payload = {
            "bootstrap_token": self.bootstrap_token,
            "csr_pem": csr_pem,
            "platform": "Linux",
            "version": "1.0.0"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f"{self.api_url}/api/v1/sensors/enroll", json=payload)
                response.raise_for_status()
                data = response.json()
                
                self.config.update("sensor_uuid", data["sensor_uuid"])
                self.config.update("tenant_uuid", data["tenant_uuid"])
                self.config.update("client_certificate_pem", data["client_certificate_pem"])
                self.config.update("base_interval", data["base_heartbeat_interval"])
                self.config.update("jitter", data["heartbeat_jitter"])
                
                logger.info(f"Enrollment successful. Assigned UUID: {self.config.get('sensor_uuid')}")
            except Exception as e:
                logger.error(f"Enrollment failed: {e}")
                raise

    async def heartbeat_loop(self):
        sensor_uuid = self.config.get("sensor_uuid")
        if not sensor_uuid:
            logger.error("Cannot start heartbeat: Sensor not enrolled.")
            return

        async with httpx.AsyncClient() as client:
            while True:
                base = self.config.get("base_interval", 60)
                jitter = self.config.get("jitter", 15)
                offset = random.randint(-jitter, jitter)
                delay = max(10, base + offset)
                
                logger.info(f"Next heartbeat in {delay} seconds")
                await asyncio.sleep(delay)
                
                payload = {
                    "sensor_uuid": sensor_uuid,
                    "status": "ONLINE",
                    "active_honeypots": 3,
                    "metrics": {"cpu": 12.5, "ram_mb": 256}
                }
                
                try:
                    response = await client.post(f"{self.api_url}/api/v1/sensors/heartbeat", json=payload)
                    response.raise_for_status()
                    data = response.json()
                    
                    self.config.update("base_interval", data["next_heartbeat_base"])
                    self.config.update("jitter", data["next_heartbeat_jitter"])
                    logger.info("Heartbeat acknowledged.")
                    
                except Exception as e:
                    logger.warning(f"Heartbeat failed (Offline Operation Active): {e}")

async def main():
    agent = SensorAgent(api_url="http://localhost:8000", bootstrap_token="deploy-token-xyz")
    await agent.enroll()
    
    # Run loops concurrently
    await asyncio.gather(
        agent.heartbeat_loop(),
        agent.delivery.delivery_loop()
    )

if __name__ == "__main__":
    asyncio.run(main())
