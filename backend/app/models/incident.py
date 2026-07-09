import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, JSON, DateTime
from app.database import Base

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, default="investigating")  # investigating | root_cause_found | resolved
    alert_name = Column(String, nullable=False)
    alert_payload = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)
    root_cause_summary = Column(String, nullable=True)
    remediation_steps = Column(JSON, default=list)
    confidence_score = Column(Float, default=0.0)
