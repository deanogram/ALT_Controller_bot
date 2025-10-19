from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


router = Router()


MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Мои каналы"), KeyboardButton(text="Новый пост")],
        [KeyboardButton(text="Очередь"), KeyboardButton(text="Статистика")],
        [KeyboardButton(text="Настройки")],
    ],
    resize_keyboard=True,
)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    greeting = (
        "Я — бот для ведения каналов: посты, кнопки, реакции, отложки. "
        "Готовы приступить?"
    )
    await message.answer(greeting, reply_markup=MAIN_MENU)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    text = (
        "Доступные команды:\n"
        "/channels — управление каналами\n"
        "/new — мастер нового поста\n"
        "/queue — очередь публикаций\n"
        "/stats — статистика каналов\n"
        "/settings — настройки профиля"
    )
    await message.answer(text)
