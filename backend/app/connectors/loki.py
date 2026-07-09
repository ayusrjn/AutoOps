import httpx
from typing import Dict, Any
from app.config import settings
from app.connectors.base import BaseTelemetryConnector

class LokiConnector(BaseTelemetryConnector):
    """
    Connects to Grafana Loki to query logs.
    """
    def __init__(self):
        super().__init__(settings.LOKI_URL)
        self.client = httpx.Client(base_url=self.base_url)

    def query_range(self, query: str, limit: int = 100) -> Dict[str, Any]:
        params = {
            "query": query,
            "limit": limit
        }
        response = self.client.get("/loki/api/v1/query_range", params=params)
        response.raise_for_status()
        return response.json()
        
    def close(self):
        self.client.close()
