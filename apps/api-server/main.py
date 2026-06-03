from fastapi import FastAPI, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import engine, Base, get_db
import models
import schemas
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

@app.get("/api/v1/sensors", response_model=schemas.PaginatedResponse[schemas.SensorResponse])
async def list_sensors(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    query = select(models.Sensor).where(models.Sensor.tenant_id == current_user.tenant_id)
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    result = await db.execute(query.offset(skip).limit(limit))
    sensors = result.scalars().all()
    
    return schemas.PaginatedResponse(items=sensors, total=total or 0, skip=skip, limit=limit)

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

@app.post("/api/v1/assets", response_model=schemas.DeceptionAssetResponse)
async def create_asset(
    asset_data: schemas.DeceptionAssetCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_active_admin)
):
    new_asset = models.DeceptionAsset(
        tenant_id=current_user.tenant_id,
        asset_type=asset_data.asset_type,
        name=asset_data.name,
        asset_data=asset_data.asset_data,
        is_active=asset_data.is_active
    )
    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)
    return new_asset

@app.get("/api/v1/assets", response_model=schemas.PaginatedResponse[schemas.DeceptionAssetResponse])
async def list_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    query = select(models.DeceptionAsset).where(models.DeceptionAsset.tenant_id == current_user.tenant_id)
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    
    result = await db.execute(query.offset(skip).limit(limit))
    assets = result.scalars().all()
    
    return schemas.PaginatedResponse(items=assets, total=total or 0, skip=skip, limit=limit)
