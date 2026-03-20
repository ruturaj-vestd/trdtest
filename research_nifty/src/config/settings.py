from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Nifty Research Stack"
    environment: str = "local"
    data_dir: Path = Path("data")
    output_dir: Path = Path("outputs")
    db_path: Path = Path("data/research.duckdb")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5.4", alias="OPENAI_MODEL")
    use_ollama_fallback: bool = Field(default=True, alias="USE_OLLAMA_FALLBACK")
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen3:30b", alias="OLLAMA_MODEL")

    max_daily_llm_budget_usd: float = Field(default=10.0, alias="MAX_DAILY_LLM_BUDGET_USD")
    llm_cache_ttl_sec: int = 60 * 60 * 12

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    digest_to_email: str | None = None

    allow_auto_patch: bool = Field(default=False, alias="ALLOW_AUTO_PATCH")
    policy_path: Path = Path("data/policy/current_policy.json")
    candidate_policy_path: Path = Path("data/policy/candidate_policy.json")

    scheduler_timezone: str = "Asia/Kolkata"
    monitor_interval_minutes: int = 15


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    settings.policy_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
