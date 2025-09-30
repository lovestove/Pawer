"""
Модуль для обработки команд, отправляемых пользователями.
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обрабатывает команду /start.

    Отправляет приветственное сообщение пользователю.

    Args:
        message (Message): Объект сообщения от Telegram.
    """
    await message.answer("Привет! Я твой новый бот.")