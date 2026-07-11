import re
from app.agent.state import IncidentState
from app.connectors.prometheus import PrometheusConnector
from app.connectors.loki import LokiConnector
from app.connectors.jaeger import JaegerConnector

def fetch_alert_details(state: IncidentState) -> dict:
    """
    Parses the Alertmanager webhook payload to extract target service names,
    timestamps, and sets up the initial reasoning state.
    """
    payload = state.get("alert_payload", {})
    
    target_services = []
    
    # Check common labels first for service mapping
    common_labels = payload.get("commonLabels", {})
    for key in ["service", "app", "job", "container"]:
        val = common_labels.get(key)
        if val and val not in target_services:
            target_services.append(val)
            
    # Check individual alerts within the payload
    alerts = payload.get("alerts", [])
    for alert in alerts:
        labels = alert.get("labels", {})
        for key in ["service", "app", "job", "container"]:
            val = labels.get(key)
            if val and val not in target_services:
                target_services.append(val)
                
    # Fallback if no specific service was identified
    if not target_services:
        target_services = ["unknown-service"]
        
    reasoning_step = f"Initial state setup. Identified target services: {', '.join(target_services)}."
    
    return {
        "target_services": target_services,
        "reasoning_history": state.get("reasoning_history", []) + [reasoning_step],
        "current_node": "fetch_alert_details"
    }

def analyze_metrics(state: IncidentState) -> dict:
    """
    Queries Prometheus for CPU, memory, and HTTP error rates for the target services.
    """
    target_services = state.get("target_services", [])
    metrics_data = []
    reasoning_history = state.get("reasoning_history", [])
    
    try:
        connector = PrometheusConnector()
    except Exception as e:
        err_msg = f"Failed to initialize Prometheus client: {e}"
        reasoning_history.append(err_msg)
        return {
            "metrics_data": [{"error": err_msg}],
            "reasoning_history": reasoning_history,
            "current_node": "analyze_metrics"
        }
        
    for service in target_services:
        queries = {
            "cpu_usage": f'sum(rate(container_cpu_usage_seconds_total{{container=~".*{service}.*"}}[5m]))',
            "memory_usage": f'sum(container_memory_working_set_bytes{{container=~".*{service}.*"}})',
            "http_5xx_rate": f'sum(rate(http_requests_total{{container=~".*{service}.*",status=~"5.."}}[5m]))'
        }
        
        for metric_name, query in queries.items():
            try:
                result = connector.query(query)
                metrics_data.append({
                    "service": service,
                    "metric": metric_name,
                    "query": query,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                metrics_data.append({
                    "service": service,
                    "metric": metric_name,
                    "query": query,
                    "status": "error",
                    "error": str(e)
                })
                
    success_queries = [m for m in metrics_data if m["status"] == "success"]
    err_queries = [m for m in metrics_data if m["status"] == "error"]
    
    step_summary = (
        f"Analyzed metrics for services: {', '.join(target_services)}. "
        f"Executed {len(metrics_data)} queries ({len(success_queries)} succeeded, {len(err_queries)} failed)."
    )
    reasoning_history.append(step_summary)
    
    return {
        "metrics_data": metrics_data,
        "reasoning_history": reasoning_history,
        "current_node": "analyze_metrics"
    }

def check_logs(state: IncidentState) -> dict:
    """
    Queries Grafana Loki for logs related to the target services.
    Parses retrieved logs to extract trace IDs.
    """
    target_services = state.get("target_services", [])
    logs_data = []
    reasoning_history = state.get("reasoning_history", [])
    extracted_trace_ids = []
    
    try:
        connector = LokiConnector()
    except Exception as e:
        err_msg = f"Failed to initialize Loki client: {e}"
        reasoning_history.append(err_msg)
        return {
            "logs_data": [{"error": err_msg}],
            "reasoning_history": reasoning_history,
            "current_node": "check_logs"
        }
        
    trace_id_regex = re.compile(r'\b([a-f0-9]{32})\b', re.IGNORECASE)
    
    for service in target_services:
        # Try a container LogQL first, then fallback to app
        queries = [
            f'{{container=~".*{service}.*"}}',
            f'{{app=~".*{service}.*"}}'
        ]
        
        service_logs = []
        queried_successfully = False
        
        for query in queries:
            try:
                response = connector.query_range(query, limit=50)
                if response.get("status") == "success":
                    results = response.get("data", {}).get("result", [])
                    for stream_info in results:
                        stream_labels = stream_info.get("stream", {})
                        for val_pair in stream_info.get("values", []):
                            timestamp_ns, log_msg = val_pair[0], val_pair[1]
                            service_logs.append({
                                "timestamp": timestamp_ns,
                                "message": log_msg,
                                "labels": stream_labels
                            })
                            
                            # Search for trace_id
                            matches = trace_id_regex.findall(log_msg)
                            for match in matches:
                                if match not in extracted_trace_ids:
                                    extracted_trace_ids.append(match)
                    
                    queried_successfully = True
                    if service_logs:
                        break
            except Exception as e:
                pass
                
        if queried_successfully:
            logs_data.append({
                "service": service,
                "status": "success",
                "logs": service_logs
            })
        else:
            logs_data.append({
                "service": service,
                "status": "error",
                "error": "Failed to fetch logs from any LogQL query"
            })
            
    connector.close()
    
    if extracted_trace_ids:
        step_summary = (
            f"Retrieved logs for services: {', '.join(target_services)}. "
            f"Found trace IDs: {', '.join(extracted_trace_ids)}."
        )
        # Populate traces_data with stub dictionaries for each trace ID found
        traces_data = [{"trace_id": tid, "spans": []} for tid in extracted_trace_ids]
    else:
        step_summary = f"Retrieved logs for services: {', '.join(target_services)}. No trace IDs detected."
        traces_data = []
        
    reasoning_history.append(step_summary)
    
    return {
        "logs_data": logs_data,
        "traces_data": traces_data,
        "reasoning_history": reasoning_history,
        "current_node": "check_logs"
    }

def analyze_traces(state: IncidentState) -> dict:
    """
    Queries Jaeger for traces using the retrieved trace_ids in the state.
    """
    traces_data = state.get("traces_data", [])
    updated_traces = []
    reasoning_history = state.get("reasoning_history", [])
    
    if not traces_data:
        reasoning_history.append("No trace IDs available to analyze.")
        return {
            "traces_data": [],
            "reasoning_history": reasoning_history,
            "current_node": "analyze_traces"
        }
        
    try:
        connector = JaegerConnector()
    except Exception as e:
        err_msg = f"Failed to initialize Jaeger client: {e}"
        reasoning_history.append(err_msg)
        return {
            "traces_data": traces_data,
            "reasoning_history": reasoning_history,
            "current_node": "analyze_traces"
        }
        
    for trace_item in traces_data:
        trace_id = trace_item.get("trace_id")
        if not trace_id:
            continue
        try:
            trace_detail = connector.get_trace(trace_id)
            spans = []
            if trace_detail and "data" in trace_detail:
                for trace_obj in trace_detail["data"]:
                    spans.extend(trace_obj.get("spans", []))
            
            updated_traces.append({
                "trace_id": trace_id,
                "status": "success",
                "spans": spans,
                "raw_data": trace_detail
            })
        except Exception as e:
            updated_traces.append({
                "trace_id": trace_id,
                "status": "error",
                "error": str(e),
                "spans": []
            })
            
    connector.close()
    
    success_traces = [t for t in updated_traces if t.get("status") == "success"]
    err_traces = [t for t in updated_traces if t.get("status") == "error"]
    
    step_summary = (
        f"Analyzed traces: queried Jaeger for {len(updated_traces)} trace IDs. "
        f"Success: {len(success_traces)}, Error: {len(err_traces)}."
    )
    reasoning_history.append(step_summary)
    
    return {
        "traces_data": updated_traces,
        "reasoning_history": reasoning_history,
        "current_node": "analyze_traces"
    }

def check_k8s_events(state: IncidentState) -> dict:
    """
    Placeholder stub to query Kubernetes events for the target services.
    Currently returns an empty/dummy list of events.
    """
    reasoning_history = state.get("reasoning_history", [])
    target_services = state.get("target_services", [])
    
    # Placeholder: empty list as per specifications
    k8s_events = []
    
    step_summary = f"Checked Kubernetes events for services: {', '.join(target_services)} (Stubbed as empty)."
    reasoning_history.append(step_summary)
    
    return {
        "k8s_events": k8s_events,
        "reasoning_history": reasoning_history,
        "current_node": "check_k8s_events"
    }

def correlate_deployments(state: IncidentState) -> dict:
    """
    Placeholder stub to correlate target services with recent deployments.
    Returns a mock deployment change history.
    """
    reasoning_history = state.get("reasoning_history", [])
    target_services = state.get("target_services", [])
    
    # Mock deployment change history
    mock_deployments = []
    for service in target_services:
        mock_deployments.append({
            "service": service,
            "deployment_id": f"dep-{service}-12345",
            "timestamp": "2026-07-11T17:30:00Z",
            "commit_sha": "a93b21c4df8e",
            "author": "dev-ops-team",
            "change_summary": f"Mock deployment for {service}: updated base image and bumped CPU limits."
        })
        
    step_summary = f"Correlated deployments for services: {', '.join(target_services)}. Found {len(mock_deployments)} mock deployments."
    reasoning_history.append(step_summary)
    
    return {
        "deployment_events": mock_deployments,
        "reasoning_history": reasoning_history,
        "current_node": "correlate_deployments"
    }

