import httpx
from typing import Dict, Any
from app.config import settings
from app.connectors.base import BaseTelemetryConnector

class JaegerConnector(BaseTelemetryConnector):
    """
    Connects to Jaeger to fetch trace details.
    """
    def __init__(self):
        super().__init__(settings.JAEGER_URL)
        self.client = httpx.Client(base_url=self.base_url)

    def get_trace(self, trace_id: str) -> Dict[str, Any]:
        response = self.client.get(f"/api/traces/{trace_id}")
        if response.status_code == 404:
            return {}
        response.raise_for_status()
        return response.json()
        
    def close(self):
        self.client.close()
