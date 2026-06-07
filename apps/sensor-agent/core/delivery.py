import sqlite3
import json
import logging
import asyncio
import httpx

logger = logging.getLogger(__name__)

class DeliveryModule:
    def __init__(self, api_url: str, db_path="events.db"):
        self.api_url = api_url
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Limit DB size to prevent disk exhaustion (ring buffer concept)
            # A real implementation would prune the oldest events.

    def enqueue_event(self, event_data: dict):
        """Called by plugins to buffer events locally."""
        try:
            payload = json.dumps(event_data)
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('INSERT INTO events (payload) VALUES (?)', (payload,))
            logger.info("Event successfully queued locally.")
        except Exception as e:
            logger.error(f"Failed to enqueue event: {e}")

    async def delivery_loop(self):
        """Asynchronously flush events to the management API."""
        backoff = 1
        
        while True:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT id, payload FROM events ORDER BY id ASC LIMIT 50')
                    rows = cursor.fetchall()

                if not rows:
                    await asyncio.sleep(5)
                    continue

                events = [{"id": r[0], "payload": json.loads(r[1])} for r in rows]
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.api_url}/api/v1/sensors/events",
                        json={"events": [e["payload"] for e in events]}
                    )
                    response.raise_for_status()

                # If successful, delete from local DB
                event_ids = [str(e["id"]) for e in events]
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(f"DELETE FROM events WHERE id IN ({','.join(event_ids)})")
                
                logger.info(f"Successfully delivered {len(events)} events.")
                backoff = 1 # Reset backoff
                await asyncio.sleep(1)

            except Exception as e:
                logger.warning(f"Event delivery failed, buffering locally. Retrying in {backoff}s. Error: {e}")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 300) # Max backoff 5 mins
