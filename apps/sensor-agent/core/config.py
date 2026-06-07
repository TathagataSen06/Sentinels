import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self, state_file="state.json"):
        self.state_file = Path(state_file)
        self.state = {}
        self.load_state()

    def load_state(self):
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    self.state = json.load(f)
                logger.info(f"Loaded persistent state from {self.state_file}")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        else:
            logger.info("No existing state found. Agent requires enrollment.")

    def save_state(self):
        try:
            # Ensure secure permissions on Linux
            if not self.state_file.exists() and os.name == 'posix':
                self.state_file.touch(mode=0o600)
            
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=4)
            if os.name == 'posix':
                os.chmod(self.state_file, 0o600)
                
            logger.info("State successfully persisted.")
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def update(self, key, value):
        self.state[key] = value
        self.save_state()

    def get(self, key, default=None):
        return self.state.get(key, default)

    def is_enrolled(self) -> bool:
        return "sensor_uuid" in self.state and "client_certificate_pem" in self.state
