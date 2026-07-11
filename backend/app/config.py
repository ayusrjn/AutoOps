import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./autoops.db"
    
    # Telemetry Endpoints
    PROMETHEUS_URL: str = "http://localhost:9090"
    LOKI_URL: str = "http://localhost:3100"
    JAEGER_URL: str = "http://localhost:16686"
    
    # LLM Settings
    LITELLM_MODEL: str = "gemini/gemini-2.5-flash"
    GEMINI_API_KEY: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

# Export config to environment variables for LiteLLM
if settings.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY

