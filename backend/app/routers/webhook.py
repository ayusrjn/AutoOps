from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.incident import WebhookPayload
from app.models.incident import Incident
from app.agent.executor import run_agent

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)

@router.post("")
def receive_alert(payload: WebhookPayload, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if not payload.alerts:
        return {"status": "ignored", "message": "No alerts in payload"}
    
    # Try to extract a meaningful alert name
    alert_name = payload.groupLabels.get("alertname")
    if not alert_name and payload.alerts:
        alert_name = payload.alerts[0].labels.get("alertname", "Unknown Alert")

    # Store payload using Pydantic V2 model_dump for JSON serialization
    new_incident = Incident(
        alert_name=alert_name,
        alert_payload=payload.model_dump(mode="json"),
        status="investigating"
    )
    
    db.add(new_incident)
    db.commit()
    db.refresh(new_incident)
    
    # Spawn LangGraph background task
    background_tasks.add_task(run_agent, new_incident.id)
    
    return {"status": "success", "incident_id": new_incident.id}
