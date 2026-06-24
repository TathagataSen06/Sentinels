from pydantic import BaseModel, ConfigDict, Field
from typing import List, Dict, Any, Optional, Generic, TypeVar
from datetime import datetime
from uuid import UUID

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int

class CursorPaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    next_cursor: Optional[str] = None

class DeceptionAssetBase(BaseModel):
    asset_type: str = Field(..., description="Type of asset, e.g., 'credential', 'host'")
    name: str
    asset_data: Dict[str, Any]
    is_active: bool = True

class DeceptionAssetCreate(DeceptionAssetBase):
    pass

class DeceptionAssetResponse(DeceptionAssetBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SensorResponse(BaseModel):
    id: UUID
    name: str
    ip_address: Optional[str] = None
    version: Optional[str] = None
    status: str
    last_heartbeat: Optional[datetime] = None
    tenant_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Auth --------------------------------------------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Sensor provisioning -----------------------------------------------------
class SensorCreate(BaseModel):
    name: str
    ip_address: Optional[str] = None
    version: Optional[str] = None


class SensorEnrollmentResponse(BaseModel):
    sensor: SensorResponse
    token: str = Field(..., description="Sensor-scoped JWT used to authenticate telemetry")


# --- Event ingestion ---------------------------------------------------------
class EventIngest(BaseModel):
    """Validated envelope for a single sensor event.

    Replaces the previous untyped `dict` body so we never write unvalidated
    attacker-controlled JSON straight into the database.
    """
    model_config = ConfigDict(extra="forbid")

    event_type: str = Field(..., min_length=1, max_length=128,
                            description="e.g. 'ssh.login.attempt'")
    source_ip: Optional[str] = Field(None, max_length=64)
    plugin_name: Optional[str] = Field(None, max_length=64)
    payload: Dict[str, Any] = Field(default_factory=dict)


# --- Incidents ---------------------------------------------------------------
class IncidentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    source_ip: str
    title: str
    severity: str
    severity_score: int
    status: str
    assignee: Optional[str] = None
    sensor_name: Optional[str] = None
    mitre: List[str] = Field(default_factory=list)
    event_count: int
    first_seen: datetime
    last_seen: datetime

    model_config = ConfigDict(from_attributes=True)


class IncidentDetailResponse(IncidentResponse):
    events: List[Dict[str, Any]] = Field(default_factory=list)


class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(
        None, pattern="^(NEW|INVESTIGATING|CONTAINED|RESOLVED|CLOSED)$")
    assignee: Optional[str] = Field(None, max_length=128)
