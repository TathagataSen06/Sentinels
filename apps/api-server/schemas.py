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
