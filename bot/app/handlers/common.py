from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.core.database import Database
from app.keyboards import get_main_keyboard, get_back_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, db: Database):
    """Команда /start"""
    await db.update_stats(message.from_user.id, "command")

    welcome_text = f"""
🎉 <b>Привет, {message.from_user.first_name}!</b>

Добро пожаловать в бота! Вот что я умею:

📊 Статистика - смотри свою активность
⚙️ Настройки - персонализируй бота
💬 Обратная связь - свяжись с нами
ℹ️ Помощь - список всех команд

Выбери действие ниже:
"""

    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message, db: Database):
    """Команда /help"""
    await db.update_stats(message.from_user.id, "command")

    help_text = """
📚 <b>Список команд:</b>

/start - Главное меню
/help - Справка по командам
/stats - Твоя статистика
/settings - Настройки
/feedback - Обратная связь

💡 <b>Совет:</b> Используй кнопки для удобной навигации!
"""

    await message.answer(
        help_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    """Показать помощь"""
    help_text = """
📚 <b>Список команд:</b>

/start - Главное меню
/help - Справка по командам
/stats - Твоя статистика
/settings - Настройки
/feedback - Обратная связь

💡 <b>Совет:</b> Используй кнопки для удобной навигации!
"""

    await callback.message.edit_text(
        help_text,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_main")
async def callback_back(callback: CallbackQuery):
    """Вернуться в главное меню"""
    welcome_text = f"""
🎉 <b>Главное меню</b>

Выбери действие:
"""

    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()