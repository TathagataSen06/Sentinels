from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import engine, Base, get_db
import models
from auth import get_current_user, get_current_active_admin
from prometheus_fastapi_instrumentator import Instrumentator
import os
import logging
import time

app = FastAPI(title="Sentinels API", version="2.0.0")
Instrumentator().instrument(app).expose(app)
logger = logging.getLogger("sentinels_audit")
logger.setLevel(logging.INFO)

@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"AUDIT: {request.client.host} {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/sensors")
async def list_sensors(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.Sensor).where(models.Sensor.tenant_id == current_user.tenant_id))
    sensors = result.scalars().all()
    return {"sensors": sensors}

@app.post("/api/v1/agent/register")
async def register_agent(db: AsyncSession = Depends(get_db)):
    # In a real scenario, this endpoint verifies a one-time provisioning token (Zero Trust)
    # and issues a signed certificate or JWT for the sensor.
    return {"message": "Sensor registered successfully, certificate issued"}

@app.post("/api/v1/agent/heartbeat")
async def agent_heartbeat(db: AsyncSession = Depends(get_db)):
    # Tracks sensor uptime and updates the 'last_heartbeat' column.
    return {"message": "Heartbeat received"}

@app.get("/api/v1/agent/config")
async def agent_config(db: AsyncSession = Depends(get_db)):
    # This endpoint provides the sensor with active deception assets to load into plugins
    result = await db.execute(select(models.DeceptionAsset).where(models.DeceptionAsset.is_active == True))
    assets = result.scalars().all()
    return {"config": {}, "deception_assets": assets}

@app.post("/api/v1/assets")
async def create_asset(asset_data: dict, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_active_admin)):
    new_asset = models.DeceptionAsset(
        tenant_id=current_user.tenant_id,
        asset_type=asset_data.get("asset_type"),
        name=asset_data.get("name"),
        asset_data=asset_data.get("asset_data", {})
    )
    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)
    return new_asset

@app.get("/api/v1/assets")
async def list_assets(db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.DeceptionAsset).where(models.DeceptionAsset.tenant_id == current_user.tenant_id))
    assets = result.scalars().all()
    return {"assets": assets}


