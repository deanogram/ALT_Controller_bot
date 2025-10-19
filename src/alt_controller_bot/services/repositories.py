from __future__ import annotations

from datetime import datetime
from typing import Iterable, Sequence

from sqlalchemy import Select, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from alt_controller_bot.db import models


class ChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_channels(self, user_id: int) -> Sequence[models.Channel]:
        stmt = (
            select(models.Channel)
            .join(models.UserChannel)
            .where(models.UserChannel.user_id == user_id)
            .order_by(models.Channel.title)
        )
        result = await self.session.scalars(stmt)
        return result.all()

    async def upsert_channel(
        self,
        tg_chat_id: int,
        title: str,
        username: str | None,
        defaults: dict | None = None,
    ) -> models.Channel:
        defaults = defaults or {}
        stmt = select(models.Channel).where(models.Channel.tg_chat_id == tg_chat_id)
        channel = await self.session.scalar(stmt)
        if channel:
            channel.title = title
            channel.username = username
            if defaults:
                channel.settings_json = {**channel.settings_json, **defaults}
            return channel

        channel = models.Channel(
            tg_chat_id=tg_chat_id,
            title=title,
            username=username,
            settings_json=defaults or {},
        )
        self.session.add(channel)
        await self.session.flush()
        return channel

    async def link_user(
        self,
        user_id: int,
        channel: models.Channel,
        role: str,
    ) -> models.UserChannel:
        stmt = select(models.UserChannel).where(
            models.UserChannel.user_id == user_id,
            models.UserChannel.channel_id == channel.id,
        )
        existing = await self.session.scalar(stmt)
        if existing:
            existing.role = role
            return existing

        link = models.UserChannel(user_id=user_id, channel_id=channel.id, role=role)
        self.session.add(link)
        await self.session.flush()
        return link


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_post(
        self,
        *,
        author_user_id: int,
        channels: Iterable[int],
        text: str | None = None,
        parse_mode: str = "HTML",
        media_json: dict | None = None,
        buttons_json: dict | None = None,
        reactions_json: dict | None = None,
        status: str = "draft",
        scheduled_at: datetime | None = None,
    ) -> models.Post:
        post = models.Post(
            author_user_id=author_user_id,
            channels=list(channels),
            text=text,
            parse_mode=parse_mode,
            media_json=media_json,
            buttons_json=buttons_json,
            reactions_json=reactions_json,
            status=status,
            scheduled_at=scheduled_at,
        )
        self.session.add(post)
        await self.session.flush()
        return post

    async def update_post(self, post_id: int, **kwargs) -> models.Post:
        stmt = select(models.Post).where(models.Post.id == post_id)
        post = await self.session.scalar(stmt)
        if not post:
            raise NoResultFound(f"Post {post_id} not found")

        for key, value in kwargs.items():
            setattr(post, key, value)
        post.updated_at = datetime.utcnow()
        await self.session.flush()
        return post

    async def list_user_posts(self, user_id: int, status: str | None = None) -> Sequence[models.Post]:
        stmt: Select[models.Post] = select(models.Post).where(models.Post.author_user_id == user_id)
        if status:
            stmt = stmt.where(models.Post.status == status)
        stmt = stmt.order_by(models.Post.created_at.desc())
        result = await self.session.scalars(stmt)
        return result.all()


class StatsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def increment_click(self, post_id: int, channel_id: int, button_key: str, value: int = 1) -> None:
        stmt = select(models.StatsClick).where(
            models.StatsClick.post_id == post_id,
            models.StatsClick.channel_id == channel_id,
            models.StatsClick.button_key == button_key,
        )
        record = await self.session.scalar(stmt)
        if record:
            record.clicks += value
            record.updated_at = datetime.utcnow()
        else:
            record = models.StatsClick(
                post_id=post_id,
                channel_id=channel_id,
                button_key=button_key,
                clicks=value,
            )
            self.session.add(record)
        await self.session.flush()

    async def increment_reaction(self, post_id: int, channel_id: int, emoji: str, value: int = 1) -> None:
        stmt = select(models.StatsReaction).where(
            models.StatsReaction.post_id == post_id,
            models.StatsReaction.channel_id == channel_id,
            models.StatsReaction.emoji == emoji,
        )
        record = await self.session.scalar(stmt)
        if record:
            record.count += value
            record.updated_at = datetime.utcnow()
        else:
            record = models.StatsReaction(
                post_id=post_id,
                channel_id=channel_id,
                emoji=emoji,
                count=value,
            )
            self.session.add(record)
        await self.session.flush()


class AuditRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        *,
        user_id: int | None,
        action: str,
        target_type: str | None = None,
        target_id: int | None = None,
        extra_json: dict | None = None,
    ) -> models.AuditEntry:
        entry = models.AuditEntry(
            user_id=user_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            extra_json=extra_json,
        )
        self.session.add(entry)
        await self.session.flush()
        return entry
