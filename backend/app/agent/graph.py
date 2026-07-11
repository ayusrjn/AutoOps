from langgraph.graph import StateGraph, END
from app.agent.state import IncidentState
from app.agent.nodes import (
    fetch_alert_details,
    analyze_metrics,
    check_logs,
    analyze_traces,
    check_k8s_events,
    correlate_deployments,
    synthesize_root_cause,
    generate_recommendations
)

# Initialize the StateGraph
workflow = StateGraph(IncidentState)

# Add all nodes
workflow.add_node("fetch_alert_details", fetch_alert_details)
workflow.add_node("analyze_metrics", analyze_metrics)
workflow.add_node("check_logs", check_logs)
workflow.add_node("analyze_traces", analyze_traces)
workflow.add_node("check_k8s_events", check_k8s_events)
workflow.add_node("correlate_deployments", correlate_deployments)
workflow.add_node("synthesize_root_cause", synthesize_root_cause)
workflow.add_node("generate_recommendations", generate_recommendations)

# Set entry point
workflow.set_entry_point("fetch_alert_details")

# Define edges
workflow.add_edge("fetch_alert_details", "analyze_metrics")
workflow.add_edge("analyze_metrics", "check_logs")

# Routing condition after check_logs: only run trace analysis if trace_ids are found
def route_after_logs(state: IncidentState) -> str:
    # If traces_data is populated with at least one trace_id, run analyze_traces
    if state.get("traces_data") and len(state.get("traces_data")) > 0:
        return "analyze_traces"
    return "check_k8s_events"

workflow.add_conditional_edges(
    "check_logs",
    route_after_logs,
    {
        "analyze_traces": "analyze_traces",
        "check_k8s_events": "check_k8s_events"
    }
)

workflow.add_edge("analyze_traces", "check_k8s_events")
workflow.add_edge("check_k8s_events", "correlate_deployments")
workflow.add_edge("correlate_deployments", "synthesize_root_cause")
workflow.add_edge("synthesize_root_cause", "generate_recommendations")
workflow.add_edge("generate_recommendations", END)

# Compile the graph
app_graph = workflow.compile()
