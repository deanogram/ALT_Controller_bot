import asyncio
from contextlib import suppress

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from redis.asyncio import Redis

from alt_controller_bot.bot.routers import register_routers
from alt_controller_bot.core.config import settings


async def create_bot() -> Bot:
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


async def create_dispatcher() -> Dispatcher:
    redis = Redis.from_url(str(settings.redis_url))
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)
    register_routers(dp)
    return dp


async def main() -> None:
    bot = await create_bot()
    dp = await create_dispatcher()

    if settings.webhook_url:
        await bot.set_webhook(settings.webhook_url)
        await dp.start_polling(bot)
        return

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(main())
