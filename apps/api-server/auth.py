import os
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import User, Sensor
from database import get_db

logger = logging.getLogger("sentinels_auth")

# --- Secret management -------------------------------------------------------
# Never ship a hardcoded secret. Read from the environment; if it is missing we
# generate a strong ephemeral one so the process still boots in dev, but tokens
# will not survive a restart (which forces real configuration in production).
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
SENSOR_TOKEN_EXPIRE_DAYS = int(os.getenv("SENSOR_TOKEN_EXPIRE_DAYS", "365"))

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("ENVIRONMENT", "development").lower() == "production":
        raise RuntimeError(
            "JWT_SECRET_KEY must be set in production. Refusing to start with an "
            "insecure default."
        )
    SECRET_KEY = secrets.token_urlsafe(64)
    logger.warning(
        "JWT_SECRET_KEY not set — generated an ephemeral dev secret. "
        "Tokens will be invalidated on restart. Set JWT_SECRET_KEY for stable auth."
    )

# Token audiences keep user sessions and sensor credentials from being
# interchangeable even though they are signed with the same key.
TOKEN_TYPE_USER = "user"
TOKEN_TYPE_SENSOR = "sensor"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- Password helpers --------------------------------------------------------
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- Token helpers -----------------------------------------------------------
def _create_token(subject: str, token_type: str, tenant_id: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "tid": tenant_id,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_user_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(user.email, TOKEN_TYPE_USER, str(user.tenant_id), delta)


def create_sensor_token(sensor: Sensor, expires_delta: Optional[timedelta] = None) -> str:
    delta = expires_delta or timedelta(days=SENSOR_TOKEN_EXPIRE_DAYS)
    return _create_token(str(sensor.id), TOKEN_TYPE_SENSOR, str(sensor.tenant_id), delta)


def _decode(token: str, expected_type: str) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise credentials_exception
    if payload.get("type") != expected_type or payload.get("sub") is None:
        raise credentials_exception
    return payload


# --- Dependencies ------------------------------------------------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    payload = _decode(token, TOKEN_TYPE_USER)
    result = await db.execute(select(User).where(User.email == payload["sub"]))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


async def get_current_sensor(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> Sensor:
    payload = _decode(token, TOKEN_TYPE_SENSOR)
    try:
        sensor_id = uuid.UUID(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate sensor credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await db.execute(select(Sensor).where(Sensor.id == sensor_id))
    sensor = result.scalar_one_or_none()
    if sensor is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate sensor credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return sensor
