import uuid
import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    users = relationship("User", back_populates="tenant")
    sensors = relationship("Sensor", back_populates="tenant")

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="analyst") # admin, analyst
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    tenant = relationship("Tenant", back_populates="users")

class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    ip_address = Column(String)
    version = Column(String)
    status = Column(String, default="offline")
    last_heartbeat = Column(DateTime)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    tenant = relationship("Tenant", back_populates="sensors")
    events = relationship("Event", back_populates="sensor")

class Event(Base):
    __tablename__ = "events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sensor_id = Column(UUID(as_uuid=True), ForeignKey("sensors.id"))
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    payload = Column(JSON, nullable=False)
    
    sensor = relationship("Sensor", back_populates="events")

class DeceptionAsset(Base):
    __tablename__ = "deception_assets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    asset_type = Column(String, nullable=False) # e.g., 'credential', 'host', 'aws_key', 'share'
    name = Column(String, nullable=False)
    asset_data = Column(JSON, nullable=False) # Store the fake credentials, paths, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    tenant = relationship("Tenant")
