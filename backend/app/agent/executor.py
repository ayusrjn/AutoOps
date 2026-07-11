from app.database import SessionLocal
from app.models.incident import Incident
from app.agent.graph import app_graph

def run_agent(incident_id: str):
    """
    Executes the LangGraph incident investigation workflow for a given incident_id,
    and updates the database with the results.
    """
    db = SessionLocal()
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            print(f"Incident with ID {incident_id} not found in database.")
            return

        # Prepare initial state for the StateGraph
        initial_state = {
            "incident_id": incident.id,
            "alert_name": incident.alert_name,
            "alert_payload": incident.alert_payload or {},
            "timestamp": incident.created_at.isoformat() if incident.created_at else "",
            "target_services": [],
            "metrics_data": [],
            "logs_data": [],
            "traces_data": [],
            "k8s_events": [],
            "deployment_events": [],
            "reasoning_history": [f"Initiated automated incident investigation for: {incident.alert_name}"],
            "current_node": "",
            "root_cause_summary": "",
            "remediation_steps": [],
            "confidence_score": 0.0
        }

        # Execute StateGraph
        final_state = app_graph.invoke(initial_state)

        # Write results back to the database
        incident.root_cause_summary = final_state.get("root_cause_summary")
        incident.remediation_steps = final_state.get("remediation_steps")
        incident.confidence_score = final_state.get("confidence_score", 0.0)
        incident.reasoning_history = final_state.get("reasoning_history")
        incident.metrics_data = final_state.get("metrics_data")
        incident.logs_data = final_state.get("logs_data")
        incident.traces_data = final_state.get("traces_data")
        incident.status = "root_cause_found"

        db.commit()
        db.refresh(incident)
    except Exception as e:
        print(f"Error executing agent for incident {incident_id}: {e}")
        try:
            # Attempt to log error in reasoning history
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if incident:
                history = incident.reasoning_history or []
                incident.reasoning_history = history + [f"Agent execution failed: {str(e)}"]
                db.commit()
        except Exception as db_err:
            print(f"Failed to record execution error in DB: {db_err}")
    finally:
        db.close()
