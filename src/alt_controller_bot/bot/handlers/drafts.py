from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import List

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from alt_controller_bot.db.database import session_scope
from alt_controller_bot.services.repositories import PostRepository

router = Router()


class DraftStates(StatesGroup):
    pick_channels = State()
    content = State()
    buttons = State()
    reactions = State()
    preview = State()


@dataclass(slots=True)
class DraftContext:
    channel_ids: List[int] = field(default_factory=list)
    text: str | None = None
    media_json: dict | None = None
    buttons_json: list[dict] = field(default_factory=list)
    reactions: List[str] = field(default_factory=lambda: ["👍", "👎", "🔥", "🎯", "😂"])
    post_id: int | None = None


def draft_controls(post_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Опубликовать", callback_data=f"draft:{post_id}:publish"),
                InlineKeyboardButton(text="Запланировать", callback_data=f"draft:{post_id}:schedule"),
            ],
            [
                InlineKeyboardButton(text="В очередь", callback_data=f"draft:{post_id}:queue"),
                InlineKeyboardButton(text="Редактировать", callback_data=f"draft:{post_id}:back"),
            ],
        ]
    )


@router.message(Command("new"))
async def cmd_new(message: Message, state: FSMContext) -> None:
    context = DraftContext()
    await state.set_state(DraftStates.pick_channels)
    await state.update_data(**asdict(context))
    await message.answer("Выберите канал для публикации (функционал в разработке).")


@router.message(DraftStates.content)
async def on_content(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    context = DraftContext(**data)
    context.text = message.html_text
    await state.update_data(**asdict(context))
    await state.set_state(DraftStates.buttons)
    await message.answer("Добавьте кнопки (пока заглушка).")


@router.callback_query(F.data.startswith("draft:"))
async def on_draft_action(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer("Функционал мастера постов ещё не завершён.", show_alert=True)


async def persist_draft(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    context = DraftContext(**data)
    if context.post_id:
        return
    async with session_scope() as session:
        repo = PostRepository(session)
        post = await repo.create_post(
            author_user_id=message.from_user.id,
            channels=context.channel_ids,
            text=context.text,
            media_json=context.media_json,
            buttons_json={"buttons": context.buttons_json},
            reactions_json=context.reactions,
        )
    context.post_id = post.id
    await state.update_data(**asdict(context))
