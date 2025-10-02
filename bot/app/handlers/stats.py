from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.core.database import Database
from app.keyboards import get_back_keyboard

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message, db: Database):
    """Команда /stats"""
    await db.update_stats(message.from_user.id, "command")
    await send_stats(message.from_user.id, message.answer, db)


@router.callback_query(F.data == "stats")
async def callback_stats(callback: CallbackQuery, db: Database):
    """Показать статистику через кнопку"""
    await send_stats(callback.from_user.id, callback.message.edit_text, db)
    await callback.answer()


async def send_stats(user_id: int, send_method, db: Database):
    """Отправка статистики пользователю"""
    stats = await db.get_user_stats(user_id)

    if stats:
        stats_text = f"""
📊 <b>Твоя статистика:</b>

💬 Сообщений отправлено: {stats['messages_sent']}
⚡ Команд использовано: {stats['commands_used']}
🕐 Последняя активность: {stats['last_activity'][:16]}

Продолжай в том же духе! 🚀
"""
    else:
        stats_text = "📊 Статистика пока недоступна"

    await send_method(
        stats_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )