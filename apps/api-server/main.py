import os
import time
import json
import base64
import uuid
import logging
import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Request, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, tuple_
from prometheus_fastapi_instrumentator import Instrumentator
import redis.asyncio as redis_async

from database import engine, Base, get_db, AsyncSessionLocal
import models
import schemas
from auth import (
    get_current_user,
    get_current_active_admin,
    get_current_sensor,
    create_user_token,
    create_sensor_token,
    hash_password,
    verify_password,
)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("sentinels_audit")

# --- Tunables ----------------------------------------------------------------
MAX_BODY_BYTES = int(os.getenv("MAX_EVENT_BYTES", str(256 * 1024)))   # 256 KB
EVENT_STREAM_MAXLEN = int(os.getenv("EVENT_STREAM_MAXLEN", "100000"))  # cap Redis stream
INGEST_RATE_LIMIT = int(os.getenv("INGEST_RATE_LIMIT_PER_MIN", "6000"))  # per sensor / min

redis_client: redis_async.Redis | None = None


async def _seed_default_admin():
    """Create a default tenant + admin user on first boot so the platform is
    usable out of the box. Credentials come from the environment."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@sentinels.local")
    admin_password = os.getenv("ADMIN_PASSWORD", "changeme")
    async with AsyncSessionLocal() as db:
        existing = await db.execute(select(models.User).limit(1))
        if existing.scalar_one_or_none() is not None:
            return
        tenant = models.Tenant(name=os.getenv("DEFAULT_TENANT_NAME", "Default"))
        db.add(tenant)
        await db.flush()
        db.add(models.User(
            email=admin_email,
            hashed_password=hash_password(admin_password),
            role="admin",
            tenant_id=tenant.id,
        ))
        await db.commit()
        if admin_password == "changeme":
            logger.warning(
                "Seeded admin '%s' with the default password 'changeme'. "
                "Set ADMIN_PASSWORD before any real deployment.", admin_email)
        else:
            logger.info("Seeded admin user '%s'.", admin_email)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = redis_async.Redis(
        host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", "6379")), db=0
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _seed_default_admin()
    yield
    if redis_client is not None:
        await redis_client.aclose()


app = FastAPI(title="Sentinels API", version="2.0.0", lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def safety_and_audit_middleware(request: Request, call_next):
    # Reject oversized bodies before they are parsed.
    content_length = request.headers.get("content-length")
    if content_length and content_length.isdigit() and int(content_length) > MAX_BODY_BYTES:
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=413, content={"detail": "Request body too large"})

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    client = request.client.host if request.client else "unknown"
    logger.info("AUDIT %s %s %s -> %s %.4fs",
                client, request.method, request.url.path, response.status_code, process_time)
    return response


# --- Cursor pagination helpers ----------------------------------------------
# Keyset pagination over (timestamp, id) — correct even though IDs are random
# UUIDv4 (the previous `id > cursor` comparison was meaningless on unordered UUIDs).
def _encode_cursor(ts: datetime.datetime, item_id: uuid.UUID) -> str:
    raw = f"{ts.isoformat()}|{item_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor: str):
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    ts_str, id_str = raw.split("|", 1)
    return datetime.datetime.fromisoformat(ts_str), uuid.UUID(id_str)


async def _rate_limit(key: str, limit: int, window: int = 60):
    if redis_client is None:
        return
    bucket = f"ratelimit:{key}:{int(time.time() // window)}"
    count = await redis_client.incr(bucket)
    if count == 1:
        await redis_client.expire(bucket, window)
    if count > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# --- Auth --------------------------------------------------------------------
@app.post("/token", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(models.User).where(models.User.email == form_data.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.Token(access_token=create_user_token(user))


# --- Sensors -----------------------------------------------------------------
@app.post("/api/v1/sensors", response_model=schemas.SensorEnrollmentResponse, status_code=201)
async def create_sensor(
    sensor_data: schemas.SensorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_admin),
):
    """Provision a sensor and mint a sensor-scoped token for it to deliver
    telemetry. (Lightweight stand-in for the mTLS enrollment flow.)"""
    sensor = models.Sensor(
        name=sensor_data.name,
        ip_address=sensor_data.ip_address,
        version=sensor_data.version,
        tenant_id=current_user.tenant_id,
    )
    db.add(sensor)
    await db.commit()
    await db.refresh(sensor)
    return schemas.SensorEnrollmentResponse(sensor=sensor, token=create_sensor_token(sensor))


@app.get("/api/v1/sensors", response_model=schemas.CursorPaginatedResponse[schemas.SensorResponse])
async def list_sensors(
    cursor: str = Query(None, description="Opaque pagination cursor"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = select(models.Sensor).where(models.Sensor.tenant_id == current_user.tenant_id)
    if cursor:
        try:
            c_ts, c_id = _decode_cursor(cursor)
            query = query.where(tuple_(models.Sensor.created_at, models.Sensor.id) > (c_ts, c_id))
        except (ValueError, TypeError):
            pass
    query = query.order_by(models.Sensor.created_at, models.Sensor.id).limit(limit)
    sensors = (await db.execute(query)).scalars().all()
    next_cursor = _encode_cursor(sensors[-1].created_at, sensors[-1].id) if len(sensors) == limit else None
    return schemas.CursorPaginatedResponse(items=sensors, next_cursor=next_cursor)


# --- Agent endpoints ---------------------------------------------------------
@app.post("/api/v1/agent/heartbeat")
async def agent_heartbeat(
    db: AsyncSession = Depends(get_db),
    current_sensor: models.Sensor = Depends(get_current_sensor),
):
    current_sensor.last_heartbeat = datetime.datetime.now(datetime.timezone.utc)
    current_sensor.status = "online"
    await db.commit()
    return {"message": "Heartbeat received"}


@app.get("/api/v1/agent/config")
async def agent_config(
    db: AsyncSession = Depends(get_db),
    current_sensor: models.Sensor = Depends(get_current_sensor),
):
    result = await db.execute(
        select(models.DeceptionAsset).where(
            models.DeceptionAsset.is_active == True,
            models.DeceptionAsset.tenant_id == current_sensor.tenant_id,
        )
    )
    assets = result.scalars().all()
    return {"config": {}, "deception_assets": assets}


@app.post("/api/v1/agent/events", status_code=202)
async def ingest_event(
    event: schemas.EventIngest,
    db: AsyncSession = Depends(get_db),
    current_sensor: models.Sensor = Depends(get_current_sensor),
):
    await _rate_limit(f"ingest:{current_sensor.id}", INGEST_RATE_LIMIT)

    # Build the enriched, internal-trusted envelope.
    enriched = event.model_dump()
    enriched["sensor_id"] = str(current_sensor.id)
    enriched["sensor_name"] = current_sensor.name
    enriched["tenant_id"] = str(current_sensor.tenant_id)
    if not enriched.get("plugin_name"):
        enriched["plugin_name"] = event.event_type.split(".")[0]
    if not enriched.get("source_ip"):
        enriched["source_ip"] = event.payload.get("src_ip") or event.payload.get("source_ip")

    db.add(models.Event(
        sensor_id=current_sensor.id,
        tenant_id=current_sensor.tenant_id,
        payload=enriched,
    ))
    await db.commit()

    if redis_client is not None:
        await redis_client.xadd(
            "sentinels_events",
            {"event": json.dumps(enriched)},
            maxlen=EVENT_STREAM_MAXLEN,
            approximate=True,
        )
    return {"message": "Event accepted"}


# --- Deception assets --------------------------------------------------------
@app.post("/api/v1/assets", response_model=schemas.DeceptionAssetResponse)
async def create_asset(
    asset_data: schemas.DeceptionAssetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_active_admin),
):
    new_asset = models.DeceptionAsset(
        tenant_id=current_user.tenant_id,
        asset_type=asset_data.asset_type,
        name=asset_data.name,
        asset_data=asset_data.asset_data,
        is_active=asset_data.is_active,
    )
    db.add(new_asset)
    await db.commit()
    await db.refresh(new_asset)
    return new_asset


@app.get("/api/v1/assets", response_model=schemas.CursorPaginatedResponse[schemas.DeceptionAssetResponse])
async def list_assets(
    cursor: str = Query(None, description="Opaque pagination cursor"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = select(models.DeceptionAsset).where(models.DeceptionAsset.tenant_id == current_user.tenant_id)
    if cursor:
        try:
            c_ts, c_id = _decode_cursor(cursor)
            query = query.where(tuple_(models.DeceptionAsset.created_at, models.DeceptionAsset.id) > (c_ts, c_id))
        except (ValueError, TypeError):
            pass
    query = query.order_by(models.DeceptionAsset.created_at, models.DeceptionAsset.id).limit(limit)
    assets = (await db.execute(query)).scalars().all()
    next_cursor = _encode_cursor(assets[-1].created_at, assets[-1].id) if len(assets) == limit else None
    return schemas.CursorPaginatedResponse(items=assets, next_cursor=next_cursor)


# --- Incidents ---------------------------------------------------------------
@app.get("/api/v1/incidents", response_model=schemas.CursorPaginatedResponse[schemas.IncidentResponse])
async def list_incidents(
    cursor: str = Query(None, description="Opaque pagination cursor"),
    limit: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = select(models.Incident).where(models.Incident.tenant_id == current_user.tenant_id)
    if cursor:
        try:
            c_ts, c_id = _decode_cursor(cursor)
            # Newest first: page through (last_seen, id) descending.
            query = query.where(tuple_(models.Incident.last_seen, models.Incident.id) < (c_ts, c_id))
        except (ValueError, TypeError):
            pass
    query = query.order_by(models.Incident.last_seen.desc(), models.Incident.id.desc()).limit(limit)
    incidents = (await db.execute(query)).scalars().all()
    next_cursor = _encode_cursor(incidents[-1].last_seen, incidents[-1].id) if len(incidents) == limit else None
    return schemas.CursorPaginatedResponse(items=incidents, next_cursor=next_cursor)


async def _get_owned_incident(incident_id: uuid.UUID, db: AsyncSession, current_user: models.User) -> models.Incident:
    result = await db.execute(
        select(models.Incident).where(
            models.Incident.id == incident_id,
            models.Incident.tenant_id == current_user.tenant_id,
        )
    )
    incident = result.scalar_one_or_none()
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.get("/api/v1/incidents/{incident_id}", response_model=schemas.IncidentDetailResponse)
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return await _get_owned_incident(incident_id, db, current_user)


@app.patch("/api/v1/incidents/{incident_id}", response_model=schemas.IncidentDetailResponse)
async def update_incident(
    incident_id: uuid.UUID,
    update: schemas.IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    incident = await _get_owned_incident(incident_id, db, current_user)
    if update.status is not None:
        incident.status = update.status
    if update.assignee is not None:
        incident.assignee = update.assignee
    await db.commit()
    await db.refresh(incident)
    return incident
