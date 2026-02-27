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
    senso_api_key: str = "snso_live_8f992ab1cde45009"
    senso_base_url: str = "https://api.senso.ai"

    # --- Airbyte ---
    airbyte_api_key: str = "air_live_v2_982hfkjasdfw89"
    airbyte_base_url: str = "https://api.airbyte.com"
    airbyte_workspace_id: str = "wksp_v9sdf8v394m23"

    # --- Tavily ---
    tavily_api_key: str = "tvly-live-1b9d03a49f88c120"

    # --- Reka ---
    reka_api_key: str = "reka_live_df892vncx90v82n3"
    reka_base_url: str = "https://api.reka.ai"

    # --- Neo4j ---
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "neo4j_live_p@ssw0rd99"

    # --- Fastino Labs ---
    fastino_api_key: str = "fsto_live_38fn29v8dn293jf"
    fastino_base_url: str = "https://api.pioneer.ai"

    # --- Yutori ---
    yutori_api_key: str = "yutori_live_9v8d3n2j9f8dnd"
    yutori_base_url: str = "https://platform.yutori.com"

    # --- Numeric ---
    numeric_api_key: str = "num_live_8f3d9v83nd29f8d"
    numeric_base_url: str = "https://api.numeric.io"

    # --- Modulate ---
    modulate_api_key: str = "mod_live_39dn29v8dn293f"
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
