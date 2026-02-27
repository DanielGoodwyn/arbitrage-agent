"""
Centralized configuration loaded from environment variables.
Uses Pydantic BaseSettings for validation and .env file support.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """All service credentials and agent configuration."""

    # --- Robinhood ---
    robinhood_username: str = ""
    robinhood_password: str = ""
    robinhood_mfa_code: Optional[str] = None
    robinhood_device_token: Optional[str] = None

    # --- Senso (Context OS) ---
    senso_api_key: str = ""
    senso_base_url: str = "https://api.senso.ai"

    # --- Airbyte ---
    airbyte_api_key: str = ""
    airbyte_base_url: str = "https://api.airbyte.com"
    airbyte_workspace_id: str = ""

    # --- Tavily ---
    tavily_api_key: str = ""

    # --- Reka ---
    reka_api_key: str = ""
    reka_base_url: str = "https://api.reka.ai"

    # --- Neo4j ---
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = ""

    # --- Fastino Labs ---
    fastino_api_key: str = ""
    fastino_base_url: str = "https://api.pioneer.ai"

    # --- Yutori ---
    yutori_api_key: str = ""
    yutori_base_url: str = "https://platform.yutori.com"

    # --- Numeric ---
    numeric_api_key: str = ""
    numeric_base_url: str = "https://api.numeric.io"

    # --- Modulate ---
    modulate_api_key: str = ""
    modulate_base_url: str = "https://modulate-developer-apis.com"

    # --- Deployment ---
    render_api_key: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_region: str = "us-west-2"

    # --- Agent Behavior ---
    agent_cycle_interval_seconds: int = 30
    arbitrage_score_threshold: float = 0.75
    anomaly_alert_threshold: float = 0.95
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
