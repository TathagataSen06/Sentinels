from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

class LogSource(BaseModel):
    product: str

class Detection(BaseModel):
    selection: Dict[str, Any]
    condition: str

class Threshold(BaseModel):
    count: int
    within: str

class CorrelationEvent(BaseModel):
    id: str

class Correlation(BaseModel):
    events: List[CorrelationEvent]
    within: str

class Mitre(BaseModel):
    tactic: List[str]
    technique: List[str]
    sub_technique: Optional[List[str]] = []

class SigmaRule(BaseModel):
    id: uuid.UUID
    title: str = Field(..., min_length=3)
    description: str
    author: Optional[str] = "Unknown"
    status: str = Field(default="experimental")
    version: str = Field(default="1.0.0")
    logsource: LogSource
    detection: Detection
    threshold: Optional[Threshold] = None
    correlation: Optional[Correlation] = None
    mitre: Mitre
    confidence: int = Field(default=50, ge=0, le=100)
    risk_score: int = Field(default=50, ge=0, le=100)
