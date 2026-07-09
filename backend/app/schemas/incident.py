from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class AlertmanagerAlert(BaseModel):
    status: str
    labels: Dict[str, str] = Field(default_factory=dict)
    annotations: Dict[str, str] = Field(default_factory=dict)
    startsAt: datetime
    endsAt: Optional[datetime] = None
    generatorURL: str = ""

class WebhookPayload(BaseModel):
    receiver: str
    status: str
    alerts: List[AlertmanagerAlert] = Field(default_factory=list)
    groupLabels: Dict[str, str] = Field(default_factory=dict)
    commonLabels: Dict[str, str] = Field(default_factory=dict)
    commonAnnotations: Dict[str, str] = Field(default_factory=dict)
    externalURL: str = ""

class IncidentResponse(BaseModel):
    id: str
    status: str
    alert_name: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    root_cause_summary: Optional[str] = None
    remediation_steps: List[str] = Field(default_factory=list)
    confidence_score: float = 0.0

    model_config = ConfigDict(from_attributes=True)
