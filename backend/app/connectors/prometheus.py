from prometheus_api_client import PrometheusConnect
from app.config import settings

class PrometheusConnector:
    """
    Connects to Prometheus using the official prometheus-api-client.
    """
    def __init__(self):
        self.prom = PrometheusConnect(url=settings.PROMETHEUS_URL, disable_ssl=True)
        
    def query(self, query: str):
        return self.prom.custom_query(query=query)
        
    def query_range(self, query: str, start_time, end_time, step: str = "1m"):
        return self.prom.custom_query_range(
            query=query,
            start_time=start_time,
            end_time=end_time,
            step=step
        )
