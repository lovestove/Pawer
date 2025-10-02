from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.core.database import Database
from app.keyboards import get_settings_keyboard

router = Router()


@router.message(Command("settings"))
async def cmd_settings(message: Message, db: Database):
    """Команда /settings"""
    await db.update_stats(message.from_user.id, "command")

    settings_text = """
⚙️ <b>Настройки бота</b>

Здесь ты можешь настроить бота под себя.
Выбери параметр:
"""

    await message.answer(
        settings_text,
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "settings")
async def callback_settings(callback: CallbackQuery):
    """Открыть настройки"""
    settings_text = """
⚙️ <b>Настройки бота</b>

Здесь ты можешь настроить бота под себя.
Выбери параметр:
"""

    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "toggle_notifications")
async def callback_toggle_notifications(callback: CallbackQuery):
    """Переключение уведомлений"""
    await callback.answer("🔔 Уведомления обновлены!", show_alert=True)


@router.callback_query(F.data == "change_language")
async def callback_change_language(callback: CallbackQuery):
    """Смена языка"""
    await callback.answer("🌍 Выбор языка (в разработке)", show_alert=True)