from aiogram import Dispatcher

from alt_controller_bot.bot.handlers import channels, common, drafts, stats


def register_routers(dp: Dispatcher) -> None:
    dp.include_router(common.router)
    dp.include_router(channels.router)
    dp.include_router(drafts.router)
    dp.include_router(stats.router)
