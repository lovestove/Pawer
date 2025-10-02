from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo

from app.core import settings

router = Router()


@router.message(Command("app"))
async def command_app(message: Message):
    """
    Handler for the /app command, which sends a button to launch the Mini App.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть Тамагочи",
                    web_app=WebAppInfo(url=settings.MINI_APP_URL),
                )
            ]
        ]
    )
    await message.answer(
        "Нажмите на кнопку ниже, чтобы открыть приложение с вашим питомцем!",
        reply_markup=keyboard,
    )