import os
import asyncio
import logging
import httpx
from pathlib import Path
from .base import BasePlugin

logger = logging.getLogger(__name__)

class CanaryCredentialsPlugin(BasePlugin):
    """
    Deploys deceptive credentials to isolated workspaces on the host filesystem
    and reports them back to the management API for global tracking.
    """
    def __init__(self, config: dict, delivery_callback):
        super().__init__(config, delivery_callback)
        self.aws_enabled = config.get("aws_keys", True)
        self.ssh_enabled = config.get("ssh_keys", True)
        self.canary_token = config.get("canary_token", "AKIAIOSFODNN7EXAMPLE")
        self.deception_workspace = Path(config.get("workspace", "/tmp/sentinels_deception"))
        self.api_url = config.get("api_url", "http://localhost:8000")
        self.sensor_uuid = config.get("sensor_uuid", "00000000-0000-0000-0000-000000000000")
        
    async def report_asset_to_api(self, asset_type: str, asset_path: str, asset_value: str):
        payload = {
            "sensor_uuid": self.sensor_uuid,
            "asset_type": asset_type,
            "asset_path": str(asset_path),
            "asset_value": asset_value
        }
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(f"{self.api_url}/api/v1/assets/report", json=payload)
                resp.raise_for_status()
                logger.info(f"Successfully reported {asset_type} asset to Management API.")
        except Exception as e:
            logger.error(f"Failed to report asset to API: {e}")

    async def deploy_aws_credentials(self):
        aws_dir = self.deception_workspace / ".aws"
        creds_file = aws_dir / "credentials"
        
        try:
            if not aws_dir.exists():
                aws_dir.mkdir(parents=True, mode=0o700, exist_ok=True)
                
            if not creds_file.exists():
                fake_creds = f"[default]\naws_access_key_id = {self.canary_token}\naws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n"
                with open(creds_file, "w") as f:
                    f.write(fake_creds)
                os.chmod(creds_file, 0o600)
                logger.info(f"Deployed Canary AWS credentials to isolated path: {creds_file}")
                self.emit_event("canary.deployed.aws", {"path": str(creds_file)})
                
                await self.report_asset_to_api("AWS_KEY", str(creds_file), self.canary_token)
        except Exception as e:
            logger.error(f"Failed to deploy AWS canary credentials: {e}")

    async def deploy_ssh_key(self):
        ssh_dir = self.deception_workspace / ".ssh"
        key_file = ssh_dir / "id_rsa_backup"
        
        try:
            if not ssh_dir.exists():
                ssh_dir.mkdir(parents=True, mode=0o700, exist_ok=True)
                
            if not key_file.exists():
                fake_key = f"-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW\nQyNTUxOQAAACB/FakeCanaryKey{self.canary_token}ExampleDataXYZ123==\n-----END OPENSSH PRIVATE KEY-----\n"
                with open(key_file, "w") as f:
                    f.write(fake_key)
                os.chmod(key_file, 0o600)
                logger.info(f"Deployed Canary SSH private key to isolated path: {key_file}")
                self.emit_event("canary.deployed.ssh", {"path": str(key_file)})
                
                await self.report_asset_to_api("SSH_KEY", str(key_file), self.canary_token)
        except Exception as e:
            logger.error(f"Failed to deploy SSH canary key: {e}")

    async def start(self):
        self.is_running = True
        logger.info(f"Starting Canary Credentials Plugin in workspace: {self.deception_workspace}...")
        
        if not self.deception_workspace.exists():
            self.deception_workspace.mkdir(parents=True, mode=0o755, exist_ok=True)
            
        if self.aws_enabled:
            await self.deploy_aws_credentials()
            
        if self.ssh_enabled:
            await self.deploy_ssh_key()
            
        logger.info("Canary Credentials deployed successfully.")

    async def stop(self):
        self.is_running = False
        logger.info("Canary Credentials Plugin stopped.")
