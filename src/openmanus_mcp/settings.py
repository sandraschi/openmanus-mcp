"""Runtime settings (env + defaults)."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """OpenManus MCP server settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openmanus_root: Path | None = Field(
        default=None,
        description="Path to a clone of FoundationAgents/OpenManus (env OPENMANUS_ROOT)",
    )
    openmanus_fleet_root: Path | None = Field(
        default=None,
        description="Fleet clone dir. Env OPENMANUS_FLEET_ROOT, else ./fleet or ./openmanus-fleet.",
    )
    api_host: str = Field(default="127.0.0.1", description="env OPENMANUS_MCP_API_HOST")
    api_port: int = Field(default=10768, description="env OPENMANUS_MCP_API_PORT")


def get_settings() -> Settings:
    return Settings()
