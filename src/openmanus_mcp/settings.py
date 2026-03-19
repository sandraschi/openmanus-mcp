"""Runtime settings (env + defaults)."""

from pathlib import Path

from pydantic import AliasChoices, Field
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
    runner_timeout_s: float = Field(
        default=300.0,
        description=(
            "Hard timeout (seconds) for a single OpenManus subprocess run. "
            "Env OPENMANUS_RUNNER_TIMEOUT_S."
        ),
    )
    job_store_max_completed: int = Field(
        default=100,
        ge=1,
        le=10_000,
        description=(
            "Max completed async jobs kept in memory (FIFO eviction). "
            "Env OPENMANUS_JOB_STORE_MAX_COMPLETED."
        ),
    )
    ollama_base_url: str = Field(
        default="http://127.0.0.1:11434",
        description="Ollama base URL (OPENMANUS_OLLAMA_BASE_URL or OLLAMA_BASE_URL).",
        validation_alias=AliasChoices("OPENMANUS_OLLAMA_BASE_URL", "OLLAMA_BASE_URL"),
    )
    lmstudio_base_url: str = Field(
        default="http://127.0.0.1:1234",
        description="LM Studio server URL (OPENMANUS_LMSTUDIO_BASE_URL or LMSTUDIO_BASE_URL).",
        validation_alias=AliasChoices("OPENMANUS_LMSTUDIO_BASE_URL", "LMSTUDIO_BASE_URL"),
    )
    supervisor_enabled: bool = Field(
        default=False,
        description=(
            "Background supervisor tick + schedules. "
            "Env OPENMANUS_SUPERVISOR_ENABLED (true/false)."
        ),
        validation_alias=AliasChoices("OPENMANUS_SUPERVISOR_ENABLED", "SUPERVISOR_ENABLED"),
    )
    supervisor_tick_s: float = Field(
        default=30.0,
        ge=5.0,
        le=3600.0,
        description="Seconds between supervisor ticks. Env OPENMANUS_SUPERVISOR_TICK_S.",
        validation_alias=AliasChoices("OPENMANUS_SUPERVISOR_TICK_S", "SUPERVISOR_TICK_S"),
    )
    skills_extra_dirs: str = Field(
        default="",
        description=(
            "Extra SKILL.md scan roots (semicolon-separated). Prepend order = higher precedence. "
            "Env OPENMANUS_SKILLS_EXTRA_DIRS."
        ),
        validation_alias=AliasChoices("OPENMANUS_SKILLS_EXTRA_DIRS", "SKILLS_EXTRA_DIRS"),
    )
    max_skill_inject_chars: int = Field(
        default=24_000,
        ge=1024,
        le=200_000,
        description="Max characters when inlining a SKILL.md into chat. Env OPENMANUS_MAX_SKILL_INJECT_CHARS.",
        validation_alias=AliasChoices("OPENMANUS_MAX_SKILL_INJECT_CHARS", "MAX_SKILL_INJECT_CHARS"),
    )


def get_settings() -> Settings:
    return Settings()
