import asyncio
import json
import logging
import sqlite3
import httpx
import uuid
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add schemas to path so we can import the compiled protobuf
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from schemas import sensor_event_pb2

logger = logging.getLogger(__name__)

class DeliveryModule:
    def __init__(self, config: dict):
        self.api_url = config.get("api_url", "http://localhost:8000")
        self.sensor_uuid = str(config.get("sensor_uuid", uuid.uuid4()))
        self.tenant_id = str(config.get("tenant_id", "default-tenant"))
        self.db_path = config.get("buffer_db", "events.db")
        self.batch_size = config.get("batch_size", 50)
        self.max_retries = config.get("max_retries", 5)
        
        self.init_db()
        self.queue = asyncio.Queue()
        self.is_running = False

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS event_buffer (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE,
                    payload BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
    def enqueue_event(self, source: str, data: dict):
        event_id = str(uuid.uuid4())
        
        # Construct Protobuf Envelope
        pb_event = sensor_event_pb2.SensorEvent()
        pb_event.event_id = event_id
        pb_event.sensor_uuid = self.sensor_uuid
        pb_event.event_type = source
        pb_event.timestamp = datetime.now(timezone.utc).isoformat()
        pb_event.source_plugin = source.split('.')[0] if '.' in source else source
        pb_event.tenant_id = self.tenant_id
        pb_event.payload_json = json.dumps(data)
        
        # Serialize to binary
        serialized_payload = pb_event.SerializeToString()
        
        # Write to SQLite offline buffer
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO event_buffer (event_id, payload) VALUES (?, ?)",
                (event_id, serialized_payload)
            )
            
        logger.debug(f"Event {event_id} ({source}) serialized via Protobuf and buffered to disk.")
        self.queue.put_nowait(event_id)

    async def delivery_loop(self):
        self.is_running = True
        logger.info("Delivery loop started.")
        
        while self.is_running:
            try:
                # Wait for events to be queued or poll the DB
                await asyncio.sleep(1)
                
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "SELECT id, event_id, payload FROM event_buffer ORDER BY id ASC LIMIT ?",
                        (self.batch_size,)
                    )
                    rows = cursor.fetchall()
                    
                if not rows:
                    continue
                    
                # We have events to send
                ids_to_delete = []
                for row in rows:
                    db_id, event_id, payload_bytes = row
                    success = await self._send_event(payload_bytes)
                    if success:
                        ids_to_delete.append(db_id)
                        
                if ids_to_delete:
                    with sqlite3.connect(self.db_path) as conn:
                        placeholders = ','.join('?' for _ in ids_to_delete)
                        conn.execute(f"DELETE FROM event_buffer WHERE id IN ({placeholders})", ids_to_delete)
                        
            except Exception as e:
                logger.error(f"Error in delivery loop: {e}")
                await asyncio.sleep(5)

    async def _send_event(self, payload_bytes: bytes) -> bool:
        # Exponential backoff retry logic
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    # In a real system, this would hit the API Gateway or Kafka Proxy
                    # We are simulating a generic delivery endpoint
                    response = await client.post(
                        f"{self.api_url}/api/v1/telemetry", 
                        content=payload_bytes,
                        headers={"Content-Type": "application/x-protobuf"}
                    )
                    response.raise_for_status()
                    return True
            except httpx.RequestError as e:
                wait_time = 2 ** attempt
                logger.warning(f"Delivery failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
        
        logger.error("Max retries exceeded for event delivery.")
        return False
