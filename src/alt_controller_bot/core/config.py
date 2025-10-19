from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, BaseModel, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChannelDefaults(BaseModel):
    timezone: str = Field(default="Asia/Tashkent", alias="tz")
    post_interval_minutes: int = Field(default=60, alias="post_interval_min")
    default_reactions: List[str] = Field(
        default_factory=lambda: ["👍", "👎", "🔥", "🎯", "😂"], alias="default_reactions"
    )
    footer: str | None = None


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"
EXAMPLE_ENV_PATH = PROJECT_ROOT / ".env.example"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(DEFAULT_ENV_PATH, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    bot_token: str = Field(validation_alias="BOT_TOKEN")
    database_url: AnyHttpUrl | str = Field(validation_alias="DATABASE_URL")
    redis_url: AnyHttpUrl | str = Field(validation_alias="REDIS_URL")
    webhook_url: AnyHttpUrl | None = Field(default=None, validation_alias="WEBHOOK_URL")
    owner_ids: List[int] = Field(default_factory=list, validation_alias="OWNER_IDS")

    channel_defaults: ChannelDefaults = Field(default_factory=ChannelDefaults)

    @field_validator("webhook_url", mode="before")
    @classmethod
    def _empty_string_to_none(cls, value: str | AnyHttpUrl | None) -> AnyHttpUrl | None:
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @field_validator("owner_ids", mode="before")
    @classmethod
    def _split_owner_ids(
        cls, value: List[int] | str | int | None
    ) -> List[int] | None:
        if isinstance(value, str):
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        if isinstance(value, int):
            return [value]
        return value


@lru_cache
def load_settings() -> Settings:
    try:
        env_files: list[Path | str] = []

        if DEFAULT_ENV_PATH.exists():
            env_files.append(DEFAULT_ENV_PATH)
        if EXAMPLE_ENV_PATH.exists():
            env_files.append(EXAMPLE_ENV_PATH)

        if env_files:
            return Settings(_env_file=tuple(env_files))

        return Settings()
    except ValidationError as exc:
        missing_fields = [
            " -> ".join(str(part) for part in error.get("loc", ()))
            for error in exc.errors()
            if error.get("type") == "missing"
        ]
        missing_message = (
            f"Missing required settings: {', '.join(missing_fields)}. "
            if missing_fields
            else "Missing required settings. "
        )
        raise RuntimeError(
            missing_message
            + "Set the corresponding environment variables or create a '.env' file "
            f"at {PROJECT_ROOT / '.env'} based on '.env.example'."
        ) from exc


settings = load_settings()
