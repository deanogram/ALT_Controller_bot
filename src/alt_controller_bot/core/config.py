from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChannelDefaults(BaseModel):
    timezone: str = Field(default="Asia/Tashkent", alias="tz")
    post_interval_minutes: int = Field(default=60, alias="post_interval_min")
    default_reactions: List[str] = Field(
        default_factory=lambda: ["👍", "👎", "🔥", "🎯", "😂"], alias="default_reactions"
    )
    footer: str | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    bot_token: str = Field(validation_alias="BOT_TOKEN")
    database_url: AnyHttpUrl | str = Field(validation_alias="DATABASE_URL")
    redis_url: AnyHttpUrl | str = Field(validation_alias="REDIS_URL")
    webhook_url: AnyHttpUrl | None = Field(default=None, validation_alias="WEBHOOK_URL")
    owner_ids: List[int] = Field(default_factory=list, validation_alias="OWNER_IDS")

    channel_defaults: ChannelDefaults = Field(default_factory=ChannelDefaults)


@lru_cache
def load_settings() -> Settings:
    return Settings()


settings = load_settings()
