from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import AnyHttpUrl, BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChannelDefaults(BaseModel):
    timezone: str = Field(default="Asia/Tashkent", alias="tz")
    post_interval_minutes: int = Field(default=60, alias="post_interval_min")
    default_reactions: List[str] = Field(
        default_factory=lambda: ["👍", "👎", "🔥", "🎯", "😂"], alias="default_reactions"
    )
    footer: str | None = None


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    bot_token: str = Field(validation_alias="BOT_TOKEN")
    database_url: AnyHttpUrl | str = Field(validation_alias="DATABASE_URL")
    redis_url: AnyHttpUrl | str = Field(validation_alias="REDIS_URL")
    webhook_url: AnyHttpUrl | None = Field(default=None, validation_alias="WEBHOOK_URL")
    owner_ids: List[int] = Field(default_factory=list, validation_alias="OWNER_IDS")

    channel_defaults: ChannelDefaults = Field(default_factory=ChannelDefaults)

    @field_validator("owner_ids", mode="before")
    @classmethod
    def _split_owner_ids(cls, value: List[int] | str | None) -> List[int] | None:
        if isinstance(value, str):
            return [int(item.strip()) for item in value.split(",") if item.strip()]
        return value


@lru_cache
def load_settings() -> Settings:
    return Settings()


settings = load_settings()
