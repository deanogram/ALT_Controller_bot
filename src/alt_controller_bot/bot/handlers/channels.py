from __future__ import annotations

from dataclasses import asdict, dataclass

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from alt_controller_bot.db.database import session_scope
from alt_controller_bot.services.repositories import ChannelRepository

router = Router()


@dataclass(slots=True)
class AddChannelContext:
    username_or_id: str | None = None
    forwarded_from_chat_id: int | None = None


class ChannelStates(StatesGroup):
    add_input = State()


def channels_keyboard(channels: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="➕ Добавить канал", callback_data="ch:add")]
    ]
    for channel_id, title in channels:
        rows.append(
            [InlineKeyboardButton(text=title, callback_data=f"ch:open:{channel_id}")]
        )
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("channels"))
async def cmd_channels(message: Message, state: FSMContext) -> None:
    async with session_scope() as session:
        repo = ChannelRepository(session)
        channels = await repo.get_user_channels(message.from_user.id)
    kb = channels_keyboard([(ch.id, ch.title) for ch in channels])
    await message.answer("Мои каналы:", reply_markup=kb)
    await state.clear()


@router.callback_query(F.data == "ch:add")
async def on_add_channel(query: CallbackQuery, state: FSMContext) -> None:
    instructions = (
        "1) Сделайте меня админом канала с правом публикации.\n"
        "2) Пришлите @username канала или перешлите сообщение из канала.\n"
        "3) Нажмите «Проверить доступ»."
    )
    await state.set_state(ChannelStates.add_input)
    await query.message.edit_text(
        instructions,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Проверить доступ", callback_data="ch:verify")],
                [InlineKeyboardButton(text="Отмена", callback_data="ch:cancel")],
            ]
        ),
    )
    await query.answer()


@router.message(ChannelStates.add_input)
async def on_channel_identifier(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    context = AddChannelContext(**data) if data else AddChannelContext()

    if message.forward_from_chat:
        context.forwarded_from_chat_id = message.forward_from_chat.id
    else:
        context.username_or_id = message.text.strip()

    await state.update_data(**asdict(context))
    await message.answer("Отлично! Нажмите «Проверить доступ», когда будете готовы.")


@router.callback_query(F.data == "ch:cancel")
async def on_cancel(query: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await query.message.edit_text("Добавление канала отменено.")
    await query.answer()


@router.callback_query(F.data == "ch:verify")
async def on_verify(query: CallbackQuery, state: FSMContext) -> None:
    await query.answer("Пока реализован только каркас проверки.", show_alert=True)
