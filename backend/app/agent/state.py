from typing import TypedDict, List, Dict, Any

class IncidentState(TypedDict):
    incident_id: str
    alert_name: str
    alert_payload: Dict[str, Any]
    timestamp: str
    target_services: List[str]
    metrics_data: List[Dict[str, Any]]
    logs_data: List[Dict[str, Any]]
    traces_data: List[Dict[str, Any]]
    k8s_events: List[Dict[str, Any]]
    deployment_events: List[Dict[str, Any]]
    reasoning_history: List[str]
    current_node: str
    root_cause_summary: str
    remediation_steps: List[str]
    confidence_score: float
