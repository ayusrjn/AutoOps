from abc import ABC

class BaseTelemetryConnector(ABC):
    """
    Base interface for all telemetry connectors (Metrics, Logs, Traces).
    """
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
