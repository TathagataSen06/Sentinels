from fastapi import FastAPI, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import engine, Base, get_db
import models
import schemas
from auth import get_current_user, get_current_active_admin, get_current_sensor
from prometheus_fastapi_instrumentator import Instrumentator
import os
import logging
import time
import datetime
import json
import redis.asyncio as redis_async

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

redis_client = None

@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = redis_async.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/sensors", response_model=schemas.CursorPaginatedResponse[schemas.SensorResponse])
async def list_sensors(
    cursor: str = Query(None, description="Cursor for pagination (ID of last item)"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    query = select(models.Sensor).where(models.Sensor.tenant_id == current_user.tenant_id)
    if cursor:
        try:
            import uuid
            cursor_uuid = uuid.UUID(cursor)
            query = query.where(models.Sensor.id > cursor_uuid)
        except ValueError:
            pass
    
    query = query.order_by(models.Sensor.id).limit(limit)
    
    result = await db.execute(query)
    sensors = result.scalars().all()
    
    next_cursor = str(sensors[-1].id) if len(sensors) == limit else None
    return schemas.CursorPaginatedResponse(items=sensors, next_cursor=next_cursor)

@app.post("/api/v1/agent/register")
async def register_agent(db: AsyncSession = Depends(get_db)):
    # In a real scenario, this endpoint verifies a one-time provisioning token (Zero Trust)
    # and issues a signed certificate or JWT for the sensor.
    return {"message": "Sensor registered successfully, certificate issued"}

@app.post("/api/v1/agent/heartbeat")
async def agent_heartbeat(
    db: AsyncSession = Depends(get_db),
    current_sensor: models.Sensor = Depends(get_current_sensor)
):
    current_sensor.last_heartbeat = datetime.datetime.utcnow()
    current_sensor.status = "online"
    await db.commit()
    return {"message": "Heartbeat received"}

@app.get("/api/v1/agent/config")
async def agent_config(
    db: AsyncSession = Depends(get_db),
    current_sensor: models.Sensor = Depends(get_current_sensor)
):
    # This endpoint provides the sensor with active deception assets to load into plugins
    result = await db.execute(
        select(models.DeceptionAsset)
        .where(
            models.DeceptionAsset.is_active == True,
            models.DeceptionAsset.tenant_id == current_sensor.tenant_id
        )
    )
    assets = result.scalars().all()
    return {"config": {}, "deception_assets": assets}

@app.post("/api/v1/agent/events")
async def ingest_event(
    event_data: dict,
    db: AsyncSession = Depends(get_db),
    current_sensor: models.Sensor = Depends(get_current_sensor)
):
    new_event = models.Event(
        sensor_id=current_sensor.id,
        tenant_id=current_sensor.tenant_id,
        payload=event_data
    )
    db.add(new_event)
    await db.commit()

    event_data["sensor_id"] = str(current_sensor.id)
    event_data["tenant_id"] = str(current_sensor.tenant_id)
    if redis_client:
        await redis_client.xadd("sentinels_events", {"event": json.dumps(event_data)})
    
    return {"message": "Event ingested successfully"}

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

@app.get("/api/v1/assets", response_model=schemas.CursorPaginatedResponse[schemas.DeceptionAssetResponse])
async def list_assets(
    cursor: str = Query(None, description="Cursor for pagination (ID of last item)"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    query = select(models.DeceptionAsset).where(models.DeceptionAsset.tenant_id == current_user.tenant_id)
    if cursor:
        try:
            import uuid
            cursor_uuid = uuid.UUID(cursor)
            query = query.where(models.DeceptionAsset.id > cursor_uuid)
        except ValueError:
            pass
    
    query = query.order_by(models.DeceptionAsset.id).limit(limit)
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    next_cursor = str(assets[-1].id) if len(assets) == limit else None
    return schemas.CursorPaginatedResponse(items=assets, next_cursor=next_cursor)
