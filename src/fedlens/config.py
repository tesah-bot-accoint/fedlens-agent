from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    anthropic_api_key: str | None = None
    fedlens_model: str = "claude-sonnet-5-5"
    fedlens_max_tool_iterations: int = 8

    fedlens_db_path: Path = REPO_ROOT / "data" / "fedlens.duckdb"
    fedlens_scope_file: Path = REPO_ROOT / "config" / "scope.yaml"

    usaspending_base_url: str = "https://api.usaspending.gov"
    usaspending_timeout_s: float = 60.0
    usaspending_max_retries: int = 5
    usaspending_requests_per_second: float = 2.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
