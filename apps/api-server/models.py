import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, JSON, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from database import Base


class Tenant(Base):
    __tablename__ = "tenants"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    users: Mapped[List["User"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    sensors: Mapped[List["Sensor"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    events: Mapped[List["Event"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    deception_assets: Mapped[List["DeceptionAsset"]] = relationship(back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, default="analyst") # admin, analyst
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="users")


class Sensor(Base):
    __tablename__ = "sensors"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String)
    version: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="offline")
    last_heartbeat: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="sensors")
    events: Mapped[List["Event"]] = relationship(back_populates="sensor", cascade="all, delete-orphan")


class Event(Base):
    __tablename__ = "events"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sensors.id", ondelete="CASCADE"), index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSONB, nullable=False)
    
    __table_args__ = (
        Index("ix_events_payload_gin", payload, postgresql_using="gin"),
    )
    
    # Relationships
    sensor: Mapped["Sensor"] = relationship(back_populates="events")
    tenant: Mapped["Tenant"] = relationship(back_populates="events")


class DeceptionAsset(Base):
    __tablename__ = "deception_assets"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    asset_type: Mapped[str] = mapped_column(String, nullable=False) # e.g., 'credential', 'host', 'aws_key', 'share'
    name: Mapped[str] = mapped_column(String, nullable=False)
    asset_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="deception_assets")


class Incident(Base):
    """A correlated attack campaign, produced by the processing engine.

    One incident represents the aggregated activity of a single source IP within
    a correlation window for a tenant. The processing engine upserts these rows
    as it correlates events; the API and SOC dashboard read them.
    """
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    source_ip: Mapped[str] = mapped_column(String, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    severity: Mapped[str] = mapped_column(String, default="LOW")  # LOW, MEDIUM, HIGH, CRITICAL
    severity_score: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String, default="NEW")  # NEW, INVESTIGATING, CONTAINED, RESOLVED, CLOSED
    assignee: Mapped[Optional[str]] = mapped_column(String)
    sensor_name: Mapped[Optional[str]] = mapped_column(String)
    mitre: Mapped[List[str]] = mapped_column(JSONB, default=list)
    event_count: Mapped[int] = mapped_column(Integer, default=0)
    events: Mapped[List[Dict[str, Any]]] = mapped_column(JSONB, default=list)
    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # One open incident per (tenant, source IP); the processing engine upserts on this.
        UniqueConstraint("tenant_id", "source_ip", name="uq_incident_tenant_source"),
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship()
