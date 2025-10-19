from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str | None]
    title: Mapped[str]
    tz: Mapped[str] = mapped_column(String(64), default="Asia/Tashkent")
    post_interval_min: Mapped[int] = mapped_column(Integer, default=60)
    settings_json: Mapped[dict] = mapped_column(JSONB, default=dict)

    members: Mapped[list[UserChannel]] = relationship(back_populates="channel")


class UserChannel(Base):
    __tablename__ = "user_channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)

    channel: Mapped[Channel] = relationship(back_populates="members")

    __table_args__ = (
        CheckConstraint("role IN ('owner','admin','editor','analyst')", name="user_channels_role_chk"),
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    author_user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    channels: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    text: Mapped[str | None]
    parse_mode: Mapped[str] = mapped_column(String(16), default="HTML")
    media_json: Mapped[dict | None] = mapped_column(JSONB)
    buttons_json: Mapped[dict | None] = mapped_column(JSONB)
    reactions_json: Mapped[dict | None] = mapped_column(JSONB)
    preview_message_id: Mapped[int | None] = mapped_column(BigInteger)

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','scheduled','queued','published','deleted')",
            name="posts_status_chk",
        ),
        CheckConstraint(
            "parse_mode IN ('HTML','Markdown','None')",
            name="posts_parse_mode_chk",
        ),
    )


class StatsClick(Base):
    __tablename__ = "stats_clicks"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    button_key: Mapped[str] = mapped_column(String(64), nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class StatsReaction(Base):
    __tablename__ = "stats_reactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))
    emoji: Mapped[str] = mapped_column(String(32), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)


class AuditEntry(Base):
    __tablename__ = "audit"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(32))
    target_id: Mapped[int | None] = mapped_column(BigInteger)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    extra_json: Mapped[dict | None] = mapped_column(JSONB)
